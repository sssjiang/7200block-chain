from utility.hash_util import hash_block, hash_string_256
from wallet import Wallet

class Verification:
    # 工作量证明 Proof-of-work
    # SHA256(交易记录 + 上一个块的hash值 + 随机数)
    @staticmethod
    def valid_proof(transactions, last_hash, proof):
        # 因为 transactions 里面放的都是 tx 对象
        # Transaction 类里面定义了 to_ordered_dict 方法
        # 调用对象的方法 to_ordered_dict() 转换为 OrderedDict
        guess = (str([tx.to_ordered_dict() for tx in transactions]) + str(last_hash) + str(proof)).encode()
        guess_hash = hash_string_256(guess)
        # print(guess_hash)
        return guess_hash[0:2] == '00'

    # 验证区块中的 hash 值
    @classmethod
    def verify_chain(cls, blockchain):
        # block_index = 0
        for (index, block) in enumerate(blockchain):
            if index == 0:
                continue
            if block.previous_hash != hash_block(blockchain[index - 1]):
                return False

            # block['transactions'][1:] 这样写是因为我把系统奖励的交易放在了第0个，要排除掉系统奖励的交易，因此从下标1开始
            if not cls.valid_proof(block.transactions[:-1], block.previous_hash, block.proof):
                print('Proof of work is invalid')
                return False
        return True

    # 校验交易
    @staticmethod
    def verify_transaction(transaction, get_balance, check_funds=True):
        if check_funds:
            sender_balance = get_balance(transaction.sender)
            return sender_balance >= transaction.amount and Wallet.verify_transaction(transaction)  # 检验发送方的余额是否多于本次交易的金额
        else:
            return Wallet.verify_transaction(transaction)

    # 校验交易列表
    @classmethod
    def verify_transactions(cls, open_transactions, get_balance):
        # all 的作用就是检验列表中的值是否都为 True
        return all([cls.verify_transaction(tx, get_balance, False) for tx in open_transactions])

