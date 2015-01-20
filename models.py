from google.appengine.ext import db

class User(db.Model):
    id = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)
    name = db.StringProperty(required=True)
    profile_url = db.StringProperty(required=True)
    access_token = db.StringProperty(required=True)
    public_user = db.BooleanProperty(default=False)

class GoodThing(db.Model):
    good_thing = db.StringProperty(required=True)
    reason = db.StringProperty(default=None)
    created = db.DateTimeProperty(auto_now_add=True)
    user = db.ReferenceProperty(User,required=True)
    #mentions = db.StringListProperty()
    #public = db.BooleanProperty()
    #wall = db.BooleanField(default=False,help_text="Post to Facebook NewsFeed")
    #fbid = models.CharField(max_length=100,blank=True,default=None,editable=False)
    deleted = db.BooleanProperty(default=False)
    cheers = db.IntegerProperty(default=0)
    img = db.BlobProperty()

class Cheer(db.Model):
    user = db.ReferenceProperty(User,required=True)
    good_thing = db.ReferenceProperty(GoodThing,required=True)
    created = db.DateTimeProperty(auto_now_add=True)

class Comment(db.Model):
    comment_text = db.StringProperty(required=True)
    user = db.ReferenceProperty(User,required=True)
    good_thing = db.ReferenceProperty(GoodThing,required=True)
    created = db.DateTimeProperty(auto_now_add=True)

class Settings(db.Model):
    user = db.ReferenceProperty(User,required=True)
    reminderDays = db.IntegerProperty(default=0)
    #defaultFB = models.BooleanField(default=False)
    #defaultPublic = models.BooleanField(default=True)
