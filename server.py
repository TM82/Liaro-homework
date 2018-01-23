#!/bin/env python
# -*- coding: utf-8 -*-
import os
import tornado.ioloop
import tornado.web
from tornado.web import url
import sqlalchemy as sa
from settings import maker
from models import User, Content
import time


class BaseHandler(tornado.web.RequestHandler):
    cookie_username = "username"  # 初期値？

    def get_current_user(self):
        username = self.get_secure_cookie(self.cookie_username)
        if not username:
            return None
        return tornado.escape.utf8(username)

    def get_user_id(self, name):
        db_session = maker()
        user_query = db_session.query(User).filter(
            User.name == name).first()
        db_session.close()
        if not user_query:
            return None
        return user_query.id

    def get_a_user_query_from_db(self, user_id):
        db_session = maker()
        user_query = db_session.query(User).filter(
            User.id == user_id).first()
        db_session.close()
        return user_query

    def get_content_query_from_db(self, my_id, partner_id):
        db_session = maker()
        my_contents_query = db_session.query(Content).filter(
            Content.from_id == my_id, Content.to_id == partner_id).all()
        db_session.close()
        return my_contents_query

    def set_current_user(self, username):
        self.set_secure_cookie(self.cookie_username,
                               tornado.escape.utf8(username))

    def clear_current_user(self):
        self.clear_cookie(self.cookie_username)


class IndexHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self, partner_id):
        my_id = self.get_user_id(self.get_current_user())
        my_user_query = self.get_a_user_query_from_db(my_id)
        partner_user_query = self.get_a_user_query_from_db(partner_id)
        my_contents_query = self.get_content_query_from_db(my_id, partner_id)
        partner_contents_query = self.get_content_query_from_db(
            partner_id, my_id)
        my_containers = []
        partner_containers = []
        for row in my_contents_query:
            my_containers.append(row.content)
        for row in partner_contents_query:
            partner_containers.append(row.content)
        self.render("index.html", my_containers=my_containers, partner_containers=partner_containers,
                    my_id=my_user_query.id, partner_id=partner_user_query.id, my_name=my_user_query.name, partner_name=partner_user_query.name)

    def post(self, partner_id):
        db_session = maker()
        body = self.get_argument('body')
        my_user_query = self.get_a_user_query_from_db(
            self.get_user_id(self.get_current_user()))
        time_stamp = time.strftime('%Y-%m-%d %H:%M:%S')
        new_content = Content(from_id=my_user_query.id,
                              to_id=partner_id, content=body, datetime=time_stamp)
        db_session.add(new_content)
        db_session.commit()
        db_session.close()
        self.redirect('/%s' % (partner_id))


class SelectHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        db_session = maker()
        partner_query = db_session.query(User).filter(
            User.name != self.current_user).all()
        self.render("select_player.html",
                    username=self.current_user, partners=partner_query)

    def post(self):
        partner_id = self.get_argument("partner_id")
        partner_query = self.get_a_user_query_from_db(partner_id)
        if partner_query:
            # 1つしかヒットしないのでOK?（同じユーザ名があるとout) > 外部制約で対応
            self.redirect('/%s' % (partner_query.id))
        else:
            self.write("choose existing user\n")
            self.write_error(403)


class CreateUserHandler(BaseHandler):
    def get(self, username):
        self.render("create_user.html", username=username)

    def post(self, username):
        username = self.get_argument("username")
        if username == "":
            print("----------------------------------------------------")
            print("blank is not allowable.")
            self.redirect('/login')
        else:
            db_session = maker()
            new_user = User(name=username)
            db_session.add(new_user)
            db_session.commit()
            db_session.close()
            self.redirect('/login')


class LoginHandler(BaseHandler):
    def get(self):
        self.render("login.html")

    def post(self):
        username = self.get_argument("username")
        users = self.get_a_user_query_from_db(self.get_user_id(username))
        if users:
            self.set_current_user(username)
            self.redirect("/select")
        else:
            self.redirect('/create_user/%s' % (username))
            # self.write('select existing user\n')
            # self.write_error(403)


class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_current_user()
        self.redirect('/login')


class Application(tornado.web.Application):
    def __init__(self):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        handlers = [
            (r'/([0-9]+)', IndexHandler),
            (r'/login', LoginHandler),
            (r'/logout', LogoutHandler),
            (r'/select', SelectHandler),
            (r'/create_user/(.*)', CreateUserHandler)
        ]
        settings = dict(
            cookie_secret='gaofjawpoer940r34823842398429afadfi4iiad',
            static_path=os.path.join(BASE_DIR, "static"),
            template_path=os.path.join(BASE_DIR, "templates"),
            login_url="/login",
            # xsrf_cookies=True,
            # autoescape="xhtml_escape",
            debug=True,
        )

        tornado.web.Application.__init__(self, handlers, **settings)


if __name__ == '__main__':
    app = Application()
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
