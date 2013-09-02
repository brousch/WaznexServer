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

function Cycle() { /*if(location.href.indexOf("Cycle") < 0) { return; }*/  if(typeof this.currentCell == "undefined") { this.currentCell = 0; } var allCells = document.getElementsByClassName("cell"); for(var c = 0; c < allCells.length; ++c) { var transform = (this.currentCell == c ? "scale(4)" : null); allCells[c].style.WebkitTransform = transform; allCells[c].style.MozTransform = transform; } ++this.currentCell; if(this.currentCell >= allCells.length) { this.currentCell = 0; } } setInterval(Cycle, 2000);
