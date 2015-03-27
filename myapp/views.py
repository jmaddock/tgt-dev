import facebook
import webapp2
import os
import jinja2
import urllib2
import models
import app_config
import json
import datetime

from google.appengine.ext import db
from webapp2_extras import sessions

FACEBOOK_APP_ID = app_config.FACEBOOK_APP_ID
FACEBOOK_APP_SECRET = app_config.FACEBOOK_APP_SECRET

# base handler that always checks to make sure the user is signed in and caches
# user information
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
                # Okay so user logged in.
                # Now, check to see if existing user
                user = models.User.get_by_key_name(cookie["uid"])
                graph = facebook.GraphAPI(cookie["access_token"])
                if not user:
                    # Not an existing user so get user info
                    profile = graph.get_object("me")
                    settings = models.Settings()
                    settings.put()
                    word_cloud = models.WordCloud()
                    word_cloud.put()
                    user = models.User(
                        key_name=str(profile["id"]),
                        id=str(profile["id"]),
                        name=profile["name"],
                        profile_url=profile["link"],
                        access_token=cookie["access_token"],
                        settings=settings,
                        word_cloud=word_cloud
                    )
                    user.put()
                elif user.access_token != cookie["access_token"]:
                    user.access_token = cookie["access_token"]
                    user.put()
                # User is now logged in
                self.session["user"] = {
                    'name':user.name,
                    'profile_url':user.profile_url,
                    'id':user.id,
                    'access_token':user.access_token,
                    'public_user':user.public_user,
                    'friends_list':graph.get_connections("me", "friends")
                }
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

    # creates a notification any time the current user cheers, comments, or
    # mentions
    # TODO: don't create notifications for current user
    def notify(self,event_type,to_user,event_id):
        from_user_id = str(self.current_user['id'])
        from_user = models.User.get_by_key_name(from_user_id)
        if from_user != to_user:
            notification = models.Notification(
                from_user=from_user,
                to_user=to_user,
                event_type=event_type,
                event_id=str(event_id),
            )
            notification.put()
        return from_user != to_user

# handler for home pages
class HomeHandler(BaseHandler):
    # check if user if user is logged in and public/private
    # serve landing page, public home page, or private home page
    def get(self):
        current_user = self.current_user
        if current_user:
            user_id = str(self.current_user['id'])
            user = models.User.get_by_key_name(user_id)
            if user.public_user:
                template = jinja_environment.get_template('public_main.html')
            elif user.public_user is False:
                template = jinja_environment.get_template('private_main.html')
            else:
                self.redirect('/intro')
                return None
            template_values = {
                'facebook_app_id':FACEBOOK_APP_ID,
                'current_user':current_user,
            }
        else:
            template = jinja_environment.get_template('landing.html')
            template_values = {
                'facebook_app_id':FACEBOOK_APP_ID,
            }
        self.response.out.write(template.render(template_values))

