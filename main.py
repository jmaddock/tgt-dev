import wsgiref.handlers
import webapp2
import fixpath
import views
import app_config

config = {}
config['webapp2_extras.sessions'] = app_config.CONFIG

app = webapp2.WSGIApplication(
        [('/*', views.HomeHandler),
         ('/logout', views.LogoutHandler),
         ('/post', views.PostHandler),
         ('/cheer', views.CheerHandler),
         ('/comment', views.CommentHandler),
         ('/delete', views.DeleteHandler),
         ('/intro', views.IntroHandler),
         ('/privacy', views.PrivacyHandler),
         ('/settings', views.SettingsHandler),
         ('/stat', views.StatHandler),
         ('/notify', views.NotificationHandler)],
        debug=True,
        config=config
    )

def main():
    wsgiref.handlers.CGIHandler().run(app)

if __name__ == "__main__":
    main()
