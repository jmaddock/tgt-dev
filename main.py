import wsgiref.handlers
import webapp2
import fixpath
import views
import app_config

config = {}
config['webapp2_extras.sessions'] = app_config.CONFIG

app = webapp2.WSGIApplication(
    [
        # logs the user out and redirects to home
        ('/logout', views.LogoutHandler),
        # API for posting good things and getting good things
        ('/post', views.PostHandler),
        # API for adding/removing cheers and getting cheers
        ('/cheer', views.CheerHandler),
        # API for posting comments and getting comments
        ('/comment', views.CommentHandler),
        # API for deleting good things and comments
        ('/delete', views.DeleteHandler),
        # handler for new users
        ('/intro', views.IntroHandler),
        # handler for privacy page
        ('/privacy', views.PrivacyHandler),
        # API for updating settings
        ('/settings', views.SettingsHandler),
        # API for getting user stats
        ('/stat', views.StatHandler),
        # API for getting notifications
        ('/notify', views.NotificationHandler),
        # handler for user profile
        ('/user/([^/]+)?', views.ProfileHandler),
        # home feed
        ('/*', views.HomeHandler),
    ],
    debug=True,
    config=config
)

def main():
    wsgiref.handlers.CGIHandler().run(app)

if __name__ == "__main__":
    main()
