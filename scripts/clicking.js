document.addEventListener('DOMContentLoaded', function() {

    // Функція для очищення попередніх позначень
    function clearPreviousMarks() {
        var previousMarks = document.querySelectorAll('.square.marked_move, .square.marked_atck');
        previousMarks.forEach(function(square) {
            square.classList.remove('marked_move', 'marked_atck'); // Видалення класів
        });
        // console.log('Cleared previous marks');
    }

    let squares = document.querySelectorAll('.square');
    let selectedSquare = null;

    squares.forEach(function(square) {
        square.addEventListener('click', function() {
            clearPreviousMarks(); // Очистити попередні позначення перед кожним кліком на клітинку

            if (selectedSquare !== null) {
                selectedSquare.classList.remove('selected');

            }
            square.classList.add('selected');
            selectedSquare = square;
        });
    });
});