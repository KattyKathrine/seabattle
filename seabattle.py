# Морской бой без четырехпалубного корабля - как-то не канонично, поэтому я взяла на себя смелость
# немного расширить масштаб игры.

import random


class Field:
    def __init__(self, n=9):
        self.n = n
        self.cells = []
        self.cells_taken = []
        self.cells_miss = []
        for i in range(n):
            self.cells.append([])
        for i in range(n):
            for j in range(n):
                self.cells[i].append(" ")

    def __str__(self):
        text = "\033[39m  | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |\n"
        for i in range(self.n):
            text += "---------------------------------------\n" + str(i + 1) + " "
            for j in range(self.n):
                text += "| " + self.cells[i][j] + "\033[39m "
            text += "|\n"
        return text

    def put_ship(self, ship):

        color = str(31 + ship.length)

        if ship.position:
            for i in range(ship.length):
                self.cells[ship.a][ship.b + i] = "\033[" + color + "m■"
                ship.cells.append((ship.a, ship.b + i))
        elif not ship.position:
            for i in range(ship.length):
                self.cells[ship.a + i][ship.b] = "\033[" + color + "m■"
                ship.cells.append((ship.a + i, ship.b))

    def is_taken(self, a, b, length, position):
        if position:
            for i in range(length + 2):
                for j in range(3):
                    try:
                        if a + j - 1 < 0 or b + i - 1 < 0:
                            raise IndexError()
                        if self.cells[a + j - 1][b + i - 1] != " ":
                            return True
                    except IndexError:
                        continue
        else:
            for i in range(length + 2):
                for j in range(3):
                    try:
                        if a + i - 1 < 0 or b + j - 1 < 0:
                            raise IndexError()
                        if self.cells[a + i - 1][b + j - 1] != " ":
                            return True
                    except IndexError:
                        continue
        return False

    def put_ships(self, ships):

        for i in range(len(ships)):
            a = random.randint(0, self.n - 1)
            b = random.randint(0, self.n - 1)

            while not(ships[i].position and b + ships[i].length - 1 < self.n
                      or not ships[i].position and a + ships[i].length - 1 < self.n) \
                    or self.is_taken(a, b, ships[i].length, ships[i].position):
                a = random.randint(0, self.n - 1)
                b = random.randint(0, self.n - 1)

            ships[i].a = a
            ships[i].b = b
            self.put_ship(ships[i])
            self.cells_taken += ships[i].cells

    def put_ships_dialog(self, ships):
        for i in range(len(ships)):

            while True:
                try:
                    print(self)
                    print(f'Задайте положение {ships[i].length}-палубного корабля:')
                    a = int(input("По вертикали: ")) - 1
                    b = int(input("По горизонтали: ")) - 1
                    position = int(input("Введите 1 для горизонтального расположения корабля" 
                                         "или 0 для вертикального: "))
                    if not 0 <= a <= 8 or not 0 <= b <= 8 or not 0 <= position <= 1:
                        raise ValueError('''Некорректное значение. Попробуйте еще раз.
Значение координат должно быть в пределах от 1 до 9. Расположение задается цифрами 0 или 1''')
                    if not(position and b + ships[i].length - 1 < self.n
                       or not position and a + ships[i].length - 1 < self.n) \
                       or self.is_taken(a, b, ships[i].length, position):
                        raise ValueError("Не помещается. Давайте попробуем еще раз:")
                except ValueError as err:
                    if "invalid literal for int() with base 10" in str(err):
                        print('''Некорректное значение. Попробуйте еще раз.
Значение координат должно быть в пределах от 1 до 9. Расположение задается цифрами 0 или 1''')
                    else:
                        print(err)
                    continue
                else:
                    break

            ships[i].a = a
            ships[i].b = b
            ships[i].position = position
            self.put_ship(ships[i])
            self.cells_taken += ships[i].cells


class Ship:
    a = None
    b = None

    def __init__(self, length, position):
        self.length = length
        self.position = position
        self.cells = []

# Функция check_kill проверяет на ранен/убит.
# В нее передаются координаты ячейки, в случае, если игрок попал, список кораблей противника
# и список ячеек, угаданных игроком, который сейчас ходит.
# Находим корабль, которому принадлежит координата coord, берем у него список всех коррдинат,
# которые он занимает и проверяем все ли они присутствуют в списке уже открытых координат
# кораблей противника.


def check_kill(coord, ships, cells_taken):
    for i in range(len(ships)):
        if coord in ships[i].cells:
            for j in range(len(ships[i].cells)):
                if ships[i].cells[j] not in cells_taken:
                    return False
            return ships[i].cells
    return False

# Если найдены все ячейки, занятые кораблем, то мы точно знаем, что на всех окружающих его ячейках
# кораблей нет. Отметим их как промахи.


