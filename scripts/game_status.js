var socket = io();


socket.on('connect', function() {
    //console.log('Підключено до сервера');
});



function haiiiip (harkachka){
    setTimeout(puque, 2000);
    function puque() {
      alert(harkachka+"\nВийти до голвоного екрану.");
      window.location.href = "/";
    }

}

socket.on('game_status', function(update_data) {
    const statusInfo = document.getElementById('statusInfo');


    switch(update_data.status) {
        case 0:
            statusInfo.textContent = '[ - - - - - - ]';

            break;
        case 1:
            statusInfo.textContent = (update_data.role === 'white') ? 'Шах для білого' : 'Шах для чорного';
            break;
        case 2:
            statusInfo.textContent = (update_data.role === 'white') ? 'Мат для білого' : 'Мат для чорного';
            haiiiip(statusInfo.textContent)

            break;
        case 3:
            statusInfo.textContent = (update_data.role === 'white') ? 'Пат для білого' : 'Пат для чорного';

            haiiiip(statusInfo.textContent)

            break;
        case 4:
            statusInfo.textContent = (update_data.role === 'white') ? 'Вийшов час білого гравця' : 'Вийшов час чорного гравця';
            break;
        default:
            statusInfo.textContent = 'Помилка статусу гри.';
    }
});