# API for saving and serving posts
class PostHandler(BaseHandler):
    # this should be turned into a get() method just for serving posts
    def post(self):
        user_id = str(self.current_user['id'])
        view = self.request.get('view')
        # if the client isn't saving a post
        if view != '':
            good_things = models.GoodThing.all().order('created').filter('deleted =',False)
            # return just the current user's posts
            if view == 'me':
                user = models.User.get_by_key_name(user_id)
                good_things.filter('user =',user)
                result = [x.template(user_id) for x in good_things]
            # return all public posts and current user's private posts
            elif view == 'all':
                user = models.User.get_by_key_name(user_id)
                result = [x.template(user_id) for x in good_things if (x.public or x.user.id == user.id)]
            # return a specified user's public posts
            else:
                profile_user_id = str(self.request.get('view'))
                profile_user = models.User.get_by_key_name(profile_user_id)
                good_things.filter('user =',profile_user).filter('public =',True)
                result = [x.template(user_id) for x in good_things]
        # save a post.  separate this into the post() method
        else:
            result = [self.save_post().template(user_id)]
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(result))

    # save a post to the datastore and return that post.  this should be turned
    # into the post() method
    def save_post(self):
        good_thing_text = self.request.get('good_thing')
        reason = self.request.get('reason')
        user_id = str(self.current_user['id'])
        user = models.User.get_by_key_name(user_id)
        raw_img = self.request.get('img')
        if raw_img != '':
            img = db.Blob(raw_img)
        else:
            img = None
        if user.public_user:
            if self.request.get('wall') == 'on':
                wall = True
            else:
                wall = False
            if self.request.get('public') == 'on':
                public = True
            else:
                public = False
        else:
            public = False
            wall = False
            mentions = []
        print wall, self.request.get('wall')
        good_thing = models.GoodThing(
            good_thing=good_thing_text,
            reason=reason,
            user=user,
            public=public,
            img=img,
            wall=wall
        )
        good_thing.put()
        # handle mentions here
        if self.request.get('mentions') != '':
            mention_list = json.loads(self.request.get('mentions'))
            for to_user_id in mention_list:
                if 'app_id' in to_user_id:
                    to_user = models.User.get_by_key_name(str(to_user_id['app_id']))
                    event_id = good_thing.key().id()
                    # handle mention notification
                    self.notify(event_type='mention',
                                to_user=to_user,
                                event_id=event_id)
                else:
                    to_user = None
                mention = models.Mention(
                    to_user=to_user,
                    good_thing=good_thing,
                    to_fb_user_id = to_user_id['id'], #may not have to store this...
                    to_user_name = to_user_id['name']
                )
                mention.put()
        # handle posting to fb
        if wall:
            graph = facebook.GraphAPI(self.current_user['access_token'])
            if img:
                graph.put_photo(image=raw_img,message=good_thing)
            else:
                graph.put_object('me','feed',message=good_thing)
        return good_thing

# API for saving and serving cheers
class CheerHandler(BaseHandler):
    def post(self):
        user_id = str(self.current_user['id'])
        user = models.User.get_by_key_name(user_id)
        good_thing_id = long(self.request.get('good_thing'))
        good_thing = models.GoodThing.get_by_id(good_thing_id)
        cheer = good_thing.cheer_set.filter('user =',user).get()
        # if the user has not cheered this post, create a new cheer
        if not cheer:
            cheer = models.Cheer(
                user=user,
                good_thing=good_thing,
            )
            cheer.put()
            cheered = True

            self.notify(event_type='cheer',
                        to_user=good_thing.user,
                        event_id=good_thing_id)
        # if the user has already cheered this post, delete the cheer
        else:
            cheer.delete()
            cheered = False
        self.response.headers['Content-Type'] = 'application/json'
        result = {
            'cheers':good_thing.num_cheers(),
            'cheered':cheered
        }
        self.response.out.write(json.dumps(result))

# API for saving and serving comments.  should be separated like good thing handler
class CommentHandler(BaseHandler):
    def post(self):
        comment_text = self.request.get('comment_text')
        good_thing_id = long(self.request.get('good_thing'))
        good_thing = models.GoodThing.get_by_id(good_thing_id)
        user_id = str(self.current_user['id'])
        # if the client is trying to save a comment, create a new comment, save
        # to the datastore and return the comment
        if comment_text != '':
            user = models.User.get_by_key_name(user_id)
            result = [self.save_comment(comment_text=comment_text,
                                        user=user,
                                        good_thing=good_thing).template(user_id)]
        # return all comments associated with a good thing
        else:
            comments = good_thing.comment_set.order('-created').filter('deleted =',False).fetch(limit=None)
            result = [x.template(user_id) for x in comments]
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(result))

    # save a comment to the datastore
    def save_comment(self, comment_text, user, good_thing):
        comment = models.Comment(
            comment_text=comment_text,
            user=user,
            good_thing=good_thing,
        )
        comment.put()
        event_id = good_thing.key().id()
        self.notify(event_type='comment',
                    to_user=good_thing.user,
                    event_id=event_id,)
        return comment

# API for deleting a good thing or a comment
class DeleteHandler(BaseHandler):
    def post(self):
        obj_id = long(self.request.get('id'))
        if self.request.get('type') == 'good_thing':
            good_thing = models.GoodThing.get_by_id(obj_id)
            good_thing.deleted = True
            good_thing.put()
        elif self.request.get('type') == 'comment':
            comment = models.Comment.get_by_id(obj_id)
            comment.deleted = True
            comment.put()
            result = {'num_comments':comment.good_thing.num_comments()}
            self.response.headers['Content-Type'] = 'application/json'
            self.response.out.write(json.dumps(result))

