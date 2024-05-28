var socket = io();
let role = window.role_player;


var audio = new Audio('http://5.58.30.179:3001/bell.mp3');
var audio2 = new Audio('http://5.58.30.179:3001/dr.mp3')


function handlePlayerRoles(data) {
    let role = window.role_player;
    let sufix = (data['white'] === null && data['black'] === null) ? ' <- Суперник (*Відсутній*)' : ' <- Суперник';
    let sufix1 = role === 'white' ? ' <- Ви' : sufix;
    let sufix2 = role === 'black' ? ' <- Ви' : sufix;
    let whitePlayer = data['white'] !== null ? data['white'] : '<span style="color: red">*не існує*</span>';
    let blackPlayer = data['black'] !== null ? data['black'] : '<span style="color: blue">*не існує*</span>';
    document.getElementById('whitePlayerInfo').innerHTML = 'Гравець білий: ' + whitePlayer + sufix1;
    document.getElementById('blackPlayerInfo').innerHTML = 'Гравець чорний: ' + blackPlayer + sufix2;
}

socket.on('player_connected', function(data) {
    handlePlayerRoles(data);
    if (data['white'] !== null && data['black'] !== null) {
        if (role !== 'observer'){
            audio.play();
        }
    }


});

socket.on('player_disconnected', function(data) {
    handlePlayerRoles(data);
    if (data['white'] !== null && data['black'] !== null) {

    }
});


