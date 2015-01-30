from google.appengine.ext import db

class Settings(db.Model):
    reminder_days = db.IntegerProperty(default=0)
    default_fb = db.BooleanProperty(default=False)
    default_public = db.BooleanProperty(default=False)

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

    def template(self):
        template = {
            'id':self.key().id(),
            'good_thing':self.good_thing,
            'reason':self.reason,
            'user_id':self.user.id,
            'user_name':self.user.name,
            'get_cheers':self.get_cheers(),
            'num_cheers':self.num_cheers(),
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

    #maybe delete
    def num_cheers(self):
        return self.cheer_set.count()

class Cheer(db.Model):
    user = db.ReferenceProperty(User,required=True)
    good_thing = db.ReferenceProperty(GoodThing,required=True)
    created = db.DateTimeProperty(auto_now_add=True)

class Comment(db.Model):
    comment_text = db.StringProperty(required=True)
    user = db.ReferenceProperty(User,required=True)
    good_thing = db.ReferenceProperty(GoodThing,required=True)
    created = db.DateTimeProperty(auto_now_add=True)

    def template(self):
        template = {
            'comment_text':self.comment_text,
            'user':self.user.id
        }
        return template
