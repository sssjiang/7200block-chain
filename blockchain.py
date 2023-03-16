from functools import reduce
import hashlib as hl
import json
from collections import OrderedDict

MINING_REWARD = 10.0  # 挖矿奖励

genesis_block = {
    'previous_hash': '',
    'index': 0,
    'transactions': [],
    'proof': 100  # 因为是 genesis block，所以值可以随便设置
}
blockchain = list([genesis_block])
open_transactions = list()
owner = 'Gamtin'
participants = {'Gamtin'}


# 使用 SHA256 对区块进行 hash 计算
def hash_block(block):
    """Hashes a block and returns a string representation of it

    Arguments
        block: The block that should be hashed 
    """
    # sort_keys 设置为 True 是因为要避免因为某种原因，字典里的 key 顺序发生了改变，而导致同一个字典（里面的 key 顺序不一致）的 hash 值不一样，进而验证失败
    return hl.sha256(json.dumps(block, sort_keys=True).encode()).hexdigest()


# 工作量证明 Proof-of-work
# SHA256(交易记录 + 上一个块的hash值 + 随机数)
def valid_proof(transactions, last_hash, proof):
    guess = (str(transactions) + str(last_hash) + str(proof)).encode()
    guess_hash = hl.sha256(guess).hexdigest()
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
    tx_sender = [[tx['amount'] for tx in block['transactions'] if tx['sender'] == participant] for block in blockchain]
    # 获得在交易池中用户发出去的金额记录
    open_tx_sender = [tx['amount'] for tx in open_transactions if tx['sender'] == participant]
    tx_sender.append(open_tx_sender)

    amount_sent = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt), tx_sender, 0) # 简化版
    # amount_sent = 0
    # for tx in tx_sender:
    #     if len(tx) > 0:
    #         amount_sent += sum(tx)

    # 获得过往交易中用户总共得到的数量
    tx_recipient = [[tx['amount'] for tx in block['transactions'] if tx['recipient'] == participant] for block in blockchain]
    amount_received = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt), tx_recipient, 0) # 简化版
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
    sender_balance = get_balance(transaction['sender'])
    if sender_balance >= transaction['amount']:  # 检验发送方的余额是否多于本次交易的金额
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
    transaction = OrderedDict([ # 只用 python 内置的 OrderedDict 库创建排好序的字典
        ('sender', sender),
        ('recipient', recipient),
        ('amount', amount)
    ])
    if verify_transaction(transaction):
        open_transactions.append(transaction)
        participants.add(sender)
        participants.add(recipient)
        return True
    return False


# 挖矿
def mine_block():
    """Create a new block and add open transactions to it."""
    last_block = blockchain[-1]
    hashed_block = hash_block(last_block)  # 计算上一个块的 hash 值
    proof = proof_of_work() # PoW只针对 open_transactions 里的交易，不包括系统奖励的交易

    reward_transaction = OrderedDict([ # 系统奖励
        ('sender', 'SYSTEM'),
        ('recipient', owner),
        ('amount', MINING_REWARD)
    ])

    copied_transactions = open_transactions[:]  # 复制交易池记录（未加入奖励交易之前的）（深拷贝！）
    copied_transactions.insert(0, reward_transaction) # 将系统奖励的coins加进去
    block = {  # 创建新块
        'previous_hash': hashed_block,
        'index': len(blockchain),
        'transactions': copied_transactions,
        'proof': proof
    }

    # 加入新块
    blockchain.append(block)
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
        print('Outputting Block')
        print(block)
    else:
        print('-' * 30)


# 验证区块中的 hash 值
def verify_chain():
    # block_index = 0
    for (index, block) in enumerate(blockchain):
        if index == 0:
            continue
        if block['previous_hash'] != hash_block(blockchain[index - 1]):
            return False
        
        # block['transactions'][1:] 这样写是因为我把系统奖励的交易放在了第0个，要排除掉系统奖励的交易，因此从下标1开始
        if not valid_proof(block['transactions'][1:], block['previous_hash'], block['proof']):
            print('Proof of work is invalid')
            return False
    return True


waiting_for_input = True

while waiting_for_input:
    print('=' * 30)
    print('Please choose')
    print('0: Print full blockchain')
    print('1: Add a new transacntion value')
    print('2: Mine a new block')
    print('3: Output the blockahcin blocks')
    print('4: Output participants')
    print('5: Check transaction validity')
    print('h: Manipulate the chain')
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
        print('-' * 30)
        print('Open transactions')
        print(open_transactions)
        print('-' * 30)
    elif user_choice == '0':
        print(blockchain)
    elif user_choice == '2':
        if mine_block():
            open_transactions = []  # 挖矿成功，交易池清空
    elif user_choice == '3':
        print_blockchain_elements()
    elif user_choice == '4':
        print(participants)
    elif user_choice == '5':
        if verify_transactions():
            print('All transactions are valid.')
        else:
            print('There are invalid transactions.')
    elif user_choice == 'h':  # 模拟hack攻击
        if len(blockchain) >= 1:
            blockchain[0] = {
                'previous_hash': '',
                'index': 0,
                'transactions': [{
                    'sender': 'A',
                    'recipient': 'B',
                    'amount': 100.0
                }]
            }
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
