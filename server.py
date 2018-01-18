#!/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
import os
import tornado.ioloop
import tornado.web
from tornado.web import url
import sqlalchemy as sa
import logging

class BaseHandler(tornado.web.RequestHandler):
    cookie_username = "username" #初期値？

    def get_current_user(self):
        username = self.get_secure_cookie(self.cookie_username)
        logging.debug('BaseHandler - username: %s' % username)
        if not username: return None
        return tornado.escape.utf8(username)

    def set_current_user(self, username):
        self.set_secure_cookie(self.cookie_username, tornado.escape.utf8(username))

    def clear_current_user(self):
        self.clear_cookie(self.cookie_username)



class IndexHandler(BaseHandler):
    @tornado.web.authenticated

    def get(self):
        db_url = 'mysql+pymysql://root:mydearest21@example-rds-mysql-server.cwddpv5w3iby.us-east-2.rds.amazonaws.com/exampledb?charset=utf8'
        engine = sa.create_engine(db_url, echo=True)
        logging.debug(self.get_current_user)
        from_id = engine.execute('SELECT id FROM users WHERE name = %s',self.get_current_user)
        to_id = 2 #とりあえず
        rows = engine.execute('SELECT content FROM contents WHERE from_id = %d AND to_id = %d'%(from_id,to_id))

        self.render("index.html", containers=rows, from_id=from_id, to_id=to_id)

    def post(self):
        db_url = 'mysql+pymysql://root:mydearest21@example-rds-mysql-server.cwddpv5w3iby.us-east-2.rds.amazonaws.com/exampledb?charset=utf8'
        engine = sa.create_engine(db_url, echo=True)
        body = self.get_argument('body')
        ins = 'INSERT INTO contents (from_id,to_id,content) VALUES (%s,%s,%s)'
        engine.execute(ins,from_id,to_id,body)

        self.redirect("/?from_id=%d&to_id=%d"%(from_id,to_id))

class SelectHandler(BaseHandler):
    @tornado.web.authenticated

    def get(self):
        self.render("select_player.html", username=self.get_current_user)

    def post(self):
        playername = self.get_argument("playername")
        logging.debug('SelectHandler:post %s'% (playername))
        db_url = 'mysql+pymysql://root:mydearest21@example-rds-mysql-server.cwddpv5w3iby.us-east-2.rds.amazonaws.com/exampledb?charset=utf8'
        engine = sa.create_engine(db_url, echo=True)
        to_id = engine.execute('SELECT id FROM users WHERE name = %s',playername)
        if len(list(to_id)) > 0:
            for x in to_id:
                self.redirect('/?to_id=%s'%(x.id))
        else:
            self.write_error(403)

class LoginHandler(BaseHandler):
    def get(self):
        self.render("login.html")

    def post(self):
        username = self.get_argument("username")

        logging.debug('LoginHandler:post %s' % (username))

        db_url = 'mysql+pymysql://root:mydearest21@example-rds-mysql-server.cwddpv5w3iby.us-east-2.rds.amazonaws.com/exampledb?charset=utf8'
        engine = sa.create_engine(db_url, echo=True)
        users = engine.execute('SELECT name FROM users WHERE name = %s',username)
        for row in users:
            if username in row.name:
                self.set_current_user(username)
                self.redirect("/select")
        self.write(users,username)
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