def put_blanks(ship, field_opponent):
    # ship - это список из координат корабля
    # field_opponent - это объект поля, на котором отмечаются корабли соперника
    # Если корабль однопалубный или корабль размещен горизонтально
    if len(ship) == 1 or ship[0][0] == ship[1][0]:
        for i in range(len(ship)):
            # Если ряд выше корабля существует, ставим туда точки
            if ship[i][0] != 0 and (ship[i][0] - 1, ship[i][1]) not in field_opponent.cells_miss:
                field_opponent.cells_miss.append((ship[i][0] - 1, ship[i][1]))
                field_opponent.cells[ship[i][0] - 1][ship[i][1]] = "."
            # Если ряд ниже существует, ставим туда точки
            if ship[i][0] != 8 and (ship[i][0] + 1, ship[i][1]) not in field_opponent.cells_miss:
                field_opponent.cells_miss.append((ship[i][0] + 1, ship[i][1]))
                field_opponent.cells[ship[i][0] + 1][ship[i][1]] = "."
        # Столбец слева от корабля
        if ship[0][1] != 0:
            for i in range(ship[0][0] - 1, ship[0][0] + 2):
                if i != -1 and i != 9 and (i, ship[0][1] - 1) not in field_opponent.cells_miss:
                    field_opponent.cells_miss.append((i, ship[0][1] - 1))
                    field_opponent.cells[i][ship[0][1] - 1] = "."
        # Столбец справа от корабля
        if ship[len(ship) - 1][1] != 8:
            for i in range(ship[0][0] - 1, ship[0][0] + 2):
                if i != -1 and i != 9 and (i, ship[len(ship) - 1][1] + 1) not in field_opponent.cells_miss:
                    field_opponent.cells_miss.append((i, ship[len(ship) - 1][1] + 1))
                    field_opponent.cells[i][ship[len(ship) - 1][1] + 1] = "."
    # Если корабль размещен вертикально
    if len(ship) > 1 and ship[0][1] == ship[1][1]:
        for i in range(len(ship)):
            # Столбец слева
            if ship[i][1] != 0 and (ship[i][0], ship[i][1] - 1) not in field_opponent.cells_miss:
                field_opponent.cells_miss.append((ship[i][0], ship[i][1] - 1))
                field_opponent.cells[ship[i][0]][ship[i][1] - 1] = "."
            # Столбец справа
            if ship[i][1] != 8 and (ship[i][0], ship[i][1] + 1) not in field_opponent.cells_miss:
                field_opponent.cells_miss.append((ship[i][0], ship[i][1] + 1))
                field_opponent.cells[ship[i][0]][ship[i][1] + 1] = "."
        # Ряд сверху
        if ship[0][0] != 0:
            for i in range(ship[0][1] - 1, ship[0][1] + 2):
                if i != -1 and i != 9 and (ship[0][0] - 1, i) not in field_opponent.cells_miss:
                    field_opponent.cells_miss.append((ship[0][0] - 1, i))
                    field_opponent.cells[ship[0][0] - 1][i] = "."
        # Ряд снизу
        if ship[len(ship) - 1][0] != 8:
            for i in range(ship[0][1] - 1, ship[0][1] + 2):
                if i != -1 and i != 9 and (ship[len(ship) - 1][0] + 1, i) not in field_opponent.cells_miss:
                    field_opponent.cells_miss.append((ship[len(ship) - 1][0] + 1, i))
                    field_opponent.cells[ship[len(ship) - 1][0] + 1][i] = "."


comp_ships = []
player_ships = []

for k in range(4, 0, -1):
    for m in range(5-k):
        comp_ships.append(Ship(k, random.randint(0, 1)))
        player_ships.append(Ship(k, random.randint(0, 1)))

# Создаем для игрока и ИИ по 2 поля:
# поле со своими кораблями и поле, на котором отмечаются корабли соперника


field_player_me = Field()
field_comp_me = Field()
field_player_opponent = Field()
field_comp_opponent = Field()

# Для ИИ заполним поле со своими кораблями автоматически

field_comp_me.put_ships(comp_ships)

# Игрок может выбрать заполнить свое поле автоматически или вручную.

print('Введите "y", если хотите вручную разместить корабли. '
      'Введите что угодно, чтобы корабли были размещены автоматически')

manual = input()
if manual == "y":
    field_player_me.put_ships_dialog(player_ships)
else:
    field_player_me.put_ships(player_ships)

print(field_player_me)

# У объекта доски со своими кораблями создадим поле, в котором будем хранить список всех координат,
# занятых кораблями. Отсортируем этот список. В дальнейшем он будет сравниваться со списком всех
# координат кораблей, открытых соперником. Когда списки сровняются, соответствующая сторона выиграла.

field_player_me.cells_taken.sort()
field_comp_me.cells_taken.sort()

# Через переменную player определяется игрок, который сейчас ходит.
# Первым ходит игрок. В случае промаха ход переходит к другой стороне.
# В случае попадания попавший ходит повторно.

# Если ИИ будет бездумно тыкать пальцем в небо, его будет очень легко обыграть, поэтому,
# чтобы было интересней с ним играть, дадим его ходам немного логики. По идее, ИРЛ
# игроки сообщают друг другу ранен корабль или убит. Если ИИ попал и ранил, то он сначала
# берет 4 клетки вокруг попадания и обходит их по кругу, пока не найдет еще клетку корабля.
# Потом нужно проверить в два направления вдоль получившейся прямой из двух клеток.
# Если ИИ попал и убил, то следующий ход он делает наугад.
# В next_moves будем собирать клетки, которые нужно ИИ проверить в следующие ходы.
# В current_ship будем собирать открытые клетки корабля.

