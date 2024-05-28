var socket = io();

socket.on('mark_dots', function(data_dots) {
    let role = window.role_player;

    var isBlack = (role === 'black');
    var isWhite = (role === 'white');

    var dotsRole = data_dots.role;

    if ((isBlack && !dotsRole) || (isWhite && dotsRole)) {

        var audio = new Audio('http://5.58.30.179:3001/err.mp3');
        audio.play();
        markAvailableMoves(data_dots.move_dots, 'marked_move');
        markAvailableMoves(data_dots.atck_dots, 'marked_atck');
    }
});

function markAvailableMoves(coordsArray, className) {
    coordsArray.forEach(function(coords) {
        var row = coords[0];
        var col = coords[1];
        var marked_sq = document.querySelector('.square[data-row="' + row + '"][data-col="' + col + '"]');
        if (marked_sq) {
            marked_sq.classList.add(className); // Додати відповідний клас
        }
    });
}

