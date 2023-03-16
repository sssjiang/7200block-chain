from functools import reduce
from collections import OrderedDict
import json
import pickle

from hash_util import hash_block, hash_string_256
from block import Block
from transaction import Transaction

MINING_REWARD = 10.0  # 挖矿奖励

blockchain = list()
open_transactions = list()
owner = 'Gamtin'
participants = {'Gamtin'}


# 加载区块链数据
def load_data():
    """ 1. mode 'rb' read the binary data
        2. use pickle to read and write data is better than using json
        3. because using json to load data may occur some order problem
    """
    global blockchain
    global open_transactions
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
                converted_tx = [Transaction(tx['sender'], tx['recipient'], tx['amount']) for tx in block['transactions']]
                # converted_tx = [OrderedDict([ # 这个步骤很重要，因为所有的 transactions 里面的字典数据都是使用 OrderedDict 生成的，和普通的 dict 不一样，不加这一步的话会导致验证区块失败
                #                     ('sender', tx['sender']),
                #                     ('recipient', tx['recipient']),
                #                     ('amount', tx['amount'])
                #                 ]) for tx in block['transactions']]
                updated_block = Block(
                    block['index'],
                    block['previous_hash'],
                    converted_tx,
                    block['proof'],
                    block['timestamp']
                )
                # updated_block = {
                #     'previous_hash': block['previous_hash'],
                #     'index': block['index'],
                #     'proof': block['proof'],
                #     'transactions': converted_tx
                # }
                updated_blockchain.append(updated_block)
            blockchain = updated_blockchain

            open_transactions = json.loads(file_content[1])
            updated_open_transactions = []
            for tx in open_transactions:
                updated_transaction = Transaction(tx['sender'], tx['recipient'], tx['amount'])
                # updated_transaction = OrderedDict([ # 这个步骤很重要，因为所有的 transactions 里面的字典数据都是使用 OrderedDict 生成的，和普通的 dict 不一样，不加这一步的话会导致验证区块失败
                #     ('sender', tx['sender']),
                #     ('recipient', tx['recipient']),
                #     ('amount', tx['amount'])
                # ])
                updated_open_transactions.append(updated_transaction)
            open_transactions = updated_open_transactions
    except (IOError, IndexError): # 处理文件为空的问题
        genesis_block = Block(0, '', [], 100, 0)
        blockchain = [genesis_block]
        open_transactions = list()
    except ValueError:
        print('Value error!')
    except:
        print('Some errors!')
    finally:
        print('Cleanup!')


# 将交易保存到本地文件中
def save_data():
    """ 1. mode 'wb' for wirting binary data to files
        2. use pickle to dumps binary data
    """
    try:
        with open('blockchain.txt', mode='w') as f:
            # 因为 block 是 Block 类的对象，不可以直接使用 json.dumps 来转化为 String 类型
            # 所以需要将 blockchian 列表里面的所有 block 对象转化为 dict，使用 block.__dict__
            saveable_chain = [block.__dict__
                              for block in [Block(block_el.index, block_el.previous_hash, [tx.__dict__ for tx in block_el.transactions], block_el.proof, block_el.timestamp)
                                            for block_el in blockchain]]
            saveable_tx = [tx.__dict__ for tx in open_transactions]

            f.write(json.dumps(saveable_chain))
            f.write('\n')
            f.write(json.dumps(saveable_tx))
            # save_data = {
            #     'chain': blockchain,
            #     'ot': open_transactions
            # }
            # f.write(pickle.dumps(save_data))
    except IOError:
        print('Saving failed!')


load_data()  # 加载区块数据


# 工作量证明 Proof-of-work
# SHA256(交易记录 + 上一个块的hash值 + 随机数)
def valid_proof(transactions, last_hash, proof):
    # 因为 transactions 里面放的都是 tx 对象
    # Transaction 类里面定义了 to_ordered_dict 方法
    # 调用对象的方法 to_ordered_dict() 转换为 OrderedDict
    guess = (str([tx.to_ordered_dict() for tx in transactions]) + str(last_hash) + str(proof)).encode()
    guess_hash = hash_string_256(guess)
    # print(guess_hash)
    return guess_hash[0:2] == '00'


# 工作量证明 Proof-of-work
def proof_of_work():
    last_block = blockchain[-1]
    last_hash = hash_block(last_block)
    proof = 0
    while not valid_proof(open_transactions, last_hash, proof):
        proof +=1
    return proof


