import pyxel

from enum import Enum

import pendulum
import image

WINDOW_W = 160
WINDOW_H = 120

FLOOR = WINDOW_H // 4 * 3


def center(text, width):
    TEXT_W = 4
    return width // 2 - len(text) * TEXT_W // 2


GRADATION = [0x2b335f, 0x3d4775, 0x4f5b8c, 0x616fa3, 0x7384ba, 0x8598d1, 0x97ace8, 0xa9c1ff]


class AfterImage:
    SIZE = 5
    COUNT = 20
    circles = [] # [(x, y, count)]

    @classmethod
    def add_circle(cls, x, y):
        cls.circles.append((x, y, cls.COUNT))
    
    @classmethod
    def clear(cls):
        cls.circles = []

    @classmethod
    def update(cls):
        cls.circles = [(x, y, count - 1) for x, y, count in cls.circles if count > 0]

    @classmethod
    def draw(cls, reverse=False):
        for circle in cls.circles:
            c = (len(GRADATION) - 1) * circle[2] // cls.COUNT
            if reverse:
                c = len(GRADATION) - 1 - c
            pyxel.circ(circle[0], circle[1], cls.SIZE, c)


class Pendulum:
    SIZE = 5

    TIME_DURATION = 30  # Time duration in seconds

    LENGTH_RANGE = (5.0, 30.0)  # Length of the pendulum strings in meters
    WEIGHT_RANGE = (1.0, 10.0)  # Weight of the pendulum bob in kg
    # Initial angles of the pendulum bobs in radians
    INIT_ANGLE_RANGE = (-3.14, 3.14)
    # Initial velocities of the pendulum bobs in m/s
    INIT_VELOCITY_RANGE = (-1.0, 1.0)

    def __init__(self, n, cx, cy, flame):
        lengths = [pyxel.rndf(*self.LENGTH_RANGE) for _ in range(n)]
        weights = [pyxel.rndf(*self.WEIGHT_RANGE) for _ in range(n)]
        init_angles = [pyxel.rndf(*self.INIT_ANGLE_RANGE) for _ in range(n)]
        init_velocities = [pyxel.rndf(*self.INIT_VELOCITY_RANGE) for _ in range(n)]
        p = pendulum.PendulumSolver(
            lengths,
            weights,
            self.TIME_DURATION,
            init_angles,
            init_velocities
        )
        self.result = p.solve(flame)
        self.center = (cx, cy)
        self.update(0)

    def update(self, i):
        self.positions = [self.center]
        for pos in self.result[i]:
            x = pos[0] + self.center[0]
            y = -pos[1] + self.center[1]
            self.positions.append((int(x), int(y)))
        self.tip_pos = self.positions[-1]
        if i % 4 == 0:
            AfterImage.add_circle(*self.tip_pos)

    def tip_position(self):
        return self.tip_pos

    def draw(self, reverse=False):
        c1, c2 = 0, 7
        if reverse:
            c1, c2 = 7, 7
        for s, t in zip(self.positions[:-1], self.positions[1:]):
            pyxel.line(s[0], s[1], t[0], t[1], c2)
        for p in self.positions[:-1]:
            pyxel.circ(p[0], p[1], self.SIZE, c1)
            pyxel.circb(p[0], p[1], self.SIZE, c2)
    
    def draw_tip(self, reverse=False):
        c = 7
        if reverse:
            c = 0
        pyxel.circ(self.tip_pos[0], self.tip_pos[1], self.SIZE, c)


class StartPoint:
    W = 12
    H = 12
    X = WINDOW_W // 8
    Y = FLOOR - H
    COLOR = 11

    @classmethod
    def draw(cls):
        pyxel.rect(cls.X, cls.Y, cls.W, cls.H, cls.COLOR)

