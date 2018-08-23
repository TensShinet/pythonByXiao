import time
from models import Model
from models.monmod import Monmod

class Board(Model):
    def __init__(self, form):
        self.id = None
        self.title = form.get('title', '')
        self.ct = int(time.time())
        self.ut = self.ct
        self.board_id = None


class Board(Monmod):
    __fields__ = Monmod.__fields__ + [
        ('title', str, ''),
        ('board_id', int, -1),
    ]