# 计算用户的余额
def get_balance(participant):
    # 获得过往交易中用户发送出去的所有金额记录
    tx_sender = [[tx.amount
                  for tx in block.transactions if tx.sender == participant] for block in blockchain]
    # 获得在交易池中用户发出去的金额记录
    open_tx_sender = [tx.amount
                      for tx in open_transactions if tx.sender == participant]
    tx_sender.append(open_tx_sender)
    print(tx_sender, 'tx_sender')

    amount_sent = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt), tx_sender, 0) # 简化版
    # amount_sent = 0
    # for tx in tx_sender:
    #     if len(tx) > 0:
    #         amount_sent += sum(tx)

    # 获得过往交易中用户总共得到的数量
    tx_recipient = [[tx.amount
                     for tx in block.transactions if tx.recipient == participant] for block in blockchain]
    amount_received = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt), tx_recipient, 0) # 简化版
    print(tx_recipient, 'tx_recipient')
    # amount_received = 0
    # for tx in tx_recipient:
    #     if len(tx) > 0:
    #         amount_received += tx[0]

    return amount_received - amount_sent  # 获得 - 送出去 = 余额


# 获取最后一个区块
def get_last_blockchain_value():
    """ Returns the last value of the current blockchian. """
    if len(blockchain) < 1:
        return None
    return blockchain[-1]


# 校验交易
def verify_transaction(transaction):
    sender_balance = get_balance(transaction.sender)
    if sender_balance >= transaction.amount:  # 检验发送方的余额是否多于本次交易的金额
        return True
    else:
        return False


# 校验交易列表
def verify_transactions():
    # all 的作用就是检验列表中的值是否都为 True
    return all([verify_transaction(tx) for tx in open_transactions])


# 新增交易
def add_transaction(recipient, sender=owner, amount=1.0):
    """
    Arguments:
        :sender: The sender of the coins.
        :recipient: The recipient of the coins.
        :amont: The amount of coins sent with the transaction (default=1.0)
    """
    transaction = Transaction(sender, recipient, amount)
    if verify_transaction(transaction):
        open_transactions.append(transaction)
        save_data()
        return True
    return False


# 挖矿
def mine_block():
    """Create a new block and add open transactions to it."""
    last_block = blockchain[-1]
    hashed_block = hash_block(last_block)  # 计算上一个块的 hash 值
    proof = proof_of_work() # PoW只针对 open_transactions 里的交易，不包括系统奖励的交易

    reward_transaction = Transaction('MINING', owner, MINING_REWARD) # 系统奖励

    copied_transactions = open_transactions[:]  # 复制交易池记录（未加入奖励交易之前的）（深拷贝！）
    copied_transactions.append(reward_transaction) # 将系统奖励的coins加进去
    block = Block(len(blockchain), hashed_block, copied_transactions, proof) # 创建新块

    # 加入新块
    blockchain.append(block)
    save_data()
    return True


# 用户输入交易金额
def get_transaction_value():
    tx_recipient = input('Enter the recipient of the transaction: ')
    tx_amount = float(input('Your transacntion amount please: '))

    return tx_recipient, tx_amount


# 用户选择功能
def get_user_choice():
    user_input = input('Your choice: ')
    return user_input


# 打印当前区块链中的区块
def print_blockchain_elements():
    for block in blockchain:
        print('-' * 20)
        print('Outputting Block')
        print(block.__dict__)
    else:
        print('-' * 20)


# 验证区块中的 hash 值
def verify_chain():
    # block_index = 0
    for (index, block) in enumerate(blockchain):
        if index == 0:
            continue
        if block.previous_hash != hash_block(blockchain[index - 1]):
            return False
        
        # block['transactions'][1:] 这样写是因为我把系统奖励的交易放在了第0个，要排除掉系统奖励的交易，因此从下标1开始
        if not valid_proof(block.transactions[:-1], block.previous_hash, block.proof):
            print('Proof of work is invalid')
            return False
    return True


waiting_for_input = True

while waiting_for_input:
    print('=' * 20)
    print('Please choose')
    print('0: Print full blockchain')
    print('1: Add a new transacntion value')
    print('2: Mine a new block')
    print('3: Output the blockahcin blocks')
    print('4: Output participants')
    print('5: Check transaction validity')
    print('q: Quit')

    user_choice = get_user_choice()

    if user_choice == '1':
        # tx_amount = get_transaction_value()
        tx_data = get_transaction_value()
        recipient, amount = tx_data

        if add_transaction(recipient, amount=amount): # 如果新增交易成功
            print('Added transaction!')
        else:
            print('Transaction failed!')
        print('Open transactions')
        print('-' * 20)
        print(open_transactions)
        print('-' * 20)
    elif user_choice == '0':
        print(blockchain)
    elif user_choice == '2':
        if mine_block():
            open_transactions = []  # 挖矿成功，交易池清空
            save_data()
    elif user_choice == '3':
        print_blockchain_elements()
    elif user_choice == '4':
        print(participants)
    elif user_choice == '5':
        if verify_transactions():
            print('All transactions are valid.')
        else:
            print('There are invalid transactions.')
    elif user_choice == 'q':
        waiting_for_input = False
    else:
        print('Input was invalid, please pick a value from the list!')

    if not verify_chain():
        print_blockchain_elements()
        print('Invalid blockchain!')
        break
    print('Balance of {}: {:6.2f}'.format(owner, get_balance(owner)))
else:
    print('User left!')


print('Done!')