player = 1
next_moves = []
current_ship = []
tmp = None

while True:

    if player:
        print("Ваш ход!")

        while True:
            try:
                vert = input("Укажите координату по вертикали:")
                hor = input("Укажите координату по горизонтали:")
                move = (int(vert) - 1, int(hor) - 1)
                if move in field_player_opponent.cells_taken or move in field_player_opponent.cells_miss:
                    raise ValueError("Уже было. Попробуйте еще раз.")
                if not 1 <= int(vert) <= 9 or not 1 <= int(hor) <= 9:
                    raise ValueError("Значение координат должно быть в пределах от 1 до 9.")
            except ValueError as err:
                if "invalid literal for int() with base 10" in str(err):
                    print('''Некорректное значение. Попробуйте еще раз.
Значение координат должно быть в пределах от 1 до 9.''')
                else:
                    print(err)
                continue
            else:
                break

        if move in field_comp_me.cells_taken:
            field_player_opponent.cells_taken.append(move)
            field_player_opponent.cells_taken.sort()
            field_player_opponent.cells[move[0]][move[1]] = "X"
            if check_kill(move, comp_ships, field_player_opponent.cells_taken):
                print("Убит!")
            else:
                print("Ранен")
        else:
            print("Мимо!")
            field_player_opponent.cells_miss.append(move)
            field_player_opponent.cells[move[0]][move[1]] = "."
            player = 0

        print(field_player_opponent)

        if field_player_opponent.cells_taken == field_comp_me.cells_taken:
            print("Вы выиграли!")
            break

    else:
        print("Ходит соперник!")
        if next_moves:
            move = next_moves.pop()
        else:
            vert = random.randint(0, field_player_me.n - 1)
            hor = random.randint(0, field_player_me.n - 1)
            move = (int(vert), int(hor))

            while move in field_comp_opponent.cells_taken or move in field_comp_opponent.cells_miss:
                vert = random.randint(0, field_player_me.n - 1)
                hor = random.randint(0, field_player_me.n - 1)
                move = (int(vert), int(hor))

        if move in field_player_me.cells_taken:
            field_comp_opponent.cells_taken.append(move)
            field_comp_opponent.cells_taken.sort()
            field_player_me.cells[move[0]][move[1]] = field_player_me.cells[move[0]][move[1]][:-1] + "X"
            field_comp_opponent.cells[move[0]][move[1]] = "X"
            tmp = check_kill(move, player_ships, field_comp_opponent.cells_taken)
            if tmp:
                print("Убит!")
                put_blanks(tmp, field_comp_opponent)
                next_moves = []
                current_ship = []

            else:
                print("Ранен")
                if not current_ship:
                    current_ship.append(move)
                    for i in [(move[0] - 1, move[1]), (move[0], move[1] - 1),
                              (move[0] + 1, move[1]), (move[0], move[1] + 1)]:
                        if i not in field_comp_opponent.cells_miss and 0 <= i[0] <= 8 and 0 <= i[1] <= 8:
                            next_moves.append(i)
                elif current_ship[0][0] == move[0] and current_ship[0][1] < move[1]:
                    current_ship.append(move)
                    next_moves = []
                    if move[1] + 1 != 9 and \
                       (move[0], move[1] + 1) not in field_comp_opponent.cells_miss:
                        next_moves.append((move[0], move[1] + 1))
                    else:
                        next_moves.append((current_ship[0][0], current_ship[0][1] - 1))
                elif current_ship[0][0] == move[0] and current_ship[0][1] > move[1]:
                    current_ship.append(move)
                    next_moves = []
                    next_moves.append((move[0], move[1] - 1))
                elif current_ship[0][1] == move[1] and current_ship[0][0] < move[0]:
                    current_ship.append(move)
                    next_moves = []
                    if move[0] + 1 != 9 and \
                       (move[0] + 1, move[1]) not in field_comp_opponent.cells_miss:
                        next_moves.append((move[0] + 1, move[1]))
                    else:
                        next_moves.append((current_ship[0][0] - 1, current_ship[0][1]))
                elif current_ship[0][1] == move[1] and current_ship[0][0] > move[0]:
                    current_ship.append(move)
                    next_moves = []
                    next_moves.append((move[0] - 1, move[1]))

            print(field_player_me)

        else:
            print("Мимо!")
            field_comp_opponent.cells_miss.append(move)
            player = 1
            field_comp_opponent.cells[move[0]][move[1]] = "."
            if len(current_ship) > 1:
                if current_ship[0][0] == move[0]:
                    next_moves = []
                    next_moves.append((current_ship[0][0], current_ship[0][1] - 1))
                elif current_ship[0][1] == move[1]:
                    next_moves = []
                    next_moves.append((current_ship[0][0] - 1, current_ship[0][1]))


        if field_player_me.cells_taken == field_comp_opponent.cells_taken:
            print("Вы проиграли =(")
            break
