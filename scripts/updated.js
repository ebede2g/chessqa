var socket = io();

socket.on('board_updated', function(update_data) {
    var audio = new Audio('http://5.58.30.179:3001/turn.mp3');
    audio.play();

    // Оновлення клітинок на основі даних з update_data
    update_data.dots.forEach(function(coords, index) {
        var row = coords[0];
        var col = coords[1];
        var figureName = update_data.fig[index]; // Отримання імені фігури для поточної клітинки

        var square = document.querySelector('.square[data-row="' + row + '"][data-col="' + col + '"]');
        square.innerHTML = figureName; // Оновлення імені фігури у клітинці
    });
});
