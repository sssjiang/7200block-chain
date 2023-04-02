from functools import reduce
import json
import requests
from time import time
# import pickle
from time import sleep
from utility.hash_util import hash_block
from utility.verification import Verification
from block import Block
from transaction import Transaction
from wallet import Wallet
from merkletools import MerkleTools

MINING_REWARD = 50.0  # 挖矿奖励
 

"""在类中，双下划线 + 变量名 表示这个变量是 private 类型的, 如: __chain"""    

class Blockchain:
    def __init__(self, publick_key, node_id):
        genesis_block = Block(index=0, previous_hash='', transactions=[],difficulty=2,nonce=100)
        self.chain = [genesis_block]  # 初始化 blockchain
        self.__open_transactions = []  # 交易池
        self.public_key = publick_key
        self.__peer_nodes = set()
        self.node_id = node_id
        self.resolve_conflicts = False
        self.load_data()

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
            with open('blockchain-{}.txt'.format(self.node_id), mode='r') as f:
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
                        index=block['index'],
                        previous_hash=block['previous_hash'],
                        transactions=converted_tx,
                        nonce=block['nonce'],
                        time=block['timestamp'],
                        difficulty=block['difficulty'],
                        merkle_root=block['merkle_root']
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
            with open('blockchain-{}.txt'.format(self.node_id), mode='w') as f:
                # 因为 block 是 Block 类的对象，不可以直接使用 json.dumps 来转化为 String 类型
                # 所以需要将 blockchian 列表里面的所有 block 对象转化为 dict，使用 block.__dict__
                saveable_chain = [block.__dict__
                                for block in [Block(index=block_el.index, previous_hash=block_el.previous_hash, transactions=[tx.__dict__ for tx in block_el.transactions], nonce=block_el.nonce, time=block_el.timestamp, difficulty=block_el.difficulty, merkle_root=block_el.merkle_root)
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
    def proof_of_work(self,difficulty,timestamp):
        difficulty = difficulty
        last_block = self.__chain[-1]
        last_hash = hash_block(last_block)
        nonce = 0

        while not Verification.valid_proof(index=self.chain[-1].index + 1,
                                           last_hash=last_hash,
                                           timestamp=timestamp,
                                           transactions=self.__open_transactions,
                                           nonce=nonce,
                                           difficulty=difficulty):
            nonce += 1
        return nonce

    # 计算用户的余额
    def get_balance(self, sender=None):
        if sender == None:
            if self.public_key == None:
                return None

            participant = self.public_key
        else:
            participant = sender

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
    def add_transaction(self, recipient, sender, signature, amount=1.0, is_receiving=False):
        """
        Arguments:
            :sender: The sender of the coins.
            :recipient: The recipient of the coins.
            :amont: The amount of coins sent with the transaction (default=1.0)
        """
        # if self.public_key == None:
        #     return False
        transaction = Transaction(sender, recipient, signature, amount)
        if Verification.verify_transaction(transaction, self.get_balance):
            self.__open_transactions.append(transaction)
            self.save_data()
            
            if not is_receiving:
                # 广播交易
                for node in self.__peer_nodes:
                    url = 'http://{}/broadcast-transaction'.format(node)
                    try:
                        response = requests.post(url, json={'sender': sender, 'recipient': recipient, 'amount': amount, 'signature': signature})
                        if response.status_code == 400 or response.status_code == 500:
                            print('Transaction declined, needs resolving')
                            return False
                    except requests.exceptions.ConnectionError:
                        continue
            return True
        return False

    # 挖矿

    def adjust_difficulty(self,last_block):
        # 挖矿难度系数
        starttime=time()
        sleep(0.2)
        endtime=time()
        MINE_RATE =(endtime-starttime)*10  # 每 2 秒挖一个区块 
        #MINE_RATE = 10 # seconds
        #根据历史区块的时间戳和当前时间戳计算出来的时间差（历史区块最多为5个）
        total_time=last_block.timestamp-self.__chain[-5].timestamp
        #如果时间差的平均值小于MINE_RATE，说明挖矿速度过快，难度增加
        ave=total_time/5
        result=int(last_block.difficulty*MINE_RATE/ave)
        #如果难度小于1，就返回1
        if result < 1:
            result=1
        elif result > 5:
            result=5
        return result
    def merkle_root(self,copied_transactions):
        #计算merkle_root
        txs = [tx.to_ordered_dict() for tx in copied_transactions]
         # Convert transactions to bytes strings
        txs_encoded = [json.dumps(tx).encode() for tx in txs]
         # Decode bytes strings to regular strings
        txs_decoded = [tx.decode() for tx in txs_encoded]
        tree = MerkleTools(hash_type='sha256')
        tree.add_leaf(txs_decoded, True)
        tree.make_tree()
        return tree.get_merkle_root()

    def mine_block(self):
        """Create a new block and add open transactions to it."""
        if self.public_key == None:
            return None

        last_block = self.__chain[-1]
        hashed_block = hash_block(last_block)  # 计算上一个块的 hash 值
        timestamp = time()
        #每五个块调节一次diffculty
        if len(self.__chain) % 5 == 0:
            difficulty = self.adjust_difficulty(last_block)
        else:
            difficulty = last_block.difficulty
        print(difficulty,'difficulty')
        nonce = self.proof_of_work(difficulty,timestamp) # PoW只针对 open_transactions 里的交易，不包括系统奖励的交易

        reward_transaction = Transaction('MINING', self.public_key, '', MINING_REWARD) # 系统奖励

        copied_transactions = self.__open_transactions[:]  # 复制交易池记录（未加入奖励交易之前的）（深拷贝！）
        for tx in copied_transactions: # 验证签名
            if not Wallet.verify_transaction(tx):
                return None
        
        copied_transactions.append(reward_transaction) # 将系统奖励的coins加进去
        block = Block(  # 创建新块
            index=len(self.__chain),
            previous_hash=hashed_block,
            transactions=copied_transactions,
            nonce=nonce,
            time=timestamp,
            difficulty=difficulty,
            merkle_root=self.merkle_root(copied_transactions)
        )

        # 加入新块
        self.__chain.append(block)
        self.__open_transactions = []
        self.save_data()

        # 挖矿成功后进行广播
        for node in self.__peer_nodes:
            url = 'http://{}/broadcast-block'.format(node)
            converted_block = block.__dict__.copy()
            converted_block['transactions'] = [tx.__dict__ for tx in converted_block['transactions']]
            try:
                response = requests.post(url, json={'block': converted_block})
                if response.status_code == 400 or response.status_code == 500:
                    print('Block declined, needs resolving')
                if response.status_code == 409:
                    self.resolve_conflicts = True
            except requests.exceptions.ConnectionError:
                continue
            
        return block

    # 收到其他节点的广播，进行加块处理
    def add_block(self, block):
        transactions = [Transaction(tx['sender'], tx['recipient'], tx['signature'], tx['amount']) for tx in block['transactions']]
        # print(block, 'bbbbbbbbbb')
        proof_is_valid = Verification.valid_proof(index=block['index'],
                                                  last_hash=block['previous_hash'],
                                                  timestamp=block['timestamp'],
                                                  transactions=transactions[:-1],
                                                  nonce=block['nonce'],
                                                  difficulty=block['difficulty'])
        hashes_match = hash_block(self.chain[-1]) == block['previous_hash']
        # print(proof_is_valid, hashes_match)
        if not proof_is_valid or not hashes_match:
            return False
        converted_block = Block(index=block['index'], previous_hash=block['previous_hash'], transactions=transactions, nonce=block['nonce'], time=block['timestamp'], difficulty=block['difficulty'], merkle_root=block['merkle_root'])
        self.__chain.append(converted_block)
        stored_transactions = self.__open_transactions[:]

        # 添加完广播回来的块之后，清理一下交易池里的记录
        for itx in block['transactions']:
            for opentx in stored_transactions:
                if opentx.sender == itx['sender'] and opentx.recipient == itx['recipient'] and opentx.amount == itx['amount'] and opentx.signature == itx['signature']:
                    try:
                        self.__open_transactions.remove(opentx)
                    except ValueError:
                        print('Item was already removed')

        self.save_data()
        return True

    # 解决冲突
    def resolve (self):
        winner_chain = self.chain
        replace = False

        for node in self.__peer_nodes:
            url = 'http://{}/chain'.format(node)
            try:
                response = requests.get(url)
                node_chain = response.json()
                node_chain = [Block(index=block['index'],
                                    previous_hash=block['previous_hash'],
                                    transactions=[Transaction(tx['sender'], tx['recipient'], tx['signature'], tx['amount']) for tx in block['transactions']],
                                    nonce=block['nonce'],
                                    time=block['timestamp'],
                                    difficulty=block['difficulty'],
                                    merkle_root=block['merkle_root']
                                    ) for block in node_chain]
                
                node_chain_length = len(node_chain)
                local_chain_length = len(winner_chain)
                if node_chain_length > local_chain_length and Verification.verify_chain(node_chain):
                    winner_chain = node_chain
                    replace = True
            except requests.exceptions.ConnectionError:
                continue
        self.resolve_conflicts = False
        self.chain = winner_chain

        if replace:
            self.__open_transactions = []
        self.save_data()
        return replace

    # 新增节点
    def add_peer_node(self, node):
        """Adds a new node to the peer node set"""
        self.__peer_nodes.add(node)
        self.save_data()

    # 删除节点
    def remove_peer_node(self, node):
        self.__peer_nodes.discard(node)
        self.save_data() 

    # 获取所有节点
    def get_peer_nodes(self):
        return list(self.__peer_nodes)
