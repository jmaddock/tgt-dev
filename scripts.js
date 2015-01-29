// submit settings from settings form
// generic alert on success
$( "#settings" ).submit(function( event ) {
    $.post( "/settings",$( "#settings" ).serialize()).done(alert('settings updated!'));
    return false;
});

// submit a new post
// clear form on success
$( "#post" ).submit(function( event ) {
    $.post( "/post",$( "#post" ).serialize()).done(function(){
        alert('added a new post!');
        $( '#post' ).each(function(){
            this.reset();
        });
    });
    return false;
});

// add a cheer
$( "#cheer" ).submit(function( event ) {
    $.post( "/cheer",$( "#cheer" ).serialize()).done(alert('1 more cheer!'));
    return false;
});

// load fb sdk and log in w/ fb button
window.fbAsyncInit = function() {
    FB.init({appId: '{{ facebook_app_id }}', status: true, cookie: true,
             xfbml: true});
    FB.Event.subscribe('{% if current_user %}auth.logout{% else %}auth.login{% endif %}', function(response) {
        {% if current_user %} window.location = "/logout" {% else %} window.location.reload(); {% endif %}
    });
};
(function(){
    var e = document.createElement('script');
    e.type = 'text/javascript';
    e.src = document.location.protocol + '//connect.facebook.net/en_US/all.js';
    e.async = true;
    document.getElementById('fb-root').appendChild(e);
}());
