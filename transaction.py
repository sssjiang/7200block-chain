from collections import OrderedDict
from utility.printable import Printable

class Transaction(Printable):
    """A transaction which can be added to a block in the blockchain
    
    Attributes:
        :sender: The sender of the coins
        :recipient: The recipient of the coins
        :signature: The signature of the transaction
        :amount: The amount of coins sent
    """
    def __init__(self, sender, recipient, signature, amount):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.signature = signature
    
    def to_ordered_dict(self):
        # 用 python 内置的 OrderedDict 库创建排好序的字典
        # 可以避免转换为字符串之后，做各种验证时因为顺序问题而导致的验证失败问题
        return OrderedDict([
            ('sender', self.sender),
            ('recipient', self.recipient),
            ('amount', self.amount)
        ])