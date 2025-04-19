import pyxel

import pendulum

TIME_DURATION = 30  # Time duration in seconds

LENGTH_RANGE = (1.0, 10.0)  # Length of the pendulum strings in meters
WEIGHT_RANGE = (1.0, 10.0)  # Weight of the pendulum bob in kg
INIT_ANGLE_RANGE = (-3.14, 3.14)  # Initial angles of the pendulum bobs in radians
INIT_VELOCITY_RANGE = (-1.0, 1.0)  # Initial velocities of the pendulum bobs in m/s

def generate_pendulum(n):
    lengths = [pyxel.rndf(*LENGTH_RANGE) for _ in range(n)]
    weights = [pyxel.rndf(*WEIGHT_RANGE) for _ in range(n)]
    init_angles = [pyxel.rndf(*INIT_ANGLE_RANGE) for _ in range(n)]
    init_velocities = [pyxel.rndf(*INIT_VELOCITY_RANGE) for _ in range(n)]
    return pendulum.pendulum(
        lengths,
        weights,
        TIME_DURATION,
        init_angles,
        init_velocities
    )

class App:
    def __init__(self):
        pyxel.init(160, 120)
        self.i = 0

        self.result = generate_pendulum(3)
        self.count = len(self.result)
        self.di = 1
        pyxel.run(self.update, self.draw)

    def update(self):
        if pyxel.btnr(pyxel.KEY_UP):
            self.di += 1
        if pyxel.btnr(pyxel.KEY_DOWN):
            self.di -= 1
        if pyxel.btnr(pyxel.KEY_SPACE):
            self.result = generate_pendulum(3)
            self.count = len(self.result)
            self.i = 0
        self.i += self.di
        if self.i >= self.count:
            self.i = 0

    def draw(self):
        pyxel.cls(0)
        pendulum_positions = self.result[self.i]
        pyxel.circ(80, 60, 2, 7)
        for pos in pendulum_positions:
            pyxel.circ(pos[0] + 80, -pos[1] + 60, 2, 8)
        pyxel.text(10, 10, f"i: {self.i} / {self.count}", 7)


App()
