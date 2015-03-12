// submit settings from settings form
// generic alert on success
$(document).on("click","button#save_settings",function(e) {
    console.log($( "form#settings" ).serialize());
    $.post( "/settings",$( "form#settings" ).serialize()).done(function() {
        $('#settings_modal').modal('hide');
    });
    get_settings();
});

// submit a new post
// clear form on success
$(document).on("click","#submit_good_thing",function(e) {
    //console.log($( "#post" ).serialize());
    var data_in = $( "#post" ).serialize() + '&view=';
    console.log(data_in)
    $.post( "/post",data_in)
        .done(function(data){
            $( '#post' ).each(function(){
                this.reset();
            });
            get_posts(data);
            get_stats();
        });
    return false;
});

// cheer a post
$(document).on("click","a#cheer",function(e) {
    var cheer = $(this)
    var url_data = 'good_thing=' + cheer.parents('div#data_container').data('id');
        $.post( "/cheer",url_data).done(function(data){
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
            console.log('deleting a good thing');
            console.log($('div[data-id="'+id+'"]').parents('li#good_thing'));
            $('div[data-id="'+id+'"]').parents('li#good_thing').remove();
            get_stats();
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
        var url_data = 'good_thing=' + good_thing.parents('div#data_container').data('id');
        $.post( "/comment",url_data).done(function(data){
            var id = good_thing.parents('div#data_container').data('id');
            get_comments(data,id);
        });
        good_thing.data('toggle', 'on');
        return false;
    } else if (good_thing.data('toggle') === 'on'){
        good_thing.parents('div#data_container').find('div#comments').text('');
        good_thing.data('toggle', 'off');
        return false;
    }
});

// on page load
window.onload = function() {
    $( document ).ready(function() {
        // get all posts on page load
        var view = 'view=me';
        $.post( "/post",view).done(function(data){
            get_posts(data);
        });
        // get user settings
        get_settings();
        // get user stats
        get_stats();
    });
};

// render posts from template and json data
function get_posts(post_list) {
    $.get('static/templates/good_thing_tpl.html', function(templates) {
        post_list.forEach(function(data) {
            // Fetch the <script /> block from the loaded external
            // template file which contains our greetings template.
            var template = $(templates).filter('#good_thing_tpl').html();
            $('ul#good_things').prepend(Mustache.render(template, data));
        });
    });
}

function get_comments(comment_list,id) {
    $.get('static/templates/good_thing_tpl.html', function(templates) {
        comment_list.forEach(function(data) {
            // Fetch the <script /> block from the loaded external
            // template file which contains our greetings template.
            var template = $(templates).filter('#comment_tpl').html();
            $('div#data_container[data-id="'+id+'"]').find('div#comments').prepend(Mustache.render(template, data));
        });
    });
}

function get_stats() {
    $.post( "/stat",'').done(function (data) {
        $('div#progress').css('width',data.progress);
        $('span#progress').text(data.progress + ' Complete');
        $('#good_things_today').text(data.posts_today + ' Good Things Today');
        $('#good_things_total').text(data.posts + ' Total Good Things');
        $.get('static/templates/good_thing_tpl.html', function(templates) {
            $('div#word_cloud').empty();
            data.word_cloud.forEach(function(data) {
                var template = $(templates).filter('#word_cloud_tpl').html();
                $('div#word_cloud').prepend(Mustache.render(template, data));
            });
            $.fn.tagcloud.defaults = {
                size: {start: 14, end: 18, unit: 'pt'},
                color: {start: '#777', end: '#777'}
            };
            $(function () {
                $('#word_cloud a').tagcloud();
            });
        });
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
