from functools import reduce
import json
# import pickle

from utility.hash_util import hash_block
from utility.verification import Verification
from block import Block
from transaction import Transaction
from wallet import Wallet

MINING_REWARD = 10.0  # 挖矿奖励

"""在类中，双下划线 + 变量名 表示这个变量是 private 类型的, 如: __chain"""
class Blockchain:
    def __init__(self, hosting_node_id):
        genesis_block = Block(0, '', [], 100, 0) # 创世块
        self.chain = [genesis_block]  # 初始化 blockchain
        self.__open_transactions = []  # 交易池
        self.__peer_nodes = set()
        self.load_data()
        self.hosting_node = hosting_node_id

    """property装饰器用来创建*只读属性*, 会将方法转换为相同名称的*只读属性*, 可以与所定义的属性配合使用, 这样可以防止属性被修改"""    
    @property
    def chain(self):
        return self.__chain[:]

    # 当不想让用户可以直接修改 self.chain 的时候，可以把 chain 定义为 property
    # 用来控制可读和可写
    # 当给 self.chain 赋值的时候就相当于给 self.__chain 赋值
    @chain.setter
    def chain(self, val):
        self.__chain = val

    def get_open_transactions(self):
        return self.__open_transactions[:]

    # 加载区块链数据
    def load_data(self):
        """ 1. mode 'rb' read the binary data
            2. use pickle to read and write data is better than using json
            3. because using json to load data may occur some order problem
        """
        try:
            with open('blockchain.txt', mode='r') as f:
                file_content = f.readlines()
                # file_content = pickle.loads(f.read())

                # blockchain = file_content['chain']
                # open_transactions = file_content['ot']
                # if not file_content:
                #     return
                blockchain = json.loads(file_content[0][:-1]) # 加[:-1]是为了去掉结尾的 \n
                updated_blockchain = []
                for block in blockchain:
                    converted_tx = [Transaction(tx['sender'], tx['recipient'], tx['signature'], tx['amount']) for tx in block['transactions']]
                    updated_block = Block(
                        block['index'],
                        block['previous_hash'],
                        converted_tx,
                        block['proof'],
                        block['timestamp']
                    )
                    updated_blockchain.append(updated_block)
                
                # 存储变量，这里因为涉及到 setter，而其他地方都是 getter
                # self.chain 赋值等于给 self.__chain 赋值
                # 因此其他地方，读取 chain 的时候，仍然使用 self.__chain
                self.chain = updated_blockchain

                open_transactions = json.loads(file_content[1][:-1]) # 加[:-1]是为了去掉结尾的 \n
                updated_open_transactions = []
                for tx in open_transactions:
                    updated_transaction = Transaction(tx['sender'], tx['recipient'], tx['signature'], tx['amount'])
                    updated_open_transactions.append(updated_transaction)
                self.__open_transactions = updated_open_transactions
                
                peer_nodes = json.loads(file_content[2])
                self.__peer_nodes = set(peer_nodes)
        except (IOError, IndexError): # 处理文件为空的问题
            print('Handled exception...')
        finally:
            print('Cleanup!')

    # 将交易保存到本地文件中
    def save_data(self):
        """ 1. mode 'wb' for wirting binary data to files
            2. use pickle to dumps binary data
        """
        try:
            with open('blockchain.txt', mode='w') as f:
                # 因为 block 是 Block 类的对象，不可以直接使用 json.dumps 来转化为 String 类型
                # 所以需要将 blockchian 列表里面的所有 block 对象转化为 dict，使用 block.__dict__
                saveable_chain = [block.__dict__
                                for block in [Block(block_el.index, block_el.previous_hash, [tx.__dict__ for tx in block_el.transactions], block_el.proof, block_el.timestamp)
                                                for block_el in self.__chain]]
                saveable_tx = [tx.__dict__ for tx in self.__open_transactions]

                f.write(json.dumps(saveable_chain))
                f.write('\n')
                f.write(json.dumps(saveable_tx))
                f.write('\n')
                f.write(json.dumps(list(self.__peer_nodes)))
                # save_data = {
                #     'chain': blockchain,
                #     'ot': open_transactions
                # }
                # f.write(pickle.dumps(save_data))
        except IOError:
            print('Saving failed!')

    # 工作量证明 Proof-of-work
    def proof_of_work(self):
        last_block = self.__chain[-1]
        last_hash = hash_block(last_block)
        proof = 0

        while not Verification.valid_proof(self.__open_transactions, last_hash, proof):
            proof +=1
        return proof

    # 计算用户的余额
    def get_balance(self):
        if self.hosting_node == None:
            return None

        participant = self.hosting_node

        # 获得过往交易中用户发送出去的所有金额记录
        tx_sender = [[tx.amount
                    for tx in block.transactions if tx.sender == participant] for block in self.__chain]
        # 获得在交易池中用户发出去的金额记录
        open_tx_sender = [tx.amount
                        for tx in self.__open_transactions if tx.sender == participant]
        tx_sender.append(open_tx_sender)
        print(tx_sender, 'tx_sender')

        amount_sent = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt), tx_sender, 0) # 简化版

        # 获得过往交易中用户总共得到的数量
        tx_recipient = [[tx.amount
                        for tx in block.transactions if tx.recipient == participant] for block in self.__chain]
        amount_received = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt), tx_recipient, 0) # 简化版
        print(tx_recipient, 'tx_recipient')

        return amount_received - amount_sent  # 获得 - 送出去 = 余额

    # 获取最后一个区块
    def get_last_blockchain_value(self):
        """ Returns the last value of the current blockchian. """
        if len(self.__chain) < 1:
            return None
        return self.__chain[-1]

    # 新增交易
    def add_transaction(self, recipient, sender, signature, amount=1.0):
        """
        Arguments:
            :sender: The sender of the coins.
            :recipient: The recipient of the coins.
            :amont: The amount of coins sent with the transaction (default=1.0)
        """
        if self.hosting_node == None:
            return
        transaction = Transaction(sender, recipient, signature, amount)

        if Verification.verify_transaction(transaction, self.get_balance):
            self.__open_transactions.append(transaction)
            self.save_data()
            return True
        return False

    # 挖矿
    def mine_block(self):
        """Create a new block and add open transactions to it."""
        if self.hosting_node == None:
            return None

        last_block = self.__chain[-1]
        hashed_block = hash_block(last_block)  # 计算上一个块的 hash 值
        proof = self.proof_of_work() # PoW只针对 open_transactions 里的交易，不包括系统奖励的交易

        reward_transaction = Transaction('MINING', self.hosting_node, '', MINING_REWARD) # 系统奖励

        copied_transactions = self.__open_transactions[:]  # 复制交易池记录（未加入奖励交易之前的）（深拷贝！）
        for tx in copied_transactions: # 验证签名
            if not Wallet.verify_transaction(tx):
                return None
        
        copied_transactions.append(reward_transaction) # 将系统奖励的coins加进去
        block = Block(  # 创建新块
            len(self.__chain),
            hashed_block,
            copied_transactions, proof
        )

        # 加入新块
        self.__chain.append(block)
        self.__open_transactions = []
        self.save_data()
        return block
    
    # 新增节点
    def add_peer_node(self, node):
        """Adds a new node to the peer node set"""
        self.__peer_nodes.add(node)
        self.save_data()

    # 删除节点
    def remove_peer_node(self, node):
        self.__peer_nodes.discard(node)
        self.save_data() 

    def get_peer_nodes(self):
        return list(self.__peer_nodes)
