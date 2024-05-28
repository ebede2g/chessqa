from flask import Flask, render_template, request, session
from flask_socketio import SocketIO, emit

import time
import math

board_size = 8
board_size_srv = [8, 8]
players = {'white': None, 'black': None}

allow_castling = [True, True]
allow_long_castling = [True, True]
allow_short_castling = [True, True]

marked_dots = [[], []]

game_time = [300, 300]
turn = True
allow_turn = True  # Можна і видалити

almost_shah = [[], []]

shah_memory = False
game_status = {
    # 0 - відсутній статус гри. 1 - шах . 2 - мат . 3 - пат . 4 - вийшов час гравця "role" .(2,3,4 - є завершальними)
    "status": 0,
    "role": "white"
}
old_game_status = 0

exempl_path = 'board/exempl.txt'
curbor_dng_path = 'board/currentboard_dng.txt'
curbor_path = "board/currentboard.txt"

imag_curbor_dng_path = 'board/imag/imag_currentboard_dng.txt'
imag_curbor_path = "board/imag/imag_currentboard.txt"

app = Flask(__name__, template_folder='pages', static_folder='scripts')
app.secret_key = 'your_secret_key'  # Ключ сесії
socketio = SocketIO(app)


def update_time():
    while True:
        game_time[turn] -= 1
        print(game_time)
        current_time = time.strftime("%H:%M:%S", time.localtime())
        emit('update_time', {'white_time': game_time[1], 'black_time': game_time[0], 'turn': turn}, broadcast=True)
        time.sleep(1)


def load_current_board():
    with open(curbor_path, "r") as file:
        return file.read().splitlines()


def assign_role():
    global turn
    if players['white'] is None and players['black'] is None:
        if turn:
            return 'white'
        else:
            return 'black'
    elif players['white'] is None:
        return 'white'
    elif players['black'] is None:
        return 'black'
    else:
        return 'observer'


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form.get('username')
        if username and (len(username) < 25):  # якшо ім'я не нуляче то можна загрузити сторінку
            role = assign_role()
            session['username'] = username
            players[role] = username

            with open(curbor_path, "r") as file:
                new_cur_bor = [list(line.strip()) for line in file]

            for i in range(len(new_cur_bor)):
                for j in range(len(new_cur_bor[i])):
                    This_figure = ord(new_cur_bor[i][j])  # Ви намагаєтесь отримати значення фігури з new_cur_bor
                    if (95 - This_figure) != 0:  # Чи черга зараз цього гравця і чи не порожня клітинка
                        totp = not turn ^ (9811 < This_figure < 9818)  # Чи обрана фігура належить гравцю
                        if totp:
                            dots = mark_dots(i, j, curbor_path, curbor_dng_path)
                            if dots.move_dots or dots.atck_dots:
                                marked_dots[turn].append(dots)

            return render_template(
                'boardPage_c1.html',
                board_size_row=board_size_srv[0],
                board_size_col=board_size_srv[1],
                username=session['username'],
                role=role,
                currentboard=load_current_board(),
                players=players
            )
    return render_template('enterPage_c0.html')


@socketio.on('connect')
def handle_connect():
    emit('player_connected', {'white': players['white'], 'black': players['black']}, broadcast=True)
    emit('game_status', game_status, broadcast=True)


@socketio.on('disconnect')
def handle_disconnect():
    if session['username'] == players['black']:
        players['black'] = None
    elif session['username'] == players['white']:
        players['white'] = None
    emit('player_disconnected', {'white': players['white'], 'black': players['black']}, broadcast=True)


class access_dots():
    def __init__(self, role, coords):
        self.move_dots = []
        self.atck_dots = []
        self.defn_dots = []
        self.atim_dots = []

        self.coords = coords
        self.role = role
        self.block_fig = False

    def to_json(self):
        return {
            'move_dots': self.move_dots,
            'atck_dots': self.atck_dots,
            'role': self.role
        }
    # Розширюю клас access_dots, додаючи нвое поле - defn_dots


class update_dots():
    def __init__(self, role):
        self.dots = []
        self.role = role
        self.fig = []

    def to_json(self):
        return {
            'dots': self.dots,
            'role': self.role,
            'fig': self.fig
        }


