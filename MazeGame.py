import os
import pygame
import pygame.locals as pl
import random
import time
import pickle
import operator

os.environ['SDL_VIDEO_WINDOW_POS'] = '%d, %d' % (0, 30)

pygame.init()

# Fonts
time_font = pygame.font.Font("BMJUA_ttf.ttf", 45)
defalut_font = pygame.font.Font("BMJUA_ttf.ttf", 25)
rank_font = pygame.font.Font("BMJUA_ttf.ttf", 45)
myrank_font = pygame.font.Font("BMJUA_ttf.ttf", 56)

# Colors
black = ( 0,  0,  0)
white = (255,255,255)
back_color = (244, 233, 255)
color = (60, 23, 96)

# Size
screen_width = 776
screen_height = 584
maze_width = 0
maze_height = 0
block_size = 8
path_width = 3
cell_size = block_size * path_width
player_size = cell_size-8

intro_image = pygame.image.load("image/intro.png")
player_image = pygame.image.load("image/player.png")
goal_image = pygame.image.load("image/mask.png")
pause1_image = pygame.image.load("image/pause1.png")
pause2_image = pygame.image.load("image/pause2.png")
pause3_image = pygame.image.load("image/pause3.png")
round1_image = pygame.image.load("image/round1.png")
round2_image = pygame.image.load("image/round2.png")
round3_image = pygame.image.load("image/round3.png")
rank_image = pygame.image.load("image/rank.png")

dict = {}
user_id = ""
sum = 0.0
rank = 0

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('마스크를 찾고싶수룡')

