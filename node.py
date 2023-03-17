from uuid import uuid4

from verification import Verification
from blockchain import Blockchain

"""
    Every node is just a computer having its local blockchain instance
    where you can mine and where you can send transactions and so on.
"""
class Node:
    def __init__(self) -> None:
        # self.id = str(uuid4())
        self.id = 'Gamtin'
        self.blockchain = Blockchain(self.id)

    # 用户选择功能
    def get_user_choice(self):
        user_input = input('Your choice: ')
        return user_input

    # 打印当前区块链中的区块
    def print_blockchain_elements(self):
        for block in self.blockchain.chain:
            print('-' * 20)
            print('Outputting Block')
            print(block)
        else:
            print('-' * 20)

    # 用户输入交易金额
    def get_transaction_value(self):
        tx_recipient = input('Enter the recipient of the transaction: ')
        tx_amount = float(input('Your transacntion amount please: '))

        return tx_recipient, tx_amount

    def listen_for_input(self):
        waiting_for_input = True

        while waiting_for_input:
            print('=' * 20)
            print('Please choose')
            print('1: Add a new transacntion value')
            print('2: Mine a new block')
            print('3: Output the blockahcin blocks')
            print('4: Check transaction validity')
            print('q: Quit')

            user_choice = self.get_user_choice()

            if user_choice == '1':
                # tx_amount = get_transaction_value()
                tx_data = self.get_transaction_value()
                recipient, amount = tx_data

                if self.blockchain.add_transaction(recipient, self.id, amount=amount): # 如果新增交易成功
                    print('Added transaction!')
                else:
                    print('Transaction failed!')
                print('Open transactions')
                print('-' * 20)
                print(self.blockchain.get_open_transactions())
                print('-' * 20)
            elif user_choice == '2':
                self.blockchain.mine_block()
            elif user_choice == '3':
                self.print_blockchain_elements()
            elif user_choice == '4':
                if Verification.verify_transactions(self.blockchain.get_open_transactions(), self.blockchain.get_balance):
                    print('All transactions are valid.')
                else:
                    print('There are invalid transactions.')
            elif user_choice == 'q':
                waiting_for_input = False
            else:
                print('Input was invalid, please pick a value from the list!')

            if not Verification.verify_chain(self.blockchain.chain):
                self.print_blockchain_elements()
                print('Invalid blockchain!')
                break
            print('Balance of {}: {:6.2f}'.format(self.id, self.blockchain.get_balance()))
        else:
            print('User left!')

        print('Done!')


node = Node()
node.listen_for_input()
