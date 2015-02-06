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
$( document ).ready(function() {
    $( "#post" ).submit(function( event ) {
        var data_in = $( "#post" ).serialize() + '&view=';
        $.post( "/post",data_in)
            .done(function(data){
                $( '#post' ).each(function(){
                    this.reset();
                });
                get_posts(data);
            });
        return false;
    });
});

// add a cheer
$(document).on("click","a#cheer",function(e) {
        var url_data = 'good_thing=' + $(this).data('id');
        $.post( "/cheer",url_data).done(function(data){
            var result = data + ' cheers'
            $(this).append(result);
        });
        return false;
});


// delete a post or comment
$(document).on("click","a#delete",function(e) {
    var id = $(this).data('id');
    var type = $(this).data('parent');
    var url_data = 'id=' + id + '&type=' + type;
    $.post( "/delete",url_data).done(function(data){
        $('#'+type+'[data-id="'+id+'"]').empty();
    });
    return false;
});

// save a comment
$(document).on("submit","form#comment",function(e) {
    var good_thing = $(this);
    var url_data = $( this ).serialize() + '&good_thing=' + $( this ).data('id');
    $.post( "/comment",url_data).done(function(data){
        good_thing.trigger("reset");
        var id = good_thing.data('id');
        get_comments(data,id);
    });
    return false;
});

// get all comments
$(document).on("click","a#comment",function(e) {
    var good_thing = $(this);
    var url_data = 'good_thing=' + good_thing.data('id');
    $.post( "/comment",url_data).done(function(data){
        var id = good_thing.data('id');
        get_comments(data,id);
    });
    return false;
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
            //window.history.pushState("", "", '/');
        });
        return false;
    });
});


// view a user profile
$(document).on("click","a#profile_link",function(e) {
    var url_data = 'view=' + $(this).data('id');
    $.post( "/post",data).done(function (data) {
        $('ul#good_things').empty();
        get_posts(data);
        //window.history.pushState("", "", '/');
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
            $('div#comments[data-id="'+id+'"]').prepend(Mustache.render(template, data));
        });
    });
}
