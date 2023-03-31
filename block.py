from time import time

from utility.printable import Printable

class Block(Printable):
    def __init__(self, index, previous_hash, transactions,difficulty,nonce, time=time()):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = time
        self.transactions = transactions
        self.nonce = nonce
        self.difficulty = difficulty
