#!/bin/env python
# -*- coding: utf-8 -*-
import logging
import os
import time

from datetime import datetime
import sqlalchemy as sa
import tornado.ioloop
import tornado.web
from tornado.web import url

from models import User, Content
from settings import maker


class BaseHandler(tornado.web.RequestHandler):
    cookie_id = ""

    def get_current_user(self): #selfではなくcls
        user_id = self.get_secure_cookie(self.cookie_id)
        user_id = str(user_id)
        if not user_id:
            return None
        return tornado.escape.utf8(user_id)

    # nameを引数にidを取得
    def get_user_id(self, name):
        db_session = maker()
        user_query = db_session.query(User).filter(
            User.name == name).first()  #idを保存したほうがuniqueなのでよい
        db_session.close()
        if not user_query:
            return None
        return user_query.id

    # idを引数にUserクエリを取得
    def get_a_user_query_from_db(self, user_id):
        db_session = maker()
        user_query = db_session.query(User).filter(
            User.id == user_id).first()
        db_session.close()
        return user_query

    # 2つのidを引数にContentクエリを取得
    def get_content_query_from_db(self, my_id, partner_id):
        db_session = maker()
        my_contents_query = db_session.query(Content).filter(
            Content.from_id == my_id, Content.to_id == partner_id).all()
        db_session.close()
        return my_contents_query

    def set_current_user(self, user_id):
        self.set_secure_cookie(str(self.cookie_id),
                               tornado.escape.utf8(str(user_id))) #usernameは値ではなくキー

    def clear_current_user(self):
        self.clear_cookie(self.cookie_id)


class ChatHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self, partner_id):
        my_id = self.get_current_user()
        my_user_query = self.get_a_user_query_from_db(my_id)    #今はチャット部分のメソッドでOK
        partner_user_query = self.get_a_user_query_from_db(partner_id)
        my_contents_query = self.get_content_query_from_db(my_id, partner_id)
        partner_contents_query = self.get_content_query_from_db(
            partner_id, my_id)
        my_containers = []  # 表示させる自分のテキスト
        partner_containers = []  # 表示させる相手のテキスト
        # リストにテキストを入れないと、クエリのままだと表示できなさそうだったのでリストにする
        for row in my_contents_query:
            my_containers.append(row.content)
        for row in partner_contents_query:
            partner_containers.append(row.content)
        self.render("chat.html", my_containers=my_containers, partner_containers=partner_containers,
                    my_id=my_user_query.id, partner_id=partner_user_query.id, my_name=my_user_query.name, partner_name=partner_user_query.name)

    def post(self, partner_id):
        db_session = maker()
        body = self.get_argument('body')
        my_user_query = self.get_a_user_query_from_db(
            self.current_user())
        time_stamp = time.strftime('%Y-%m-%d %H:%M:%S')
        # データ追加
        new_content = Content(from_id=my_user_query.id,
                              to_id=partner_id, content=body, datetime=time_stamp)
        try:
            db_session.add(new_content)
            db_session.commit()
        except Exception as e:
            db_session.rollback()
            logging.error(datetime.now())
            raise e
        finally:
            db_session.close()
        self.redirect('/chat/{}'.format(partner_id))


class SelectHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        # 自分以外のUserクエリをUserテーブルから選択
        db_session = maker()
        partner_query = db_session.query(User).filter(
            User.id != self.current_user).all()
        self.render("select_partner.html",
                    username=self.current_user, partners=partner_query)

    def post(self):
        partner_id = self.get_argument("partner_id")
        self.redirect('/chat/{}'.format(partner_id))


class CreateUserHandler(BaseHandler):
    def get(self, username):
        self.render("create_user.html", username=username)

    def post(self, username):
        username = self.get_argument("username")
        if username == "":
            self.redirect('/create_user/')
        else:
            db_session = maker()
            new_user = User(name=username)
            try:
                db_session.add(new_user)
                db_session.commit() #ロールバック処理
                self.set_current_user(self.get_user_id(username))
            except Exception as e:
                db_session.rollback()
                logging.error(datetime.now())
            finally:
                db_session.close()

            self.redirect('/select')


class LoginHandler(BaseHandler):
    def get(self):
        self.render("login.html")

    def post(self):
        username = self.get_argument("username")
        user_id = self.get_user_id(username)
        users = self.get_a_user_query_from_db(user_id)
        if users:
            self.set_current_user(user_id)
            self.redirect("/select")
        else:
            self.redirect('/create_user/{}'.format(username))


class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_current_user()
        self.redirect('/login')


class Application(tornado.web.Application):
    def __init__(self):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        handlers = [
            (r'/chat/([0-9]+)', ChatHandler),
            (r'/login', LoginHandler),
            (r'/logout', LogoutHandler),
            (r'/select', SelectHandler),
            (r'/create_user/([a-zA-Z0-9]*)', CreateUserHandler)
        ]
        settings = dict(
            cookie_secret='dJD8PK6SR6CfDhtoG1K1yphPs52CQ09IjlFYdM6b8Ws=',
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