class Apple:
    R = 4
    COLOR = 8

    X_RANGE = (WINDOW_W // 4, WINDOW_W)
    Y_RANGE = (FLOOR - 50, FLOOR)

    NUM_PRE_STAGE = 3

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.collected = False

    def draw(self): 
        pyxel.circ(self.x, self.y, self.R, self.COLOR)

    @classmethod
    def generate(cls):
        x = pyxel.rndi(*cls.X_RANGE)
        y = pyxel.rndi(*cls.Y_RANGE)
        return cls(x, y)


class CharacterStatus(Enum):
    NONE = 0
    JUMP = 1
    START = 2
    DEAD = 3
    RE_SPAWN = 4

class Character:
    W = 10
    H = 10
    MAX_X_VELOCITY = 2
    MAX_Y_VELOCITY = 8
    SPEED = 1
    JUMP = 6

    JUMP_COUNT = 5
    JUMP_CHARGE_COUNT = 2

    START_COUNT = 2
    DEAD_COUNT = 4
    RE_SPAWN_COUNT = 4

    COLOR = 10

    def __init__(self):
        self.reset()

    def reset(self):
        self.x = StartPoint.X + StartPoint.W // 2 - self.W // 2
        self.y = StartPoint.Y + StartPoint.H // 2 - self.H // 2
        self.vx = 0
        self.vy = 0
        self.count = self.START_COUNT
        self.status = CharacterStatus.START
        self.double_jumped = False
    
    def dead(self):
        self.vx = 0
        self.vy = 0
        self.status = CharacterStatus.DEAD
        self.count = self.DEAD_COUNT
    
    def is_dead(self):
        return self.status == CharacterStatus.DEAD
    
    def re_spawn(self):
        self.x = StartPoint.X + StartPoint.W // 2 - self.W // 2
        self.y = StartPoint.Y + StartPoint.H // 2 - self.H // 2
        self.vx = 0
        self.vy = 0
        self.status = CharacterStatus.RE_SPAWN
        self.count = self.RE_SPAWN_COUNT

    def update(self):
        if self.count > 0:
            self.count -= 1
        if self.count == 0:
            if self.status == CharacterStatus.DEAD:
                self.re_spawn()
            else:
                self.status = CharacterStatus.NONE
        if self.on_floor():
            self.double_jumped = False

        self.x += self.vx
        self.y += self.vy
        self.x_limit()

        match self.status:
            case CharacterStatus.NONE:
                self.update_none()
            case CharacterStatus.JUMP:
                self.update_jump()
            case CharacterStatus.START:
                self.update_start()
            case CharacterStatus.DEAD:
                self.update_dead()
            case CharacterStatus.RE_SPAWN:
                self.update_re_spawn()

    def update_none(self):
        self.gravity()
        self.move_x()
        self.speed_limit()
        if self.pushed_jump_button():
            if self.on_floor():
                self.vy = -self.JUMP
                self.status = CharacterStatus.JUMP
                self.count = self.JUMP_COUNT
            elif not self.double_jumped:
                self.vy = -self.JUMP
                self.status = CharacterStatus.JUMP
                self.count = self.JUMP_COUNT
                self.double_jumped = True

    def update_jump(self):
        self.gravity()
        self.move_x()
        self.speed_limit()

    def update_start(self):
        pass

    def update_dead(self):
        pass

    def update_re_spawn(self):
        pass

    def on_floor(self):
        if self.y + self.H >= FLOOR:
            return True
        return False

    # Applies gravity to the character.
    def gravity(self):
        if self.on_floor():
            self.vy = 0
            self.y = FLOOR - self.H
        else:
            self.vy += 1

    # Moves the character left or right based on button presses.
    def move_x(self):
        vx = 0
        if self.pushed_right_button():
            vx += self.SPEED
        if self.pushed_left_button():
            vx -= self.SPEED
        if vx == 0:
            if self.vx > 0:
                self.vx -= 1
            elif self.vx < 0:
                self.vx += 1
        else:
            self.vx += vx

    # Clamps the horizontal (vx) and vertical (vy) velocities to ensure they
    # do not exceed the defined maximum limits for smooth character movement.
    def speed_limit(self):
        self.vx = min(max(self.vx, -self.MAX_X_VELOCITY), self.MAX_X_VELOCITY)
        self.vy = min(max(self.vy, -self.MAX_Y_VELOCITY), self.MAX_Y_VELOCITY)

    def x_limit(self):
        self.x = min(max(self.x, 0), WINDOW_W - self.W)

    # Checks if the jump button is pressed (W, SPACE, or UP arrow keys)
    def pushed_jump_button(self):
        return pyxel.btnp(pyxel.KEY_W) or pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.KEY_UP)

    # Checks if the left button is pressed (A or LEFT arrow keys)
    def pushed_left_button(self):
        return pyxel.btn(pyxel.KEY_A) or pyxel.btn(pyxel.KEY_LEFT)

    # Checks if the right button is pressed (D or RIGHT arrow keys)
    def pushed_right_button(self):
        return pyxel.btn(pyxel.KEY_D) or pyxel.btn(pyxel.KEY_RIGHT)

    def collision_to_apple(self, apple: Apple):
        px, py = self.x + self.W // 2, self.y + self.H // 2
        distance = ((px - apple.x) ** 2 + (py - apple.y) ** 2)
        if distance < (self.W // 2 + apple.R) ** 2:
            return True
        return False

    def collision_to_startpoint(self):
        if (self.x < StartPoint.X + StartPoint.W and
            self.x + self.W > StartPoint.X and
            self.y < StartPoint.Y + StartPoint.H and
            self.y + self.H > StartPoint.Y):
            return True
        return False

    def collision_to_pendulum(self, x, y):
        px, py = self.x + self.W // 2, self.y + self.H // 2
        distance = ((px - x) ** 2 + (py - y) ** 2)
        if distance < (self.W // 2 + Pendulum.SIZE) ** 2:
            return True
        return False

    def draw(self):
        dx, dy = 0, 0
        if self.status == CharacterStatus.JUMP:
            if self.JUMP - self.count < self.JUMP_CHARGE_COUNT:
                dx, dy = -1, 1
            elif self.JUMP - self.count > self.JUMP_CHARGE_COUNT:
                dx, dy = 1, -1
        if self.status == CharacterStatus.DEAD:
            scale = self.DEAD_COUNT - self.count
            dx = dy = scale
        if self.status == CharacterStatus.RE_SPAWN:
            scale = self.count
            dx = dy = scale
        pyxel.rect(self.x + dx, self.y + dy, self.W - 2*dx, self.H - 2*dy, self.COLOR)


class Stage:
    MAX_N_PENDULUM = 5
    PENDULUM_CENTERS = (
        (WINDOW_W // 2, WINDOW_H // 3),
        (WINDOW_W // 4 * 3, WINDOW_H // 4),
        (WINDOW_W // 4, WINDOW_H // 4),
        (WINDOW_W // 8 * 3, WINDOW_H // 6),
        (WINDOW_W // 8 * 5, WINDOW_H // 6),
    )
    INCREASE_PENDULUM_STAGE = 10
    PENDULUM_RANGE = (2, 5)

    FLAME = 600

    @classmethod
    def generate(cls, level):
        pendulum_num = min(cls.MAX_N_PENDULUM, level // cls.INCREASE_PENDULUM_STAGE + 1)
        pendulums = []
        for i in range(pendulum_num):
            cx, cy = cls.PENDULUM_CENTERS[i]
            n = pyxel.rndi(*cls.PENDULUM_RANGE)
            pendulum = Pendulum(n, cx, cy, cls.FLAME)
            pendulums.append(pendulum)
        apples = [Apple.generate() for _ in range(Apple.NUM_PRE_STAGE)]

        return pendulums, apples

    @classmethod
    def clear(cls, apples):
        return all(apple.collected for apple in apples)

    @classmethod
    def reset(cls, apples):
        for apple in apples:
            apple.collected = False


class GameState(Enum):
    MAIN_MENU = 0
    READY_STAGE = 1
    NEXT_STAGE = 2
    PLAYING = 3
    GAME_OVER = 4


class Button:
    W = 60
    H = 10

    def __init__(self, x, y, message):
        self.x = x
        self.y = y
        self.message = message

    def draw(self, selected):
        if selected:
            c = 10
        else:
            c = 13
        pyxel.rectb(self.x, self.y, self.W, self.H, c)
        pyxel.text(self.x + center(self.message, self.W), self.y + self.H // 2 - 3, self.message, c)

class UIBase:
    buttons = []
    selected_index = 0

    @classmethod
    def reset(cls):
        cls.selected_index = 0

    @classmethod
    def update(cls):
        if pyxel.btnp(pyxel.KEY_D):
            cls.selected_index = (cls.selected_index - 1) % len(cls.buttons)
        elif pyxel.btnp(pyxel.KEY_A):
            cls.selected_index = (cls.selected_index + 1) % len(cls.buttons)
    
    @classmethod
    def draw(cls):
        for i, button in enumerate(cls.buttons):
            button.draw(i==cls.selected_index)


class MainMenuUI(UIBase):
    start_button = Button(WINDOW_W // 2 - Button.W // 2, WINDOW_H // 4 * 3 - Button.H // 2, "Start")
    buttons = [start_button]

    @classmethod
    def update(cls):
        super().update()
        if pyxel.btnp(pyxel.KEY_SPACE):
            match cls.buttons[cls.selected_index]:
                case cls.start_button:
                    return GameState.PLAYING

    @classmethod
    def draw(cls):
        super().draw()
        image.TitleImage.draw()


class ReadyStageUI(UIBase):
    @classmethod
    def update(cls):
        return GameState.NEXT_STAGE

    @classmethod
    def draw(cls):
        image.StageClearImage.draw()
        s = "Now loading..."
        pyxel.text(center(s, WINDOW_W), WINDOW_H//2, s, 13)


class NextStageUI(UIBase):
    next_button = Button(WINDOW_W // 2 - Button.W // 2, WINDOW_H // 2 - Button.H // 2, "Next Stage")
    buttons = [next_button]

    @classmethod
    def update(cls):
        super().update()
        if pyxel.btnp(pyxel.KEY_SPACE):
            match cls.buttons[cls.selected_index]:
                case cls.next_button:
                    return GameState.PLAYING

    @classmethod
    def draw(cls, level):
        super().draw()
        image.StageClearImage.draw()
        s = f"Next Stage : Level{level}"
        pyxel.text(center(s, WINDOW_W), WINDOW_H//4 * 3, s, 13)


class GameOverUI(UIBase):
    retry_button = Button(WINDOW_W // 2 - Button.W // 2, WINDOW_H // 2 - Button.H // 2, "Retry Stage")
    main_menu_button = Button(WINDOW_W // 2 - Button.W // 2, WINDOW_H // 2 + Button.H, "Main Menu")
    buttons = [retry_button, main_menu_button]

    @classmethod
    def update(cls):
        super().update()
        if pyxel.btnp(pyxel.KEY_SPACE):
            match cls.buttons[cls.selected_index]:
                case cls.retry_button:
                    return GameState.PLAYING
                case cls.main_menu_button:
                    return GameState.MAIN_MENU
 
    @classmethod
    def draw(cls):
        super().draw()
        image.GameOverImage.draw()


class App:
    def __init__(self):
        pyxel.init(WINDOW_W, WINDOW_H)
        for i, c in enumerate(GRADATION):
            pyxel.colors[i] = c

        image.load_images()

        self.initialize()
        pyxel.run(self.update, self.draw)
    
    def initialize(self):
        self.level = 0
        self.pendulums = []
        self.apples = []
        self.character = Character()
        self.count = 0
        self.status = GameState.MAIN_MENU
        AfterImage.clear()
        MainMenuUI.reset()
        ReadyStageUI.reset()
        NextStageUI.reset()
        GameOverUI.reset()

    def update(self):
        match self.status:
            case GameState.MAIN_MENU:
                state = MainMenuUI.update()
                if state:
                    self.status = state
                    self.set_next_stage()
            case GameState.READY_STAGE:
                state = ReadyStageUI.update()
                if state:
                    self.status = state
                    self.set_next_stage()
            case GameState.NEXT_STAGE:
                state = NextStageUI.update()
                if state:
                    self.status = state
            case GameState.PLAYING:
                self.count += 1
                if self.count >= Stage.FLAME:
                    self.game_over()
                    self.status = GameState.GAME_OVER
                    return

                for pendulum in self.pendulums:
                    pendulum.update(self.count)
                self.character.update()
                AfterImage.update()
                if not self.character.collision_to_startpoint():
                    for pendulum in self.pendulums:
                        if self.character.collision_to_pendulum(*pendulum.tip_position()) and not self.character.is_dead():
                            self.character.dead()
                            self.restart()
                for apple in self.apples:
                    if self.character.collision_to_apple(apple) and not self.character.is_dead():
                        apple.collected = True
                
                if self.character.collision_to_startpoint():
                    if Stage.clear(self.apples):
                        self.status = GameState.READY_STAGE
            case GameState.GAME_OVER:
                state = GameOverUI.update()
                if state:
                    if state == GameState.PLAYING:
                        self.status = state
                    if state == GameState.MAIN_MENU:
                        self.status = state
                        self.initialize()

    def set_next_stage(self):
        self.level += 1
        self.pendulums, self.apples = Stage.generate(self.level)
        self.character.reset()
        self.count = 0
        AfterImage.clear()

    def restart(self):
        Stage.reset(self.apples)
    
    def game_over(self):
        self.count = 0
        self.character.reset()
        Stage.reset(self.apples)
        AfterImage.clear()

    def draw(self):
        pyxel.cls(0)
        match self.status:
            case GameState.MAIN_MENU:
                MainMenuUI.draw()
            case GameState.READY_STAGE:
                ReadyStageUI.draw()
            case GameState.NEXT_STAGE:
                NextStageUI.draw(self.level)
            case GameState.PLAYING:
                draw_split = WINDOW_H * self.count // Stage.FLAME

                pyxel.clip(0, 0, WINDOW_W, draw_split)
                pyxel.rect(0, 0, WINDOW_W, draw_split, 0)
                for pendulum in self.pendulums:
                    pendulum.draw()
                AfterImage.draw()
                for pendulum in self.pendulums:
                    pendulum.draw_tip()

                pyxel.clip(0, draw_split, WINDOW_W, WINDOW_H - draw_split)
                pyxel.rect(0, draw_split, WINDOW_W, WINDOW_H - draw_split, 7)
                for pendulum in self.pendulums:
                    pendulum.draw(reverse=True)
                AfterImage.draw(reverse=True)
                for pendulum in self.pendulums:
                    pendulum.draw_tip(reverse=True)

                pyxel.clip()
                StartPoint.draw()
                for apple in self.apples:
                    if apple.collected:
                        continue
                    apple.draw()
                self.character.draw()

                pyxel.line(0, FLOOR, WINDOW_W, FLOOR, 9)
            case GameState.GAME_OVER:
                GameOverUI.draw()


App()