def mark_dots(tr, tc, path_to_board, path_to_board_d):
    with open(path_to_board, 'r') as file:
        f_r_curBoar = file.readlines()

    tf = ord(f_r_curBoar[tr][tc][-1])
    role = True if (9812 <= tf <= 9817) else False

    if 65 <= tf <= 90:
        role = True

    elif 97 <= tf <= 122:
        role = False

    def within_board(arr):  #Приймає координати
        return 0 <= arr[0] < board_size_srv[0] and 0 <= arr[1] < board_size_srv[1]

    def ray_degree(r, start_ang, div, approach, horse, dots):

        for ang in range(div):
            ang = start_ang + (360 / div) * ang

            first_fig_king = False  # Уявне продовження атаки, для унеможливлення відступу короля, умовно загрожує атакою всім клітинкам позаду атакованих фігур
            endray = False  # Якщо це не кінь то дійсні атаки і рухи закінчуютсья на першій перешкоді

            king_might_be_there = []  # Позаду може бути Король, якщо позаду пропуски і або самий король - то БЛОКУЄМО РУХ фігруи, координат иякої запсиано в масив

            for i in range(1, approach + 1):
                q1r = [
                    round(r * i * math.cos(math.pi * ang / 180) + tr),
                    round(r * i * math.sin(math.pi * ang / 180) + tc)]
                if within_board(q1r):
                    at = ord(f_r_curBoar[q1r[0]][q1r[1]][-1])  # at - attack

                    if (king_might_be_there):
                        if (q1r != king_might_be_there):
                            if ((at == 9812 and not role) or (at == 9818 and role)):
                                if king_might_be_there not in almost_shah[not role]:
                                    if (path_to_board == curbor_path):
                                        almost_shah[not role].append(king_might_be_there)
                                break
                            elif at != 95:
                                break
                        else:
                            pass

                    elif not endray or first_fig_king:
                        if at == 95:  # порожня комірка
                            if not endray:
                                dots.move_dots.append([q1r[0], q1r[1]])
                            if first_fig_king:
                                dots.atim_dots.append([q1r[0], q1r[1]])
                        elif not endray:
                            if ((not role) ^ (
                                    9811 < at < 9818)):  # позначення клітинок(у яких дружня фігура яку королям бити не можна), які дефає ця фігурка, кого вона може крити, шоб король не зміг атакувати захищені фіугрки.
                                dots.defn_dots.append([q1r[0], q1r[1]])
                                break
                            elif (role ^ (9811 < at < 9818)):  # ворог в досяжності
                                if ((at == 9812 and not role) or (at == 9818 and role)):  # в досяжності ворожий король
                                    dots.atim_dots.append([q1r[0], q1r[1]])
                                    first_fig_king = True
                                    if not horse:
                                        endray = True
                                else:
                                    dots.atck_dots.append([q1r[0], q1r[1]])
                                    if not horse:
                                        endray = True
                                    king_might_be_there = [q1r[0], q1r[1]]
                                    first_fig_king = False



                else:
                    break  # Завершення циклу,межі дошки

        return dots

    def isEmpty(row, s_col, f_col):
        if s_col > f_col:
            s_col, f_col = f_col, s_col  # Перестановка значень, якщо s_col > f_col
        ans = True
        for i in range(s_col + 1, f_col):
            if f_r_curBoar[row][i] != '_':
                ans = False
                break
        return ans

    if (tf == 9817 or tf == 9823):  # Обрано ♙ або ♟
        dots = access_dots(role, [tr, tc])
        inv = 1 if role else -1

        if (within_board([tr + 2 * inv, tc])):  #Чи не за межами дошки
            if (f_r_curBoar[tr + 2 * inv][tc] == '_' and f_r_curBoar[tr + inv][tc] == '_'):
                if ((tr <= 1 and role) or (tr >= (
                        board_size_srv[0] - 2) and not role)):  # чи пішак на стартових позиціях (на перших двох рядках)
                    dots.move_dots.append([tr + 2 * inv, tc])

        if (within_board([tr + inv, tc])):  #Чи не за межами дошки
            if (f_r_curBoar[tr + inv][tc] == '_'):
                dots.move_dots.append([tr + inv, tc])

        for i in (-1, 1):  # атака фігур по діоганалях
            if (within_board([tr + inv, tc + i])):
                at = ord(f_r_curBoar[tr + inv][tc + i][-1])
                if ((role ^ (9811 < at < 9818)) & (at != 95)):
                    dots.atck_dots.append([tr + inv, tc + i])
                elif (at == 95):
                    dots.atim_dots.append([tr + inv, tc + i])
                elif ((not role ^ (9811 < at < 9818)) & (at != 95)):
                    dots.defn_dots.append([tr + inv, tc + i])

        return dots

    elif (tf == 9816 or tf == 9822):  # Обрано ♘ коня
        dots = access_dots(role, [tr, tc])
        return ray_degree(2, 70, 8, 1, True, dots)

    elif (tf == 9815 or tf == 9821):  # Обрано ♗ аоб ♝
        dots = access_dots(role, [tr, tc])
        return ray_degree(1, 45, 4, 7, False, dots)

    elif (tf == 9820 or tf == 9814):  # Обрано ♜ або ♖
        dots = access_dots(role, [tr, tc])
        return ray_degree(1, 0, 4, board_size, False, dots)

    elif (tf == 9813 or tf == 9819):  # Обрано ♕ або ♛
        dots = access_dots(role, [tr, tc])
        return ray_degree(1, 0, 8, board_size, False, dots)

    elif (tf == 78 or tf == 110):  # Обрано N
        dots = access_dots(role, [tr, tc])
        return ray_degree(1, 70, 8, 1, True, dots)

    elif (tf == 9812 or tf == 9818):  # Обрано ♔ або ♚
        dots = access_dots(role, [tr, tc])
        if (allow_castling[role]):  # Чи рухався король цього кольору
            if (1 < tc < board_size_srv[1] - 2):
                if within_board([tr, board_size_srv[1] - 1]):
                    if (f_r_curBoar[tr][board_size_srv[1] - 1] != '_'):
                        if (allow_long_castling[role] & isEmpty(tr, tc, 0)):
                            dots.move_dots.append([tr, tc - 2])  # Королю записується додатковий хід на 7;6 або 0;6
                            # При виборі цього ходу - тура переміщається на 7;5 або 0;5

                if within_board([tr, 0]):
                    if (f_r_curBoar[tr][0] != '_'):
                        if (allow_short_castling[role] & isEmpty(tr, tc, board_size - 1)):
                            dots.move_dots.append([tr, tc + 2])  # Королю записується додатковий хід на 7;2 або 0;2
                            # При виборі цього ходу - тура переміщається на 7;3 або 0;3

        dots = ray_degree(1, 0, 8, 1, False, dots)

        # Відкриття файлу для читання
        with open(path_to_board_d, 'r') as file:
            board = file.readlines()
        # Перегляд усіх координат ходів і перевірка, чи вони містяться у файлі
        role_num = 'b' if role else 'w'
        for coord in dots.atck_dots + dots.move_dots:
            i, j = coord
            if 0 <= i < len(board) and 0 <= j < len(board[i]):
                if board[i][j] in [role_num, 'x']:
                    print(f'Видаляю ходи КОРОЛЯ {coord} бо цей хід заходить на клітинку {board[i][j]}')
                    # Додавання координат до списку для видалення
                    if coord in dots.atck_dots:
                        dots.atck_dots.remove(coord)
                    if coord in dots.move_dots:
                        dots.move_dots.remove(coord)

        return dots
















    else:
        dots = access_dots(role, [tr, tc])
        return ray_degree(1, 0, 8, board_size, False, dots)
        return dots