class TextInput:
    """
    This class lets the user input a piece of text, e.g. a name or a message.
    This class let's the user input a short, one-lines piece of text at a blinking cursor
    that can be moved using the arrow-keys. Delete, home and end work as well.
    """
    def __init__(
            self,
            initial_string="",
            font_family="BMJUA_ttf.ttf",
            font_size=28,
            antialias=True,
            text_color=black,
            cursor_color=black,
            repeat_keys_initial_ms=400,
            repeat_keys_interval_ms=35,
            max_string_length=10):
        """
        :param initial_string: Initial text to be displayed
        :param font_family: name or list of names for font (see pygame.font.match_font for precise format)
        :param font_size:  Size of font in pixels
        :param antialias: Determines if antialias is applied to font (uses more processing power)
        :param text_color: Color of text (duh)
        :param cursor_color: Color of cursor
        :param repeat_keys_initial_ms: Time in ms before keys are repeated when held
        :param repeat_keys_interval_ms: Interval between key press repetition when held
        :param max_string_length: Allowed length of text
        """

        # Text related vars:
        self.antialias = antialias
        self.text_color = text_color
        self.font_size = font_size
        self.max_string_length = max_string_length
        self.input_string = initial_string  # Inputted text

        if not os.path.isfile(font_family):
            font_family = pygame.font.match_font(font_family)

        self.font_object = pygame.font.Font(font_family, font_size)

        # Text-surface will be created during the first update call:
        self.surface = pygame.Surface((1, 1))
        self.surface.set_alpha(0)

        # Vars to make keydowns repeat after user pressed a key for some time:
        self.keyrepeat_counters = {}  # {event.key: (counter_int, event.unicode)} (look for "***")
        self.keyrepeat_intial_interval_ms = repeat_keys_initial_ms
        self.keyrepeat_interval_ms = repeat_keys_interval_ms

        # Things cursor:
        self.cursor_surface = pygame.Surface((int(self.font_size / 20 + 1), self.font_size))
        self.cursor_surface.fill(cursor_color)
        self.cursor_position = len(initial_string)  # Inside text
        self.cursor_visible = True  # Switches every self.cursor_switch_ms ms
        self.cursor_switch_ms = 500  # /|\
        self.cursor_ms_counter = 0

        self.clock = pygame.time.Clock()

    def update(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                self.cursor_visible = True  # So the user sees where he writes

                # If none exist, create counter for that key:
                if event.key not in self.keyrepeat_counters:
                    self.keyrepeat_counters[event.key] = [0, event.unicode]

                if event.key == pl.K_BACKSPACE:
                    self.input_string = (
                        self.input_string[:max(self.cursor_position - 1, 0)]
                        + self.input_string[self.cursor_position:]
                    )

                    # Subtract one from cursor_pos, but do not go below zero:
                    self.cursor_position = max(self.cursor_position - 1, 0)
                elif event.key == pl.K_DELETE:
                    self.input_string = (
                        self.input_string[:self.cursor_position]
                        + self.input_string[self.cursor_position + 1:]
                    )

                elif event.key == pl.K_RETURN:
                    return True

                elif event.key == pl.K_RIGHT:
                    # Add one to cursor_pos, but do not exceed len(input_string)
                    self.cursor_position = min(self.cursor_position + 1, len(self.input_string))

                elif event.key == pl.K_LEFT:
                    # Subtract one from cursor_pos, but do not go below zero:
                    self.cursor_position = max(self.cursor_position - 1, 0)

                elif event.key == pl.K_END:
                    self.cursor_position = len(self.input_string)

                elif event.key == pl.K_HOME:
                    self.cursor_position = 0

                elif len(self.input_string) < self.max_string_length or self.max_string_length == -1:
                    if event.unicode == " ":
                        break

                    # If no special key is pressed, add unicode of key to input_string
                    self.input_string = (
                        self.input_string[:self.cursor_position]
                        + event.unicode
                        + self.input_string[self.cursor_position:]
                    )
                    self.cursor_position += len(event.unicode)  # Some are empty, e.g. K_UP

            elif event.type == pl.KEYUP:
                # *** Because KEYUP doesn't include event.unicode, this dict is stored in such a weird way
                if event.key in self.keyrepeat_counters:
                    del self.keyrepeat_counters[event.key]

        # Update key counters:
        for key in self.keyrepeat_counters:
            self.keyrepeat_counters[key][0] += self.clock.get_time()  # Update clock

            # Generate new key events if enough time has passed:
            if self.keyrepeat_counters[key][0] >= self.keyrepeat_intial_interval_ms:
                self.keyrepeat_counters[key][0] = (
                    self.keyrepeat_intial_interval_ms
                    - self.keyrepeat_interval_ms
                )

                event_key, event_unicode = key, self.keyrepeat_counters[key][1]
                pygame.event.post(pygame.event.Event(pl.KEYDOWN, key=event_key, unicode=event_unicode))

        # Re-render text surface:
        self.surface = self.font_object.render(self.input_string, self.antialias, self.text_color)

        # Update self.cursor_visible
        self.cursor_ms_counter += self.clock.get_time()
        if self.cursor_ms_counter >= self.cursor_switch_ms:
            self.cursor_ms_counter %= self.cursor_switch_ms
            self.cursor_visible = not self.cursor_visible

        if self.cursor_visible:
            cursor_y_pos = self.font_object.size(self.input_string[:self.cursor_position])[0]
            # Without this, the cursor is invisible when self.cursor_position > 0:
            if self.cursor_position > 0:
                cursor_y_pos -= self.cursor_surface.get_width()
            self.surface.blit(self.cursor_surface, (cursor_y_pos, 0))

        self.clock.tick()
        return False

    def get_surface(self):
        return self.surface

    def get_text(self):
        return self.input_string

    def get_cursor_position(self):
        return self.cursor_position

    def set_text_color(self, color):
        self.text_color = color

    def set_cursor_color(self, color):
        self.cursor_surface.fill(color)

    def clear_text(self):
        self.input_string = ""
        self.cursor_position = 0

def intro():
    intro = True
    textinput = TextInput()

    while intro:
        events = pygame.event.get()
        mouse = pygame.mouse.get_pos()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
            if screen_width/2-100 < mouse[0] < screen_width/2+100 and 465 < mouse[1] < 528 and event.type == pygame.MOUSEBUTTONDOWN:
                intro = False

        clock = pygame.time.Clock()
        screen.blit(intro_image, (0, 0))

        textinput.update(events)
        screen.blit(textinput.get_surface(), (int(screen_width/2 - textinput.get_surface().get_width() //2), 405))

        pygame.display.update()
        clock.tick(30)

    if len(textinput.get_text()) > 0:
        return textinput.get_text()
    else:
        return "Anonymous"

# creates the string that displays time
def get_time(hours,minutes,seconds):
    if len(str(hours)) > 1:
        h = str(hours)
    else:
        h = "0" + str(hours)

    if len(str(minutes)) > 1:
        m = str(minutes)
    else:
        m = "0" + str(minutes)

    if len(str(seconds)) > 1:
        s = str(seconds)
    else:
        s = "0" + str(seconds)

    return h + ":" + m + ":" + s

# creates rank time
def get_rank_time(t):
    hours = 0
    minutes = 0
    seconds = 0
    current_time = int(t)
    if current_time > 3600:
        while True:
            if current_time - 3600 > 0:
                hours += 1
                current_time -= 3600
            else:
                while True:
                    if current_time - 60 > 0:
                        minutes += 1
                        current_time -= 60
                    else:
                        seconds += int(current_time)
                        break
                break

    else:
        while True:
            if current_time - 60 > 0:
                minutes += 1
                current_time -= 60
            else:
                seconds += int(current_time)
                break

    return get_time(hours, minutes, seconds)

# creates the time counter
def draw_time(start_time,pause_time):
    hours = 0
    minutes = 0
    seconds = 0
    current_time = time.time() - pause_time - start_time
    rank_time = current_time
    if current_time > 3600:
        while True:
            if current_time - 3600 > 0:
                hours += 1
                current_time -= 3600
            else:
                while True:
                    if current_time - 60 > 0:
                        minutes += 1
                        current_time -= 60
                    else:
                        seconds += int(current_time)
                        break
                break

    else:
        while True:
            if current_time - 60 > 0:
                minutes += 1
                current_time -= 60
            else:
                seconds += int(current_time)
                break

    return [time_font.render(get_time(hours, minutes, seconds), True, white, color), get_time(hours, minutes, seconds), rank_time]

class cell:
    def __init__(self,up,down,left,right):
        self.visited = False
        self.walls = [up,down,left,right]

class prim_maze:
    # generates the maze
    def __init__(self):
        self.walls = []
        self.maze_walls = []
        self.cells = []

        x = 0
        y = 0

        # creates all cell within the maze
        for h in range(maze_height):
            for w in range(maze_width):
                # if command makes sure no cellls are created where the clock is supposed to be
                if not (h in (0, 1) and w > maze_width - 8):
                    self.cells.append(
                        cell((x + block_size, y, cell_size, block_size), (x + block_size, y + cell_size + block_size, cell_size, block_size), (x, y + block_size, block_size, cell_size), (x + cell_size + block_size, y + block_size, block_size, cell_size)))
                x += cell_size + block_size
            x = 0
            y += cell_size + block_size

        # generates maze using prim's algorithm
        for v in self.cells[0].walls:
            self.maze_walls.append(v)
            self.walls.append(v)

        self.cells[0].visited = True

        while len(self.walls) > 0:
            wall = random.choice(self.walls)
            # checks which cells are divided by the wall
            divided_cells = []
            for u in self.cells:
                if wall in u.walls:
                    divided_cells.append(u)

            if len(divided_cells) > 1 and (not ((divided_cells[0].visited and divided_cells[1].visited) or (
                    (not divided_cells[0].visited) and (not divided_cells[1].visited)))):
                # checks which cells have been visited
                for k in divided_cells:
                    k.walls.remove(wall)

                    if k.visited == False:
                        k.visited = True

                    for q in k.walls:
                        if not q in self.walls:
                            self.walls.append(q)

                        if not q in self.maze_walls:
                            self.maze_walls.append(q)

                    if wall in self.maze_walls:
                        self.maze_walls.remove(wall)

            self.walls.remove(wall)

        for j in range(0, screen_height, cell_size + block_size):
            for i in range(0, screen_width, cell_size + block_size):
                self.maze_walls.append((i, j, block_size, block_size))

    def draw(self):
        screen.fill(back_color)

        for k in self.maze_walls:
            pygame.draw.rect(screen, color, pygame.Rect(k[0], k[1], k[2], k[3]))

        pygame.draw.rect(screen, color, pygame.Rect(screen_width-block_size-(cell_size+block_size)*7, 0, (cell_size+block_size)*8+block_size,(cell_size+block_size)*2+block_size))  # clock background
        screen.blit(goal_image, goal)

def rank_print():
    rank = True

    screen.blit(rank_image, (0, 0))

    fin = open("rank.txt", 'r')
    while True:
        line = fin.readline()
        if not line or line == "\n": break
        temp = line.split()
        dict[temp[0]] = float(temp[1])
    fin.close()

    dict[user_id] = sum
    sdict = sorted(dict.items(), key=operator.itemgetter(1))

    data = ""
    fout = open("rank.txt", 'w')
    count = 0
    for i in sdict:
        count += 1
        if i[0] == user_id:
            rank = count
        temp = "%s %f\n" %(i[0], i[1])
        data += temp
    fout.write(data)
    fout.close()

    myrank = myrank_font.render(str(rank), True, color)
    screen.blit(myrank, (int(739 - myrank.get_width() //2), int(268 - myrank.get_height() //2)))

    rank1 = rank_font.render("1", True, color)
    screen.blit(rank1, (int(170 - rank1.get_width() // 2), int(478 - rank1.get_height() //2)))
    rank1_name = rank_font.render(sdict[0][0], True, color)
    screen.blit(rank1_name, (int(500 - rank1_name.get_width() //2), int(478 - rank1_name.get_height() //2)))
    rank1_time = rank_font.render(get_rank_time(sdict[0][1]), True, color)
    screen.blit(rank1_time, (810, int(478 - rank1_time.get_height() //2)))

    rank2 = rank_font.render("2", True, color)
    screen.blit(rank2, (int(170 - rank1.get_width() // 2), int(568 - rank1.get_height() // 2)))
    rank2_name = rank_font.render(sdict[1][0], True, color)
    screen.blit(rank2_name, (int(500 - rank2_name.get_width() // 2), int(568 - rank2_name.get_height() // 2)))
    rank2_time = rank_font.render(get_rank_time(sdict[1][1]), True, color)
    screen.blit(rank2_time, (810, int(568 - rank2_time.get_height() // 2)))

    rank3 = rank_font.render("3", True, color)
    screen.blit(rank3, (int(170 - rank1.get_width() // 2), int(658 - rank1.get_height() // 2)))
    rank3_name = rank_font.render(sdict[2][0], True, color)
    screen.blit(rank3_name, (int(500 - rank3_name.get_width() // 2), int(658 - rank3_name.get_height() // 2)))
    rank3_time = rank_font.render(get_rank_time(sdict[2][1]), True, color)
    screen.blit(rank3_time, (810, int(658 - rank3_time.get_height() // 2)))

    rank4 = rank_font.render("4", True, color)
    screen.blit(rank4, (int(170 - rank1.get_width() // 2), int(748 - rank1.get_height() // 2)))
    rank4_name = rank_font.render(sdict[3][0], True, color)
    screen.blit(rank4_name, (int(500 - rank4_name.get_width() // 2), int(748 - rank4_name.get_height() // 2)))
    rank4_time = rank_font.render(get_rank_time(sdict[3][1]), True, color)
    screen.blit(rank4_time, (810, int(748 - rank4_time.get_height() // 2)))

    rank5 = rank_font.render("5", True, color)
    screen.blit(rank5, (int(170 - rank1.get_width() // 2), int(838 - rank1.get_height() // 2)))
    rank5_name = rank_font.render(sdict[4][0], True, color)
    screen.blit(rank5_name, (int(500 - rank5_name.get_width() // 2), int(838 - rank5_name.get_height() // 2)))
    rank5_time = rank_font.render(get_rank_time(sdict[4][1]), True, color)
    screen.blit(rank5_time, (810, int(838 - rank5_time.get_height() // 2)))

    while rank:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                rank = False

        clock = pygame.time.Clock()

        pygame.display.update()
        clock.tick(30)

user_id = intro()
id = 0
running = True
while running:
    if id == 0:
        screen_width = 776
        screen_height = 584
        maze_width = 24
        maze_height = 18

    elif id == 1:
        screen_width = 968
        screen_height = 776
        maze_width = 30
        maze_height = 24

    elif id == 2:
        screen_width = 1160
        screen_height = 968
        maze_width = 36
        maze_height = 30

    elif id == 3:
        rank_print()
        break

    screen = pygame.display.set_mode((screen_width, screen_height))

    done = False
    x = 8
    y = 8
    clock = pygame.time.Clock()
    start = time.time()
    maze = prim_maze()
    # goal = pygame.Rect(40, 40, 24, 24)
    goal = pygame.Rect(screen_width - cell_size - block_size, screen_height - cell_size - block_size, cell_size, cell_size)
    victory = False
    speed = 3 # movement speed
    pause = False
    pause_time = 0 # time spent in pause menu
    pause_time_start = 0

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                    if pause:
                        pause = False
                        pause_time += time.time() - pause_time_start
                    else:
                        pause = True
                        pause_time_start = time.time()

                if event.key == pygame.K_RETURN:
                    done = True

        if pause:
            if id == 0:
                screen.blit(pause1_image, (0, 0))
            elif id == 1:
                screen.blit(pause2_image, (0, 0))
            elif id == 2:
                screen.blit(pause3_image, (0, 0))

        # the actual game
        if not victory and not pause:
            move_up = True
            move_down = True
            move_left = True
            move_right = True
            pressed = pygame.key.get_pressed()

            # movement
            if pressed[pygame.K_w] or pressed[pygame.K_UP]:
                # checks if their is a overlap with the wall
                for m in maze.maze_walls:
                    player = pygame.Rect(x, y - speed, player_size, player_size)
                    if player.colliderect(pygame.Rect(m[0],m[1],m[2],m[3])):
                        move_up = False
                        break
                if move_up:
                    y -= speed

            if pressed[pygame.K_s] or pressed[pygame.K_DOWN]:
                player = pygame.Rect(x, y + speed, player_size, player_size)
                for m in maze.maze_walls:
                    if player.colliderect(pygame.Rect(m[0],m[1],m[2],m[3])):
                        move_down = False
                        break
                if move_down:
                    y += speed

            if pressed[pygame.K_a] or pressed[pygame.K_LEFT]:
                player = pygame.Rect(x - speed, y, player_size, player_size)
                for m in maze.maze_walls:
                    if player.colliderect(pygame.Rect(m[0],m[1],m[2],m[3])):
                        move_left = False
                        break
                if move_left:
                    x -= speed

            if pressed[pygame.K_d] or pressed[pygame.K_RIGHT]:
                player = pygame.Rect(x + speed, y, player_size, player_size)
                for m in maze.maze_walls:
                    if player.colliderect(pygame.Rect(m[0],m[1],m[2],m[3])):
                        move_right = False
                        break
                if move_right:
                    x += speed

            # checks if player has reached the goal
            if goal.colliderect((x, y, player_size, player_size)):
                victory = True
                id += 1
                round_time = draw_time(start, pause_time)[2]
                sum += round_time

            # draws the screen
            maze.draw()
            screen.blit(player_image, (x, y))
            text = draw_time(start, pause_time)
            screen.blit(text[0], (int(screen_width-block_size/2-(cell_size+block_size)*3.5 - text[0].get_width() // 2), int((cell_size+block_size)+block_size/2 - text[0].get_height() // 2)))

        # victory screen
        if victory:
            if id == 1:
                screen.blit(round1_image, (0, 0))
                time_text = time_font.render("Time : " + text[1],True,color)
                reset = defalut_font.render("(Press Enter to Start Next Round)",True,color)

                screen.blit(time_text, (int(screen_width/2 - (time_text.get_width() // 2)), int((screen_height/2 - (time_text.get_height() // 2)) + 60)))
                screen.blit(reset, (int(screen_width/2 - (reset.get_width() // 2)), int((screen_height/2 - (reset.get_height() // 2)) + 60 + time_text.get_height())))

            if id == 2:
                screen.blit(round2_image, (0, 0))
                time_text = time_font.render("Time : " + text[1], True, color)
                reset = defalut_font.render("(Press Enter to Start Next Round)", True, color)

                screen.blit(time_text, (int(screen_width / 2 - (time_text.get_width() // 2)), int((screen_height / 2 - (time_text.get_height() // 2)) + 80)))
                screen.blit(reset, (int(screen_width / 2 - (reset.get_width() // 2)), int((screen_height / 2 - (reset.get_height() // 2)) + 80 + time_text.get_height())))

            if id == 3:
                screen.blit(round3_image, (0, 0))
                time_text = time_font.render("Time : " + text[1], True, color)
                reset = defalut_font.render("(Press Enter to Start Next Round)", True, color)

                screen.blit(time_text, (int(screen_width / 2 - (time_text.get_width() // 2)), int((screen_height / 2 - (time_text.get_height() // 2)) + 100)))
                screen.blit(reset, (int(screen_width / 2 - (reset.get_width() // 2)), int((screen_height / 2 - (reset.get_height() // 2)) + 100 + time_text.get_height())))

        clock.tick(60)
        pygame.display.flip()
