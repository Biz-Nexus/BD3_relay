
import datetime
import dateutil.relativedelta

import tornado.web
import tornado.ioloop
import tornado.options
import tornado.httpserver
import tornado.httpclient
import tornado.gen
import tornado.escape
import tornado.websocket

from database import db_conn


class ContributionsHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('static/contributions.html')


class ContributorsHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('static/contributors.html')


class DashboardHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('static/dashboard.html')

class DashboardAPIHandler(tornado.web.RequestHandler):
    def get(self):
        now = datetime.datetime.now()
        this_month = datetime.datetime(now.year, now.month, 1)
        print(this_month, this_month.timestamp())
        next_month = this_month + dateutil.relativedelta.relativedelta(months=1)
        print(next_month, next_month.timestamp())

        since = int(next_month.timestamp())
        until = int(this_month.timestamp())

        event_rows = db_conn.iteritems()
        event_rows.seek(b'timeline_%s' % str(until).encode('utf8'))
        users = {}
        points = {}
        for event_key, event_id in event_rows:
            if not event_key.startswith(b'timeline_'):
                break
            # print(event_key, event_id)
            event_row = db_conn.get(b'event_%s' % event_id)
            event = tornado.escape.json_decode(event_row)
            qualified = 0
            point = 0
            for tag in event['tags']:
                if tag[0] == 't' and tag[1] == 'lxdao':
                    qualified += 1
                if tag[0] == 't' and tag[1] == 'points':
                    point = int(tag[2])
                    qualified += 1

            if qualified == 2:
                print(event)
                users.setdefault(event['pubkey'], [])
                users[event['pubkey']].append(event)

                points.setdefault(event['pubkey'], 0)
                points[event['pubkey']] += point

        self.finish({'users': users, 'points': points})
