#!/usr/bin/env python
#
# Copyright 2010 Facebook
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""
A barebones AppEngine application that uses Facebook for login.
1.  Make sure you add a copy of facebook.py (from python-sdk/src/)
    into this directory so it can be imported.
2.  Don't forget to tick Login With Facebook on your facebook app's
    dashboard and place the app's url wherever it is hosted
3.  Place a random, unguessable string as a session secret below in
    config dict.
4.  Fill app id and app secret.
5.  Change the application name in app.yaml.
"""

import facebook
import webapp2
import os
import jinja2
import urllib2
import models
import app_config

from google.appengine.ext import db
from webapp2_extras import sessions

FACEBOOK_APP_ID = app_config.FACEBOOK_APP_ID
FACEBOOK_APP_SECRET = app_config.FACEBOOK_APP_SECRET

config = {}
config['webapp2_extras.sessions'] = app_config.CONFIG

class BaseHandler(webapp2.RequestHandler):
    """Provides access to the active Facebook user in self.current_user
    The property is lazy-loaded on first access, using the cookie saved
    by the Facebook JavaScript SDK to determine the user ID of the active
    user. See http://developers.facebook.com/docs/authentication/ for
    more information.
    """
    @property
    def current_user(self):
        if self.session.get("user"):
            # model.User is logged in
            return self.session.get("user")
        else:
            # Either used just logged in or just saw the first page
            # We'll see here
            cookie = facebook.get_user_from_cookie(self.request.cookies,
                                                   FACEBOOK_APP_ID,
                                                   FACEBOOK_APP_SECRET)
            if cookie:
                print cookie
                # Okay so user logged in.
                # Now, check to see if existing user
                user = models.User.get_by_key_name(cookie["uid"])
                if not user:
                    # Not an existing user so get user info
                    graph = facebook.GraphAPI(cookie["access_token"])
                    profile = graph.get_object("me")
                    user = models.User(
                        key_name=str(profile["id"]),
                        id=str(profile["id"]),
                        name=profile["name"],
                        profile_url=profile["link"],
                        access_token=cookie["access_token"]
                    )
                    user.put()
                    self.redirect('/intro')
                elif user.access_token != cookie["access_token"]:
                    user.access_token = cookie["access_token"]
                    user.put()
                # User is now logged in
                self.session["user"] = {
                    'name':user.name,
                    'profile_url':user.profile_url,
                    'id':user.id,
                    'access_token':user.access_token,
                    'public_user':user.public_user
                }
                print self.session.get("user")
                return self.session.get("user")
        return None

    def dispatch(self):
        """
        This snippet of code is taken from the webapp2 framework documentation.
        See more at
        http://webapp-improved.appspot.com/api/webapp2_extras/sessions.html
        """
        self.session_store = sessions.get_store(request=self.request)
        try:
            webapp2.RequestHandler.dispatch(self)
        finally:
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        """
        This snippet of code is taken from the webapp2 framework documentation.
        See more at
        http://webapp-improved.appspot.com/api/webapp2_extras/sessions.html
        """
        return self.session_store.get_session()

class HomeHandler(BaseHandler):
    def get(self):
        current_user = self.current_user
        if current_user:
            view = self.request.get('view')
            template = jinja_environment.get_template('index.html')
            posts = models.GoodThing.all().order('-created')
            if view == 'me':
                user = models.User.get_by_key_name(current_user['id'])
                posts.filter('user =',user)
            template_values = {
                'facebook_app_id':FACEBOOK_APP_ID,
                'current_user':current_user,
                'posts':posts
            }
            self.response.out.write(template.render(template_values))
        else:
            template = jinja_environment.get_template('landing.html')
            posts = models.GoodThing.all()
            template_values = {
                'facebook_app_id':FACEBOOK_APP_ID,
                'current_user':current_user,
                'posts':posts
            }
            self.response.out.write(template.render(template_values))

class PostHandler(BaseHandler):
    def post(self):
        good_thing = self.request.get('good_thing')
        reason = self.request.get('reason')
        user_id = str(self.current_user['id'])
        user = models.User.get_by_key_name(user_id)
        if user.public_user:
            if self.request.get('wall') == 'on':
                wall = True
            if self.request.get('public') == 'on':
                public = True
            if wall:
                graph = facebook.GraphAPI(self.current_user['access_token'])
                graph.put_object('me','feed',message=good_thing)
        #photo_url = ("http://www.facebook.com/"
        #             "photo.php?fbid={0}".format(response['id']))
        else:
            public = False
            wall = False
        good_thing = models.GoodThing(
            good_thing=good_thing,
            reason=reason,
            user=user,
            public=public
        )
        good_thing.put()
        self.redirect('/')

class CheerHandler(BaseHandler):
    def post(self):
        user_id = str(self.current_user['id'])
        user = models.User.get_by_key_name(user_id)
        good_thing_id = self.request.get('good_thing')
        good_thing = models.GoodThing.get(good_thing_id)
        cheer = models.Cheer(
            user=user,
            good_thing=good_thing,
        )
        cheer.put()
        good_thing.cheers += 1
        good_thing.put()
        self.redirect('/')

class CommentHandler(BaseHandler):
    def post(self):
        user_id = str(self.current_user['id'])
        user = models.User.get_by_key_name(user_id)
        good_thing_id = self.request.get('good_thing')
        good_thing = models.GoodThing.get(good_thing_id)
        comment_text = self.request.get('comment_text')
        comment = models.Comment(
            comment_text=comment_text,
            user=user,
            good_thing=good_thing,
        )
        comment.put()
        print good_thing.comment_set
        self.redirect('/')

class LogoutHandler(BaseHandler):
    def get(self):
        if self.current_user is not None:
            self.session['user'] = None

        self.redirect('/')

class IntroHandler(BaseHandler):
    def get(self):
        template = jinja_environment.get_template('intro.html')
        template_values = {}
        self.response.out.write(template.render(template_values))

class PrivacyHandler(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template('privacy.html')
        template_values = {}
        self.response.out.write(template.render(template_values))

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__))
)

app = webapp2.WSGIApplication(
    [('/', HomeHandler),
     ('/logout', LogoutHandler),
     ('/post', PostHandler),
     ('/cheer', CheerHandler),
     ('/comment', CommentHandler),
     ('/intro', IntroHandler),
     ('/privacy', PrivacyHandler),],
    debug=True,
    config=config
)
