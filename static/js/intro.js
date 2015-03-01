// submit settings from settings form
// generic alert on success
$(document).on("click","button#save_settings",function(e) {
    console.log($( "form#settings" ).serialize());
    $.post( "/settings",$( "form#settings" ).serialize()).done(alert('settings updated!'));
    get_settings();
});

// choose public or private user
$(document).on("click","#submit_public_user",function(e) {
    var data_in = $( "form#public_user" ).serialize();
    console.log(data_in);
    $.post( "/intro",data_in)
        .done(function(){
            window.location = "http://tgt-dev.appspot.com/";
        });
    return false;
});

// assign public or private user
function assign_user(friend_list) {
    $(document).on("click","#assign_public_user",function(e) {
        if (friend_list.length > 0 ) {
            data_in = 'public_user=public';
        } else {
            data_in = 'public_user=assign';
        }
        $.post( "/intro",data_in)
            .done(function(){
                window.location = "http://tgt-dev.appspot.com/";
            });
        return false;
    });
}

function get_settings() {
    $.get( "/settings",'')
        .done(function(data) {
            $('input#settings_wall').prop('checked', data.default_fb);
            $('input#settings_public').prop('checked', data.default_public);
            $('input#reminder_days').val(data.reminder_days);
        });
    return false;
}

function get_notifications(notification_list) {
    $.get('static/templates/good_thing_tpl.html', function(templates) {
        notification_list.forEach(function(data) {
            var template;
            if (data.event_type === 'comment') {
                template = $(templates).filter('#comment_notification_tpl').html();
            } else if (data.event_type === 'cheer') {
                template = $(templates).filter('#cheer_notification_tpl').html();
            } else if (data.event_type === 'mention') {
                template = $(templates).filter('#mention_notification_tpl').html();
            }
            $('ul#notifications').prepend(Mustache.render(template, data));
        });
    });
}

function logout() {
    FB.logout(function(response) {
        if (response && !response.error) {
            window.location = "http://tgt-dev.appspot.com/logout";
        } else {
            console.log(response.error)
        }
    });
}

window.fbAsyncInit = function() {
    FB.init({
        appId      : "997456320282204", // App ID
        version: 'v2.0',
        status     : true, // check login status
        cookie     : true, // enable cookies to allow the server to access the session
        xfbml      : true  // parse XFBML
    });

    // logout handler
    $(document).on("click","a#logout",function(e) {
        logout()
    });

    FB.getLoginStatus(function(response){
        FB.api("/me/friends", function (response) {
            if (response && !response.error) {
                assign_user(response.data);
            }
        });
    });
};

// Load the SDK Asynchronously
(function(d){
    var js, id = 'facebook-jssdk'; if (d.getElementById(id)) {return;}
    js = d.createElement('script'); js.id = id; js.async = true;
    js.src = "//connect.facebook.net/en_US/sdk.js";
    d.getElementsByTagName('head')[0].appendChild(js);
}(document));
