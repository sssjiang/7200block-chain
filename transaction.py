from collections import OrderedDict

class Transaction:
    def __init__(self, sender, recipient, amount):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
    
    def to_ordered_dict(self):
        # 用 python 内置的 OrderedDict 库创建排好序的字典
        # 可以避免转换为字符串之后，做各种验证时因为顺序问题而导致的验证失败问题
        return OrderedDict([
            ('sender', self.sender),
            ('recipient', self.recipient),
            ('amount', self.amount)
        ])