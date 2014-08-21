$(document).ready(function() {
    if ($('#message-wrapper').length > 0) {
        setTimeout(function() {
            $('#message-wrapper').fadeOut('slow');
        }, 10000);
    }

    $("#lnk-mark-bad").click(confirm_delete);
});

function confirm_delete(event) {
    var r = confirm("Are you sure you want to delete this session grid?");
    if (r!=true) {
        event.preventDefault();
    }
}

