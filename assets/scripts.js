// submit settings from settings form
// generic alert on success
$( document ).ready(function() {
    $( "#settings" ).submit(function( event ) {
        $.post( "/settings",$( "#settings" ).serialize()).done(alert('settings updated!'));
        return false;
    });
});

// submit a new post
// clear form on success
$(document).on("click","#submit_good_thing",function(e) {
    //console.log($( "#post" ).serialize());
    var mention_list = JSON.stringify($('#magic_friend_tagging').magicSuggest().getSelection());
    var data_in = $( "#post" ).serialize() + '&mentions=' + mention_list + '&view=';
    $.post( "/post",data_in)
        .done(function(data){
            $( '#post' ).each(function(){
                this.reset();
            });
            get_posts(data);
        });
    return false;
});

// friend tagging with magicsuggest
$( document ).ready(function() {
    var friend_ids = JSON.parse(localStorage['friend_ids']);
    $("input#magic_friend_tagging").magicSuggest({
        placeholder: "Tag Friends",
        allowFreeEntries: false,
        data: friend_ids,
        displayField: 'name',
       // valueField: 'id'
    });
});

$(document).on("click","a#cheer",function(e) {
    var cheer = $(this)
    var url_data = 'good_thing=' + cheer.parents('div#data_container').data('id');
        $.post( "/cheer",url_data).done(function(data){
            alert(data.cheered);
            if (data.cheered) {
                var result = '(' + data.cheers + ') uncheer';
            } else {
                var result = '(' + data.cheers + ') cheer';
            }
            cheer.text(result);
        });
        return false;
});


// delete a post or comment
$(document).on("click","a#delete",function(e) {
    var id = $(this).parents('div#data_container').data('id');
    var type = $(this).parents('div#data_container').data('type');
    var url_data = 'id=' + id + '&type=' + type;
    $.post( "/delete",url_data).done(function(data){
        if (type == 'comment') {
            console.log('deleting a comment')
            var result = data.num_comments + ' comments'
            $('div[data-id="'+id+'"]').parents('div#data_container').find('a#comment').text(result);
            $('div[data-id="'+id+'"]').remove();
        } else {
            console.log('deleting a good thing')
            console.log($('div[data-id="'+id+'"]').parents('li#good_thing'))
            $('div[data-id="'+id+'"]').parents('li#good_thing').remove();
        }
    });
    return false;
});

// save a comment
$(document).on("submit","form#comment",function(e) {
    var good_thing = $(this);
    var url_data = $( this ).serialize() + '&good_thing=' + $( this ).parents('div#data_container').data('id');
    $.post( "/comment",url_data).done(function(data){
        good_thing.trigger("reset");
        var id = good_thing.parents('div#data_container').data('id');
        get_comments(data,id);
    });
    return false;
});

// get all comments
$(document).on("click","a#comment",function(e) {
    var good_thing = $(this);
    if (good_thing.data('toggle') === 'off') {
        alert(good_thing.data('toggle'));
        var url_data = 'good_thing=' + good_thing.parents('div#data_container').data('id');
        $.post( "/comment",url_data).done(function(data){
            var id = good_thing.parents('div#data_container').data('id');
            get_comments(data,id);
        });
        good_thing.data('toggle', 'on');
        return false;
    } else if (good_thing.data('toggle') === 'on'){
        alert(good_thing.data('toggle'));
        good_thing.parents('div#data_container').find('div#comments').text('');
        good_thing.data('toggle', 'off');
        return false;
    }
});

// get all posts on page load
window.onload = function() {
    $( document ).ready(function() {
        var view = 'view=all';
        $.post( "/post",view).done(function(data){
            get_posts(data);
        });
    });
};

// change views
$( document ).ready(function() {
    $( "a#view_select" ).click(function( event ) {
        var data = 'view=' + $(this).data('view');
        $.post( "/post",data).done(function (data) {
            $('ul#good_things').empty();
            get_posts(data);
        });
        return false;
    });
});


// view a user profile
$(document).on("click","a#profile_link",function(e) {
    var url_data = 'view=' + $(this).parents('div#data_container').data('user_id');
    $.post( "/post",url_data).done(function (data) {
        $('ul#good_things').empty();
        get_posts(data);
    });
    return false;
});

// render posts from template and json data
function get_posts(post_list) {
    $.get('templates/good_thing_tpl.html', function(templates) {
        post_list.forEach(function(data) {
            // Fetch the <script /> block from the loaded external
            // template file which contains our greetings template.
            var template = $(templates).filter('#good_thing_tpl').html();
            $('ul#good_things').prepend(Mustache.render(template, data));
        });
    });
}

function get_comments(comment_list,id) {
    $.get('templates/good_thing_tpl.html', function(templates) {
        comment_list.forEach(function(data) {
            // Fetch the <script /> block from the loaded external
            // template file which contains our greetings template.
            var template = $(templates).filter('#comment_tpl').html();
            $('div#data_container[data-id="'+id+'"]').find('div#comments').prepend(Mustache.render(template, data));
        });
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
    FB.Event.subscribe('auth.logout', function(response) {
        window.location = "http://tgt-dev.appspot.com/logout";
    });

    // get friend list on login and store for friend tagging
    FB.getLoginStatus(function(response){
        var friend_ids = [];
        var friend_app_ids = {};
        // get list of friends who use 3gt
        FB.api("/me/friends",function (response) {
            if (response && !response.error) {
                response.data.forEach(function(friend_data) {
                    friend_app_ids[friend_data.name] = friend_data.id.toString();
                });
                console.log(friend_app_ids);
                // get list of taggable fb friends
                FB.api("/me/taggable_friends",function (response) {
                    if (response && !response.error) {
                        response.data.forEach(function(friend_data) {
                            friend = {
                                'name':friend_data.name,
                                'id':friend_data.id.toString()
                            };
                            // if the a taggable friend uses 3gt, store the user id
                            if (friend_data.name in friend_app_ids) {
                                console.log(friend_app_ids[friend_data.name]);
                                friend.app_id = friend_app_ids[friend_data.name];
                                console.log(friend);
                            }
                            friend_ids.push(friend);
                        });
                        localStorage['friend_ids'] = JSON.stringify(friend_ids);
                    } else {
                        console.log(response.error)
                    }
                });
            } else {
                console.log(response.error)
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

// logout function
$(document).on("click","a#logout",function(e) {
    FB.logout(function(response) {
        // user is now logged out
    });
    window.location = "http://tgt-dev.appspot.com/logout";
});
