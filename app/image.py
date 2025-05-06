import pyxel


def load_images():
    TitleImage.load()
    StageClearImage.load()
    GameOverImage.load()
    GameClearImage.load()


class ImageBase:
    X = 0
    Y = 0
    W = 0
    H = 0
    file = ""
    image = None

    @classmethod
    def load(cls):
        cls.image = pyxel.Image(cls.W, cls.H)
        cls.image.load(0, 0, cls.file)

    @classmethod
    def draw(cls):
        pyxel.blt(cls.X, cls.Y, cls.image, 0, 0, cls.W, cls.H)

class TitleImage(ImageBase):
    X = 0
    Y = 16
    W = 160
    H = 32
    file = "assets/title.png"

class StageClearImage(ImageBase):
    X = 32
    Y = 24
    W = 96
    H = 16
    file = "assets/stageclear.png"

class GameOverImage(ImageBase):
    X = 32
    Y = 24
    W = 96
    H = 16
    file = "assets/gameover.png"

class GameClearImage(ImageBase):
    X = 0
    Y = 16
    W = 160
    H = 32
    file = "assets/gameclear.png"
