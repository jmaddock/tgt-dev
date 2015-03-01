import webapp2
from myapp import views

def main():
    app = webapp2.WSGIApplication(
        [('/*', HomeHandler),
         ('/logout', LogoutHandler),
         ('/post', PostHandler),
         ('/cheer', CheerHandler),
         ('/comment', CommentHandler),
         ('/delete', DeleteHandler),
         ('/intro', IntroHandler),
         ('/privacy', PrivacyHandler),
         ('/settings', SettingsHandler),
         ('/stat', StatHandler),
         ('/notify', NotificationHandler)],
        debug=True,
        config=config
    )

if __name__ == "__main__":
    main()