# log the current user out and redirect to the landing page
class LogoutHandler(BaseHandler):
    def get(self):
        if self.current_user is not None:
            self.session['user'] = None

        self.redirect('/')

# intro page for first time users
class IntroHandler(BaseHandler):
    # serve the intro page
    def get(self):
        current_user = self.current_user
        template = jinja_environment.get_template('intro.html')
        template_values = {
                'facebook_app_id':FACEBOOK_APP_ID,
                'current_user':current_user,
        }
        self.response.out.write(template.render(template_values))

    # update the public/private field after the user has passed through the intro
    # screen.
    def post(self):
        user_id = str(self.current_user['id'])
        user = models.User.get_by_key_name(user_id)
        # public version of the app
        if self.request.get('public_user') == 'public':
            user.public_user = True
        # private version of the app
        elif self.request.get('public_user') == 'private':
            user.public_user = False
        # randomly assign the user to the public or the private version
        elif self.request.get('public_user') == 'assign':
            user.public_user = random.choice([True, False])
        # if the user doesn't choose an option, don't assign a public/private
        # value.  app will redirect to this handler before allowing user to
        # view the home page
        else:
            user.public_user = None
        user.put()

# API for updating a user's settings
class SettingsHandler(BaseHandler):
    # update the current user's settings
    def post(self):
        user_id = str(self.current_user['id'])
        user = models.User.get_by_key_name(user_id)
        settings = user.settings
        if self.request.get('reminder_days_true') == 'on':
            reminder_days = self.request.get('reminder_days')
            if reminder_days != '':
                settings.reminder_days = int(reminder_days)
        else:
            settings.reminder_days = -1
        if self.request.get('default_fb') == 'on':
            settings.default_fb = True
        else:
            settings.default_fb = False
        if self.request.get('default_public') == 'on':
            settings.default_public = True
        else:
            settings.default_public = False
        settings.put()

    # get the current user's settings
    def get(self):
        user_id = str(self.current_user['id'])
        user = models.User.get_by_key_name(user_id)
        result = user.settings.template()
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(result))

# serve the privacy page
class PrivacyHandler(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template('privacy.html')
        template_values = {}
        self.response.out.write(template.render(template_values))

# API for getting a user's stats (word cloud, good things today).  can be used
# any public user, not just current user
class StatHandler(BaseHandler):
    def post(self):
        print self.request.get('user_id')
        if self.request.get('user_id') == '':
            user_id = str(self.current_user['id'])
        else:
            user_id = self.request.get('user_id')
        user = models.User.get_by_key_name(user_id)
        posts = user.goodthing_set.filter('deleted =',False).count()
        posts_today = user.goodthing_set.filter('created >=',datetime.date.today()).filter('deleted =',False).count()
        progress = int((float(posts_today)/3)*100)
        if progress > 100:
            progress = 100
        progress = str(progress) + '%'
        user.word_cloud.update_word_dict()
        word_cloud = user.word_cloud.get_sorted_word_dict()
        result = {
            'posts_today':posts_today,
            'progress':progress,
            'posts':posts,
            'word_cloud':word_cloud
        }
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(result))

# API for getting all of the current user's unread notifications
# after this API has been called once all notifications are marked as read
class NotificationHandler(BaseHandler):
    def get(self):
        user_id = str(self.current_user['id'])
        user = models.User.get_by_key_name(user_id)
        notification_list = models.Notification.all().filter('to_user =',user).filter('read =',False)
        result = []
        for notification in notification_list:
            result.append(notification.template())
            notification.read = True
            notification.put()

        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(result))

# serve the profile page for a public user
class ProfileHandler(BaseHandler):
    def get(self, user_id):
        user = models.User.get_by_key_name(user_id)
        if user.public_user:
            template = jinja_environment.get_template('profile.html')
            template_values = {
                'facebook_app_id':FACEBOOK_APP_ID,
                'user_id':user_id,
                'user_name':user.name
            }
        self.response.out.write(template.render(template_values))

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__),'templates')),
    autoescape=True,
    extensions=['jinja2.ext.autoescape'],
)
