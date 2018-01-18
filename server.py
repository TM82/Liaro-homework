#!/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
import os
import tornado.ioloop
import tornado.web
from tornado.web import url
import sqlalchemy as sa



class IndexHandler(tornado.web.RequestHandler):


    def get(self):
        #URL/?abc=1234&def=5678
        self.dburl = 'mysql+pymysql://root:mydearest21@example-rds-mysql-server.cwddpv5w3iby.us-east-2.rds.amazonaws.com/exampledb?charset=utf8'
        self.engine = sa.create_engine(self.dburl, echo=True)
        self.from_id = int(self.get_argument('from_id'))
        self.to_id = int(self.get_argument('to_id'))
        title = "ここにタイトルを入力"

        rows = self.engine.execute('SELECT content FROM contents WHERE from_id = %d AND to_id = %d'%(self.from_id,self.to_id))
        # for row in rows:
        #     containers.append(row)
        self.render("index.html", title=title, containers=rows, from_id=self.from_id, to_id=self.to_id)

    def post(self):
        # self.dburl = 'mysql+pymysql://root:mydearest21@example-rds-mysql-server.cwddpv5w3iby.us-east-2.rds.amazonaws.com/exampledb?charset=utf8'
        # engine = sa.create_engine(self.dburl, echo=True)
        body = self.get_argument('body')
        # from_id = 1
        # to_id = 2
        ins = 'INSERT INTO contents (from_id,to_id,content) VALUES (%s,%s,%s)'
        self.engine.execute(ins,self.from_id,self.to_id,body)

        self.redirect("/?from_id=%d&to_id=%d"%(from_id,to_id))

class Application(tornado.web.Application):

    def __init__(self):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        tornado.web.Application.__init__(self,
                                         [
                                         url(r'/', IndexHandler),
                                         #url(r'/chat', ChatHandler, name='chat'),
                                         ],
                                         template_path=os.path.join(BASE_DIR, 'templates'),
                                         static_path=os.path.join(BASE_DIR, 'static'),
                                         )


if __name__ == '__main__':
    app = Application()
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
