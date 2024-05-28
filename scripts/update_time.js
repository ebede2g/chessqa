var socket = io();

socket.on('update_time', function(data) {
    // Оновлюємо сторінку змінами, отриманими від сервера
    // Наприклад, можна змінювати вміст HTML-елементів або стилізувати їх
    document.getElementById('someElementId').innerHTML = data.someValue;
    document.getElementById('anotherElementId').style.backgroundColor = data.color;
});
