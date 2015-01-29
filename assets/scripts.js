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
        $.post( "/post",$( "#post" ).serialize())
            .done(function(data){
                $( '#post' ).each(function(){
                    this.reset();
                });
                // fix this to append 'good_thing' template
                $('body').append($('<p>', {
                    text: data.good_thing
                }));
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
