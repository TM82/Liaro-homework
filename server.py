#!/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
import os
import tornado.ioloop
import tornado.web
from tornado.web import url
import sqlalchemy as sa
from settings import maker
from models import *

class BaseHandler(tornado.web.RequestHandler):
    cookie_username = "username" #初期値？

    def get_current_user(self):
        username = self.get_secure_cookie(self.cookie_username)
        if not username: return None
        return tornado.escape.utf8(username)

    def set_current_user(self, username):
        self.set_secure_cookie(self.cookie_username, tornado.escape.utf8(username))

    def clear_current_user(self):
        self.clear_cookie(self.cookie_username)



class IndexHandler(BaseHandler):
    @tornado.web.authenticated

    def get(self):
        db_session = maker()
        from_id = 1#前のページから引き継ぎたい
        to_id = 2#前のページから引き継ぎたい
        containers = []
        contents = db_session.query(Content).filter(Content.from_id==from_id, Content.to_id==to_id).all()
        db_session.close()
        for row in contents:
            containers.append(row.content)
        self.render("index.html", containers=containers, from_id=from_id, to_id=to_id)

    def post(self):
        body = self.get_argument('body')
        from_id = 1
        to_id = 2
        db_session = maker()
        new_content = Content(from_id=from_id,to_id=to_id,content=body)
        db_session.add(new_content)
        db_session.commit()
        db_session.close()

        self.redirect('/?to_id=%d'%(to_id))

class SelectHandler(BaseHandler):
    @tornado.web.authenticated

    def get(self):
        self.render("select_player.html", username=self.current_user)

    def post(self):
        playername = self.get_argument("playername")
        db_session = maker()
        users = db_session.query(User).all()
        db_session.close()
        for row in users:
            if playername in row.name:
                self.redirect('/?to_id=%s'%(row.id)) #1つしかヒットしないのでOK?（同じユーザ名があるとout)
        else:
            self.write_error(403)

class LoginHandler(BaseHandler):
    def get(self):
        self.render("login.html")

    def post(self):
        username = self.get_argument("username")
        db_session = maker()
        users = db_session.query(User).all()
        db_session.close()
        for row in users:
            if username in row.name:
                self.set_current_user(username)
                self.redirect("/select")
        self.write('select existing user\n')
        self.write_error(403)

class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_current_user()
        self.redirect('/login')


class Application(tornado.web.Application):
    def __init__(self):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        handlers = [
            (r'/', IndexHandler),
            (r'/login', LoginHandler),
            (r'/logout', LogoutHandler),
            (r'/select', SelectHandler),
        ]
        settings = dict(
            cookie_secret='gaofjawpoer940r34823842398429afadfi4iiad',
            static_path=os.path.join(BASE_DIR, "static"),
            template_path=os.path.join(BASE_DIR, "templates"),
            login_url="/login",
            #xsrf_cookies=True,
            #autoescape="xhtml_escape",
            debug=True,
            )

        tornado.web.Application.__init__(self,handlers,**settings)


if __name__ == '__main__':
    app = Application()
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
