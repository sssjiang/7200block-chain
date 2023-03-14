genesis_block = {
    'previous_hash': '',
    'index': 0,
    'transaction': []
}
blockchain = list([genesis_block])
open_transactions = list()
owner = 'Gamtin'


def hash_block(block):
    return '-'.join([str(block[key]) for key in block])


def get_last_blockchain_value():
    """ Returns the last value of the current blockchian. """
    if len(blockchain) < 1:
        return None
    return blockchain[-1]


def add_transaction(recipient, sender=owner, amount=1.0):
    """
    Arguments:
        :sender: The sender of the coins.
        :recipient: The recipient of the coins.
        :amont: The amount of coins sent with the transaction (default=1.0)
    """

    # if last_transaction == None:
    #     last_transaction = [1]
    # blockchain.append([last_transaction, transaction_amount])
    transaction = {
        'sender': sender,
        'recipient': recipient,
        'amount': amount
    }
    open_transactions.append(transaction)


def mine_block():
    # pass
    last_block = blockchain[-1]
    # 给上一个块进行 hash 计算
    hashed_block = hash_block(last_block)
    
    block = {
        'previous_hash': hashed_block,
        'index': len(blockchain),
        'transactions': open_transactions
    }

    # 加入新块
    blockchain.append(block)


def get_transaction_value():
    tx_recipient = input('Enter the recipient of the transaction: ')
    tx_amount = float(input('Your transacntion amount please: '))

    return tx_recipient, tx_amount


def get_user_choice():
    user_input = input('Your choice: ')
    return user_input


def print_blockchain_elements():
    for block in blockchain:
        print('Outputting Block')
        print(block)
    else:
        print('-' * 20)


def verify_chain():
    # block_index = 0
    for (index, block) in enumerate(blockchain):
        if index == 0:
            continue
        if block['previous_hash'] != hash_block(blockchain[index - 1]):
            return False
    return True


waiting_for_input = True

while waiting_for_input:
    print('Please choose')
    print('0: Print full blockchain')
    print('1: Add a new transacntion value')
    print('2: Mine a new block')
    print('3: Output the blockahcin amount')
    print('h: Manipulate the chain')
    print('q: Quit')

    user_choice = get_user_choice()

    if user_choice == '1':
        # tx_amount = get_transaction_value()
        tx_data = get_transaction_value()
        recipient, amount = tx_data

        add_transaction(recipient, amount=amount)
        print(open_transactions)
    elif user_choice == '0':
        print(blockchain)
    elif user_choice == '2':
        mine_block()
    elif user_choice == '3':
        print_blockchain_elements()
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
else:
    print('User left!')


print('Done!')
