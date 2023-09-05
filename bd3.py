
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

import database


class ContributionsHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('static/contributions.html')


class ContributorsHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('static/contributors.html')


class DashboardHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('static/dashboard.html')

# class ContributorsAPIHandler(tornado.web.RequestHandler):
#     def get(self):
#         db_conn = database.get_conn()
#         address_rows = db_conn.iteritems()
#         address_rows.seek(b'DAO_lxdao_')
#         users = []
#         for address_key, _ in address_rows:
#             if not address_key.startswith(b'DAO_lxdao_'):
#                 break

#             addr = address_key.decode('utf8').replace('DAO_lxdao_', '').lower()
#             print(addr, b'profile_%s' % (addr.encode('utf8')))
#             profile_json = db_conn.get(b'profile_%s' % (addr.encode('utf8')))
#             print(profile_json)
#             if profile_json:
#                 profile = tornado.escape.json_decode(profile_json)
#                 profile['addr'] = addr
#                 users.append(profile)
#             else:
#                 users.append({'addr': addr})

#         self.finish({'users': users})

class DashboardAPIHandler(tornado.web.RequestHandler):
    def get(self):
        db_conn = database.get_conn()
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
        total = 0
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
                users.setdefault(event['pubkey'], {})
                if 'profile' not in users[event['pubkey']]:
                    profile_json = db_conn.get(b'profile_%s' % (event['pubkey'].encode('utf8')))
                    # print(profile_json)
                    if profile_json:
                        profile = tornado.escape.json_decode(profile_json)
                        users[event['pubkey']]['profile'] = profile

                users[event['pubkey']].setdefault('points', 0)
                users[event['pubkey']]['points'] += point

                total += point

        users_list = []
        for k, v in users.items():
            v['addr'] = k
            users_list.append(v)

        self.add_header('access-control-allow-origin', '*')
        self.finish({'users': users_list, 'total': total})


class PersonsAPIHandler(tornado.web.RequestHandler):
    def get(self):
        db_conn = database.get_conn()
        event_rows = db_conn.iteritems()
        event_rows.seek(b'profile_')
        results = {}
        for key, profile_json in event_rows:
            if not key.startswith(b'profile_'):
                break
            # print(key, profile_json)
            profile = tornado.escape.json_decode(profile_json)
            if 'role' in profile and profile['role'] == 'person':
                results[key.decode('utf8').replace('profile_', '')] = profile

        self.add_header('access-control-allow-origin', '*')
        self.finish(results)


class OrganizationsAPIHandler(tornado.web.RequestHandler):
    def get(self):
        db_conn = database.get_conn()
        p = self.get_argument('from', None)
        event_rows = db_conn.iteritems()
        if p:
            event_rows.seek(('profile_%s' % p).encode('utf8'))
        else:
            event_rows.seek(b'profile_')

        results = {'users': []}
        count = 0
        for key, profile_json in event_rows:
            if not key.startswith(b'profile_'):
                break
            if p:
                p = None
                continue

            # print(key, profile_json)
            profile = tornado.escape.json_decode(profile_json)
            if 'role' in profile and profile['role'] == 'organization':
                #results[key.decode('utf8').replace('profile_', '')] = profile
                addr = key.decode('utf8').replace('profile_', '')
                profile['address'] = addr
                results['users'].append(profile)
                results['next'] = addr

            count += 1
            if count >= 10:
                break

        self.add_header('access-control-allow-origin', '*')
        self.finish(results)

class AttestUserAPIHandler(tornado.web.RequestHandler):
    def get(self):
        db_conn = database.get_conn()
        addr = self.get_argument('addr')
        attest_rows = db_conn.iteritems()
        attest_rows.seek(('attest_%s' % addr).encode('utf8'))
        result = {'users':[]}
        for attest_key, attest_value in attest_rows:
            if not attest_key.startswith(('attest_%s' % addr.lower()).encode('utf8')):
                break
            print(attest_key, attest_value)
            keys = attest_key.decode('utf8').split('_')
            print(keys)
            if len(keys[2]) == 42:
                result['users'].append(keys[2])

        self.add_header('access-control-allow-origin', '*')
        self.finish(result)

class AttestEventAPIHandler(tornado.web.RequestHandler):
    def get(self):
        db_conn = database.get_conn()

class PeopleHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('static/people.html')

class PersonHandler(tornado.web.RequestHandler):
    def get(self):
        addr = self.get_argument('addr')
        db_conn = database.get_conn()
        profile_json = db_conn.get(('profile_%s' % addr).encode('utf8'))
        print(profile_json)
        if profile_json:
            profile = tornado.escape.json_decode(profile_json)
            if 'role' in profile and profile['role'] == 'organization':
                self.redirect('/organization?addr=%s' % addr)

        self.render('static/person.html')

class NeedHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('static/need.html')

class OrganizationsHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('static/organizations.html')

class OrganizationHandler(tornado.web.RequestHandler):
    def get(self):
        addr = self.get_argument('addr')
        db_conn = database.get_conn()
        profile_json = db_conn.get(('profile_%s' % addr).encode('utf8'))
        print(profile_json)
        if profile_json:
            profile = tornado.escape.json_decode(profile_json)
            if 'role' in profile and profile['role'] == 'person':
                self.redirect('/person?addr=%s' % addr)

        self.render('static/organization.html')

