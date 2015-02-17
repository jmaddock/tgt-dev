from google.appengine.ext import db

class Settings(db.Model):
    reminder_days = db.IntegerProperty(default=0)
    default_fb = db.BooleanProperty(default=False)
    default_public = db.BooleanProperty(default=False)

    def template(self):
        template = {
            'reminder_days':self.reminder_days,
            'default_fb':self.default_fb,
            'default_public':self.default_public
        }
        return template

class User(db.Model):
    id = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)
    name = db.StringProperty(required=True)
    profile_url = db.StringProperty(required=True)
    access_token = db.StringProperty(required=True)
    public_user = db.BooleanProperty(default=True) # change default back to false
    settings = db.ReferenceProperty(Settings,required=True)

class GoodThing(db.Model):
    good_thing = db.StringProperty(required=True)
    reason = db.StringProperty(default=None)
    created = db.DateTimeProperty(auto_now_add=True)
    user = db.ReferenceProperty(User,required=True)
    #mentions = db.StringListProperty()
    public = db.BooleanProperty(default=True)
    wall = db.BooleanProperty(default=False)
    #fbid = models.CharField(max_length=100,blank=True,default=None,editable=False)
    deleted = db.BooleanProperty(default=False)
    #cheers = db.IntegerProperty(default=0)
    img = db.BlobProperty()

    def template(self,user_id):
        if user_id == self.user.id:
            current_user = True
        else:
            current_user = False
        template = {
            'id':self.key().id(),
            'good_thing':self.good_thing,
            'reason':self.reason,
            'user_id':self.user.id,
            'user_name':self.user.name,
            #'get_cheers':self.get_cheers(),
            'num_cheers':self.num_cheers(),
            'num_comments':self.num_comments(),
            'current_user':current_user,
            'cheered':self.cheered(user_id),
            'mentions':self.get_mentions(),
            'num_mentions':self.num_mentions(),
            #add img
        }
        return template

    def get_cheers(self):
        cheers = self.cheer_set.fetch(limit=None)
        if cheers:
            result = [x.user.id for x in cheers]
        else:
            result = None
        return result

    def cheered(self,user_id):
        user = User.get_by_key_name(user_id)
        cheer = self.cheer_set.filter('user =',user).get()
        if cheer:
            cheered = True
        else:
            cheered = False
        return cheered

    def get_mentions(self):
        mentions = self.mention_set.fetch(limit=None)
        result = [{'name':mention.to_user_name} for mention in mentions]
        return result

    def num_mentions(self):
        return self.mention_set.count()

    #maybe delete
    def num_cheers(self):
        return self.cheer_set.count()

    def num_comments(self):
        return self.comment_set.filter('deleted =',False).count()

class Cheer(db.Model):
    user = db.ReferenceProperty(User,required=True)
    good_thing = db.ReferenceProperty(GoodThing,required=True)
    created = db.DateTimeProperty(auto_now_add=True)

class Comment(db.Model):
    comment_text = db.StringProperty(required=True)
    user = db.ReferenceProperty(User,required=True)
    good_thing = db.ReferenceProperty(GoodThing,required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    deleted = db.BooleanProperty(default=False)

    def template(self,user_id):
        if user_id == self.user.id:
            current_user = True
        else:
            current_user = False
        template = {
            'id':self.key().id(),
            'comment_text':self.comment_text,
            'user_name':self.user.name,
            'user_id':self.user.id,
            'good_thing_id':self.good_thing.key().id(),
            'current_user':current_user
        }
        return template

class Mention(db.Model):
    to_fb_user_id = db.StringProperty(required=True)
    to_user_name = db.StringProperty(required=True)
    to_user = db.ReferenceProperty(User)
    good_thing = db.ReferenceProperty(GoodThing,required=True)
    created = db.DateTimeProperty(auto_now_add=True)

class Notification(db.Model):
    from_user = db.ReferenceProperty(User,required=True),
    to_user = db.ReferenceProperty(User,required=True)
    event_type = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    read = db.BooleanProperty(default=False)
