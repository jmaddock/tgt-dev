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
$( document ).ready(function() {
    $( "#cheer" ).submit(function( event ) {
        var data = 'good_thing=' + $( "#cheer" ).data('id');

        $.post( "/cheer",data).done(alert('1 more cheer!'));
        return false;
    });
});

// add a comment
$( document ).ready(function() {
    $( "#comment" ).submit(function( event ) {
        var data = $( "#comment" ).serialize() + '&good_thing=' + $( "#comment" ).data('id');

        $.post( "/comment",data).done(function(){
            alert('added a new comment!');
            $( '#comment' ).each(function(){
                this.reset();
            });
        });
        return false;
    });
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
