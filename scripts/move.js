document.addEventListener('DOMContentLoaded', function() {

    let squares = document.querySelectorAll('.square');
    let role = window.role_player;
    let socket = io();
    let prev_row = 4;
    let prev_col = 4;
    let prev_fig = 'start';

    squares.forEach(function(square) {
        square.addEventListener('click', function() {
            let row = square.getAttribute('data-row');
            let col = square.getAttribute('data-col');
            let fig = square.innerText;
            let color = ""; // Задаємо значення за замовчуванням

            if (square.classList.contains('marked_move')) {
                // Підсвітка доступних кроків
                color = 'marked_move';
            } else if (square.classList.contains('marked_atck')) {
                // Підсвітка доступних атак
                color = 'marked_atck';
            }

            if (fig === "") {
                fig = "_";
            }

            if (prev_fig) {
                socket.emit('update_board', {
                    role: role,
                    prev_row: prev_row,
                    prev_col: prev_col,
                    prev_fig: prev_fig,
                    this_row: row,
                    this_col: col,
                    this_fig: fig,
                    color: color
                });
            }

            prev_row = row;
            prev_col = col;
            prev_fig = fig;
        });
    });
});
