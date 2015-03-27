import json
import string
import datetime
from google.appengine.ext import db
from collections import Counter,OrderedDict

# model for user's settings
# TODO: fix timezone issue
class Settings(db.Model):
    reminder_days = db.IntegerProperty(default=0)
    default_fb = db.BooleanProperty(default=False)
    default_public = db.BooleanProperty(default=True)

    def template(self):
        template = {
            'reminder_days':self.reminder_days,
            'default_fb':self.default_fb,
            'default_public':self.default_public
        }
        return template

# model for a user's wordcloud. stores a json representation of a counter object
# and most recent update time
class WordCloud(db.Model):
    word_dict = db.TextProperty(default=None)
    updated = db.DateTimeProperty(auto_now_add=True)
    stopwords = db.StringListProperty(default=['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now'])

    # update the word counter.  only load posts since last update time
    # store the counter as json and change the last updated time
    def update_word_dict(self):
        counter = Counter()
        replace_punctuation = string.maketrans(string.punctuation, ' '*len(string.punctuation))
        if self.word_dict:
            counter.update(json.loads(self.word_dict))
        users = self.user_set.fetch(limit=None)
        for user in users:
            good_thing_list = user.goodthing_set.filter('created >=', self.updated).fetch(limit=None)
            for good_thing in good_thing_list:
                x = str(good_thing.good_thing).translate(replace_punctuation).lower()
                words = [word for word in x.split(' ') if word not in self.stopwords]
                counter.update(words)
        self.word_dict = json.dumps(counter)
        self.upated = datetime.datetime.now()

    # return the 20 most common words as a sorted list of dictionaries
    def get_sorted_word_dict(self):
        if self.word_dict:
            word_dict = json.loads(self.word_dict)
            sorted_dict = OrderedDict(sorted(word_dict.items(), key=lambda t: t[1]))
            result = [{'word':word,'count':sorted_dict[word]} for word in sorted_dict][-20:]
            print result
            return result
        else:
            return [{'word':"You haven't posted any good things!",'count':1}]

# model for each user based on facebook login information
# TODO: add email field
class User(db.Model):
    id = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)
    name = db.StringProperty(required=True)
    profile_url = db.StringProperty(required=True)
    access_token = db.StringProperty(required=True)
    public_user = db.BooleanProperty(default=None) # change default back to false
    settings = db.ReferenceProperty(Settings,required=True)
    word_cloud = db.ReferenceProperty(WordCloud,required=True)

# model for each good thing
# TODO: update to work with images
class GoodThing(db.Model):
    good_thing = db.StringProperty(required=True)
    reason = db.StringProperty(default=None)
    created = db.DateTimeProperty(auto_now_add=True)
    user = db.ReferenceProperty(User,required=True)
    public = db.BooleanProperty(default=True)
    wall = db.BooleanProperty(default=False)
    deleted = db.BooleanProperty(default=False)
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

    # return a list of cheers associated with this good thing
    # if no cheers, return None
    def get_cheers(self):
        cheers = self.cheer_set.fetch(limit=None)
        if cheers:
            result = [x.user.id for x in cheers]
        else:
            result = None
        return result

    # return true if the fb user id has cheered this good thing
    # else return false
    def cheered(self,user_id):
        user = User.get_by_key_name(user_id)
        cheer = self.cheer_set.filter('user =',user).get()
        if cheer:
            cheered = True
        else:
            cheered = False
        return cheered

    # return a list of user names mentioned in this good thing
    def get_mentions(self):
        mentions = self.mention_set.fetch(limit=None)
        result = [{'name':mention.to_user_name} for mention in mentions]
        return result

    # return the number of mentions
    def num_mentions(self):
        count = self.mention_set.count()
        if count > 0:
            return count
        else:
            return None

    #maybe delete
    def num_cheers(self):
        return self.cheer_set.count()

    # return the number of comments
    def num_comments(self):
        return self.comment_set.filter('deleted =',False).count()

# model for a cheer associated with a good thing
class Cheer(db.Model):
    user = db.ReferenceProperty(User,required=True)
    good_thing = db.ReferenceProperty(GoodThing,required=True)
    created = db.DateTimeProperty(auto_now_add=True)

# model for a comment associated with a good thing
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

# model for a mention associated with a good thing and a user's fb friend
# associates with to_user model if the user is a 3GT user
class Mention(db.Model):
    to_fb_user_id = db.StringProperty(required=True)
    to_user_name = db.StringProperty(required=True)
    to_user = db.ReferenceProperty(User)
    good_thing = db.ReferenceProperty(GoodThing,required=True)
    created = db.DateTimeProperty(auto_now_add=True)

# model for a notification (cheer, comment, mention)
class Notification(db.Model):
    from_user = db.ReferenceProperty(User,required=True, collection_name='from_user_set')
    to_user = db.ReferenceProperty(User,required=True,collection_name='to_user_set')
    event_type = db.StringProperty(required=True)
    event_id = db.StringProperty(required=True) # change to required = True
    created = db.DateTimeProperty(auto_now_add=True)
    read = db.BooleanProperty(default=False)

    def template(self):
        template = {
            'from_user':self.from_user.name,
            'event_type':self.event_type,
            'event_id':self.event_id,
        }
        return template