@socketio.on('update_board')
def handle_update_board(data):
    global turn
    global allow_castling
    global allow_short_castling
    global allow_long_castling
    global shah_memory

    if (data['role'] != 'observer'):

        if (data['role'] == 'white'):
            role = True
        else:
            role = False

        this_row = int(data['this_row'])
        this_col = int(data['this_col'])
        this_fig = data['this_fig']
        color = data['color']

        prev_row = int(data['prev_row'])
        prev_col = int(data['prev_col'])
        prev_fig = data['prev_fig']

        def what_if(imag_move=[], iteration=0):

            if (imag_move):
                # print("Почато уявну перевріку \n")
                this_curbor_dng = imag_curbor_dng_path + str(iteration)
                this_curbor = imag_curbor_path + str(iteration)

                def copy_board_data(source, destination):
                    with open(source, 'r') as src_file:
                        data = src_file.read()
                    with open(destination, 'w') as dest_file:
                        dest_file.write(data)

                copy_board_data(curbor_path, this_curbor)

                # Приходить два масиви - one_move[[2,2],[2,3]]
                # По перше - всі рокіровки ТИМЧАОСОВо прибираються (а й нє)
                # відкрвиаютсья два нові файли - imag_cb.txt Ta imag_cbd.txt
                # дошка imag_cb в місці [2,3] науває значення ьаткого ж  як і в [2,2]
                # а в місці [2,2] підчищаєтсья "_"

                # і нова дошка imag_cbd.txt тепер перевіряє чи поставлено шах
                # якщо так - то функція вертатиме True , що означатиме що цей мув є безпечним, цей мув - це чи атака чи просто рух.

                # Уяни експеремнт, а що якшо якось походити , чи буде шах ?
                with open(this_curbor, 'r') as file:
                    f_r_cb = file.readlines()

                from_row, from_col = imag_move[0]
                to_row, to_col = imag_move[1]
                piece = f_r_cb[from_row][from_col]
                f_r_cb[to_row] = f_r_cb[to_row][:to_col] + piece + f_r_cb[to_row][to_col + 1:]
                f_r_cb[from_row] = f_r_cb[from_row][:from_col] + '_' + f_r_cb[from_row][from_col + 1:]

                with open(this_curbor, 'w') as file:
                    file.writelines(f_r_cb)

            else:
                this_curbor_dng = curbor_dng_path
                this_curbor = curbor_path

            # онволення данх imag_curbor_dng
            # спершу знати де всі фігурки розташовін і скільки їх
            # алк я деган шоб мілйьон разів відкривати і закривати файл
            # Заповнення файлу первинними значеннями

            with open(this_curbor_dng, 'w') as file:
                for _ in range(board_size_srv[0]):
                    file.write('_' * board_size_srv[1] + '\n')

            with open(this_curbor, 'r') as file:
                f_r_cb = file.readlines()

            with open(this_curbor_dng, 'r') as file:
                f_r_cbd = file.readlines()

            for i in range(board_size_srv[0]):
                for j in range(board_size_srv[1]):
                    if f_r_cb[i][j] != '_':

                        figure = mark_dots(i, j, this_curbor, this_curbor_dng)

                        tf = ord(f_r_cb[i][j][-1])
                        if (tf == 9817 or tf == 9823):  # Очння лише рухів пішки
                            figure.move_dots.clear()
                        role_char = 'w' if figure.role else 'b'
                        for coord in figure.move_dots + figure.atck_dots + figure.defn_dots + figure.atim_dots:
                            i_, j_ = coord  # Розділення координат на рядок і стовбець
                            if 0 <= i_ < board_size_srv[0] and 0 <= j_ < board_size_srv[1]:
                                if f_r_cbd[i_][j_] == "w" and role_char == 'b':
                                    f_r_cbd[i_] = f_r_cbd[i_][:j_] + "x" + f_r_cbd[i_][j_ + 1:]
                                elif f_r_cbd[i_][j_] == "b" and role_char == 'w':
                                    f_r_cbd[i_] = f_r_cbd[i_][:j_] + "x" + f_r_cbd[i_][j_ + 1:]
                                elif f_r_cbd[i_][j_] == "x":
                                    f_r_cbd[i_] = f_r_cbd[i_][:j_] + "x" + f_r_cbd[i_][j_ + 1:]
                                else:
                                    f_r_cbd[i_] = f_r_cbd[i_][:j_] + role_char + f_r_cbd[i_][j_ + 1:]

            # Запис змінених даних назад у файл

            with open(this_curbor_dng, 'w') as file:
                file.writelines(f_r_cbd)

            # залежно від вхідних парметрів залежить яка дошка оновиться, уявна чи основна.

            # Перевірка чи поставлено ШАХ конкретно гравцю, який щойно уявно походив ?
            with open(this_curbor_dng, 'r') as file:
                f_r_cbd = file.readlines()
            is_shah_form_me = False

            old_game_status = game_status['status']
            for i in range(board_size_srv[0]):
                for j in range(board_size_srv[1]):
                    if f_r_cb[i][j] == '♔':
                        if (f_r_cbd[i][j] == 'x') or (f_r_cbd[i][j] == 'b'):
                            if imag_move:
                                is_shah_form_me = True  # Шах білим
                                print('Посвлено УЯВНИЙ шах білим')
                                break
                            if not imag_move:
                                print("трушний шах для Білих")
                                game_status['status'] = 1
                                game_status['role'] = 'white'
                                break


                    if f_r_cb[i][j] == '♚':
                        if (f_r_cbd[i][j] == 'x') or (f_r_cbd[i][j] == 'w'):
                            if imag_move:
                                is_shah_form_me = True  # Шах Чорним
                                print('Посвлено УЯВНИЙ шах Чорним')
                            if not imag_move:
                                print("трушний шах для Чорних")
                                game_status['status'] = 1
                                game_status['role'] = 'black'
                                break

                if is_shah_form_me or (game_status['status'] ^ old_game_status):
                    break


            return is_shah_form_me

        # клацнуто по клітинці для руху, атаки, або рокіровки.
        if (color == 'marked_atck' or color == 'marked_move'):

            update = update_dots(role)
            update.dots.extend([[this_row, this_col], [prev_row, prev_col]])
            update.fig.extend([prev_fig, ''])

            with open(curbor_path, "r") as file:
                currentboard = [list(line.strip()) for line in file]
            currentboard[this_row][this_col] = prev_fig
            currentboard[prev_row][prev_col] = '_'

            prev_fig_uniqd = ord(prev_fig[-1])
            this_fig_uniqd = ord(this_fig[-1])
            if (allow_castling[role] & (prev_fig_uniqd == 9812 or prev_fig_uniqd == 9818)):  # минула фігурка ♔ або ♚
                if (allow_long_castling[role] & (this_row == prev_row) & (this_col == prev_col - 2)):  # long casting
                    currentboard[this_row][0], currentboard[this_row][this_col + 1] = currentboard[this_row][
                        this_col + 1], \
                        currentboard[this_row][0]
                    update.dots.extend([[prev_row, 0], [prev_row, this_col + 1]])
                    update.fig.extend(['', currentboard[prev_row][this_col + 1]])
                elif (allow_short_castling[role] & (this_row == prev_row) & (
                        this_col == prev_col + 2)):  # short casting
                    board_size = len(currentboard)
                    currentboard[this_row][board_size - 1], currentboard[this_row][this_col - 1] = \
                        currentboard[this_row][
                            this_col - 1], currentboard[this_row][board_size - 1]
                    update.dots.extend([[prev_row, board_size - 1], [prev_row, this_col - 1]])
                    update.fig.extend(['', currentboard[prev_row][this_col - 1]])
                allow_castling[role] = False

            def equlZer():
                if (allow_short_castling[role] == allow_long_castling[role]):
                    allow_castling[role] = False
                print(f"EQUL 0 -> {allow_castling[role]}")

            if (allow_castling[role] & (prev_fig_uniqd == 9820 or prev_fig_uniqd == 9814)):
                if ((prev_row == ((not role) * (len(currentboard) - 1))) & (
                        prev_col == 0)):  # здійснено рух турою, яка віповідє довшій рокіровці
                    allow_long_castling[role] = False
                elif ((prev_row == ((not role) * (len(currentboard) - 1))) & (
                        prev_col == (len(currentboard[0]) - 1))):  # здійснено рух турою, яка віповідє довшій рокіровці
                    allow_short_castling[role] = False
                equlZer()

            if (allow_castling[not role] & (this_fig_uniqd == 9820 or this_fig_uniqd == 9814)):
                if ((this_row == (role * (len(currentboard) - 1))) & (
                        this_col == 0)):  # убито туру, яка віповідє довшій рокіровці
                    allow_long_castling[not role] = False
                elif ((this_row == (role * (len(currentboard) - 1))) & (
                        this_col == (len(currentboard[0]) - 1))):  # убито туру, яка віповідє довшій рокіровці
                    allow_short_castling[not role] = False
                equlZer()
            with open(curbor_path, "w") as file:
                for row in currentboard:
                    file.write(''.join(row) + '\n')
            turn = turn ^ allow_turn  # Зміна ходу print
            marked_dots[role].clear()

            almost_shah[0].clear()
            almost_shah[1].clear()
            what_if()

            with open(curbor_path, "r") as file:
                new_cur_bor = [list(line.strip()) for line in file]

            matik = game_status['status']
            print(f'matik ={matik}')







            for i in range(len(new_cur_bor)):
                for j in range(len(new_cur_bor[i])):
                    This_figure = ord(new_cur_bor[i][j])
                    if (95 - This_figure) != 0 and (
                            not (not role ^ turn)):  # Чи черга зараз цього гравця і чи не порожня клітинка
                        totp = role ^ (
                                9811 < This_figure < 9818)  # Чи обрана фігура належить вроому гравцю гравцю для прорахування його ходів
                        if totp:
                            dots = mark_dots(i, j, curbor_path, curbor_dng_path)
                            if dots.move_dots or dots.atck_dots:

                                if matik:
                                    print(
                                        f'постено мат, тому я починаю прцоес обрізання для фігури за кордами {new_cur_bor[i][j]}')

                                    if dots.move_dots:
                                        # Створюємо копію списку перед ітерацією
                                        for move_coord in dots.move_dots[:]:
                                            print(f'перевіряю мувез {move_coord}')
                                            if what_if([[i, j], move_coord]):
                                                print(f'удолив мувез {move_coord}')
                                                dots.move_dots.remove(move_coord)

                                    if dots.atck_dots:
                                        # Створюємо копію списку перед ітерацією
                                        for atck_dots in dots.atck_dots[:]:
                                            print(f'перевіряю атакенн {atck_dots}')
                                            if what_if([[i, j], atck_dots]):
                                                print(f'удолив ataken {atck_dots}')
                                                dots.atck_dots.remove(atck_dots)

                                    if dots.move_dots or dots.atck_dots:
                                        print(f'з атак зостались - {dots.atck_dots}')
                                        print(f'з movezz зостались - {dots.move_dots}')
                                        marked_dots[not role].append(dots)


                                else:
                                    marked_dots[not role].append(dots)

            durnytsya___8 = False
            print(f'{marked_dots}')
            if not marked_dots[not role]:
                print('durntsuya is True')
                durnytsya___8 = True











            if game_status['status'] == 1 and durnytsya___8:
                game_status['status'] = 2
            elif durnytsya___8:
                print('status is PAT')
                game_status['status'] = 3

            emit('board_updated', update.to_json(), broadcast=True)

            emit('game_status', game_status, broadcast=True)

            if game_status['status'] in (2, 3):
                # print('розіслати всім сповіщення про кінець гри')
                with open(exempl_path, 'r') as exempl_file:
                    exempl_content = exempl_file.readlines()

                with open(curbor_path, 'w') as curbor_file:
                    curbor_file.writelines(exempl_content)
                
                allow_castling = [True, True]
                allow_long_castling = [True, True]
                allow_short_castling = [True, True]
                turn = True
                what_if()

            game_status['status'] = 0



        # клацнуто по порожній клітнці, або фігурі.
        else:

            with open(curbor_path, "r") as file:
                currentboard = [list(line.strip()) for line in file]

            This_figure = ord(currentboard[this_row][this_col][-1])
            if (95 - This_figure) != 0 and (not (role ^ turn)):  # Чи черга зараз цього гравця і чи не порожня клітинка

                for puque in marked_dots[role]:
                    if puque.coords == [this_row, this_col]:
                        dots = puque
                        break
                    else:
                        dots = None

                if dots:
                    if almost_shah[role]:
                        print(f"доеревірочний код 707.  role= {role} almost_shah[role] = {almost_shah[role]}")
                        for coord in almost_shah[role]:
                            print(f'доеревірочний код 708. coord = {coord}')
                            if coord == [this_row, this_col]:  # Чи вибрана зараз така "підозріла" фігурка?
                                iteration = 0

                                # Створюємо копію списку перед ітерацією
                                for atck_coord in dots.atck_dots[:]:
                                    iteration += 1
                                    print(f'Певіряю атаку на - {atck_coord}')
                                    if what_if([[this_row, this_col], atck_coord], iteration):
                                        print(f'успішно видалено цею атаку.\n\n')
                                        dots.atck_dots.remove(atck_coord)

                                # Створюємо копію списку перед ітерацією
                                for move_coord in dots.move_dots[:]:
                                    iteration += 1
                                    print(f'Певіряю переміщення на - {move_coord}')
                                    if what_if([[this_row, this_col], move_coord], iteration):
                                        print(f'успішно видалено цей рух.\n\n')
                                        dots.move_dots.remove(move_coord)

                                break

                    if (game_status[
                        'status'] == 1):  # не є доцільним перевіряти яка роль цього гравця, шах завжди дається на один хід і цей хід авжди дістається ворогу
                        True

                    print(f' Зблоковані клітинки -  {almost_shah}')
                    emit('mark_dots', dots.to_json(), broadcast=True)


if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=3001)
