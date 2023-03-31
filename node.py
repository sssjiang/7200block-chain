from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from wallet import Wallet
from blockchain import Blockchain

app = Flask(__name__, template_folder='ui', static_folder='ui', static_url_path='/ui')
# wallet = Wallet()
# blockchain = Blockchain(wallet.public_key)
CORS(app)

# 新增钱包（公私钥，余额）
@app.route('/wallet', methods=['POST'])
def create_keys():
    wallet.create_keys()
    if wallet.save_keys():
        global blockchain
        blockchain = Blockchain(wallet.public_key, port)
        response = {
            'public_key': wallet.public_key,
            'private_key': wallet.private_key,
            'funds': blockchain.get_balance()
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Saving the keys failed.'
        }
        return jsonify(response), 500

# 查看钱包
@app.route('/wallet', methods=['GET'])
def load_keys():
    if wallet.load_keys():
        global blockchain
        blockchain = Blockchain(wallet.public_key, port)
        response = {
            'public_key': wallet.public_key,
            'private_key': wallet.private_key,
            'funds': blockchain.get_balance()
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Loading the keys failed.'
        }
        return jsonify(response), 500

# 查看余额
@app.route('/balance', methods=['GET'])
def get_balance():
    balance = blockchain.get_balance()
    if balance != None:
        response = {
            'message': 'Fetching balance successfully.',
            'funds': balance
        }
        return jsonify(response), 200
    else:
        response = {
            'message': 'Loading balance failed.',
            'wallet_set_up': wallet.public_key != None
        }
        return jsonify(response), 500


@app.route('/', methods=['GET'])  # 进入首页
def get_ui():
    return send_from_directory('ui', 'index.html')


@app.route('/network', methods=['GET'])
def get_network_ui(): # 进入节点管理页
    return send_from_directory('ui', 'network.html')


# 新增交易
@app.route('/transaction', methods=['POST'])
def add_transaction():
    if wallet.public_key == None:
        response = {
            'message': 'No wallet set up.',
        }
        return jsonify(response), 400

    values = request.get_json() if request.data else None
    if not values:
        response = {
            'message': 'No data found.'
        }
        return jsonify(response), 400

    required_fields = ['recipient', 'amount']
    if not all(field in values for field in required_fields):
        response = {
            'message': 'Required data in missing.'
        }
        return jsonify(response), 400
    recipient = values['recipient']
    amount = float(values['amount'])
    signature = wallet.sign_transaction(wallet.public_key, recipient, amount)
    success = blockchain.add_transaction(
        recipient,
        wallet.public_key,
        signature,
        amount
    )
    
    if success:
        response = {
            'message': 'Successfully added transaction.',
            'transaction': {
                'sender': wallet.public_key,
                'recipient': recipient,
                'amount': amount,
                'signature': signature
            },
            'funds': blockchain.get_balance()
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Creating a transaction failed.'
        }
        return jsonify(response), 500

# 挖矿
@app.route('/mine', methods=['POST'])
def mine():
  if blockchain.resolve_conflicts:  # 当挖矿的时候发现区块链和其他节点的存在冲突
      response = {'message': 'Resolve conflicts first, block not added!'}
      return jsonify(response), 409

  block = blockchain.mine_block()
  if block != None:
      dict_block = block.__dict__.copy()
      dict_block['transactions'] = [tx.__dict__ for tx in dict_block['transactions']]
      response = {
          'message': 'Block added successfully',
          'block': dict_block,
          'funds': blockchain.get_balance()
      }
      return jsonify(response), 201
  else:
      response = {
          'message': 'Adding a block failed.',
          'wallet_set_up': wallet.public_key != None
      }
      return jsonify(response), 500
  

@app.route('/resolve-conflicts', methods=['POST'])
def resolve_conflicts():
    replaced = blockchain.resolve()
    if replaced:
        response = {'message': 'Chain was replaced!'}
    else:
        response = {'message': 'Local chain kept!'}
    return jsonify(response), 200
  

@app.route('/broadcast-block', methods=['POST'])
def broadcast_block():
    values = request.get_json()
    if not values:
        response = {'message': 'No data found.'}
        return jsonify(response), 400
    if 'block' not in values:
        response = {'message': 'Some data is missing.'}
        return jsonify(response), 400
    block = values['block']
    if block['index'] == blockchain.chain[-1].index + 1:  # 如果广播来的区块的index等于最后一个区块的index+1
        if blockchain.add_block(block):
            response = {'message': 'Block added.'}
            print('Block added.')
            return jsonify(response), 201
        else:
            response = {'message': 'Block seems invalid.'}
            print('Block seems invalid.')
            return jsonify(response), 409
    elif block['index'] > blockchain.chain[-1].index: # 如果广播来的区块长度大于当前区块长度
        # print(block['index'], blockchain.chain[-1].index)
        response = {'message': 'Blockchain seems to differ from local blockchain'}
        print('Blockchain seems to differ from local blockchain')
        blockchain.resolve_conflicts = True
        return jsonify(response), 200
    else:
        response = {'message': 'Blockchain seems to be shorter, block not added'}
        print('Blockchain seems to be shorter, block not added')
        return jsonify(response), 409



# 广播交易
# 当其节点新增了交易地时候，就会调用这个接口
# 比如，网络中有 5000 和 5001 两个节点
# 5000 节点新增了交易，就会调用 5001 节点的 /broadcast-transaction 接口来让 5001 自动更新它本地的交易池
@app.route('/broadcast-transaction', methods=['POST'])
def broadcast_transaction():
    values = request.get_json()
    if not values:
        response = {'message': 'No data found.'}
        return jsonify(response), 400
    required = ['sender', 'recipient', 'amount', 'signature']
    if not all(key in values for key in required):
        response = {'message': 'Some data is missing.'}
        return jsonify(response), 400
    success = blockchain.add_transaction(values['recipient'], values['sender'], values['signature'], values['amount'], is_receiving=True)
    if success:
        response = {
            'message': 'Successfully added transaction.',
            'transaction': {
                'sender': wallet.public_key,
                'recipient': values['recipient'],
                'amount': values['amount'],
                'signature': values['signature']
            }
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Creating a transaction failed.'
        }
        return jsonify(response), 500


# 获取交易池
@app.route('/transactions', methods=['GET'])
def get_open_transaction():
    transactions = blockchain.get_open_transactions()
    dict_transactions = [tx.__dict__ for tx in transactions]
    response = dict_transactions
    return jsonify(response), 200


# 获取区块链信息
@app.route('/chain', methods=['GET'])
def get_chain():
    chain_snapshot = blockchain.chain
    # Add .copy() to prevent unexpected side effect when you manipulate the data
    dict_chain = [block.__dict__.copy() for block in chain_snapshot]
    for dict_block in dict_chain:
        dict_block['transactions'] = [tx.__dict__ for tx in dict_block['transactions']]

    return jsonify(dict_chain), 200


@app.route('/node', methods=['POST'])
def add_node():
    values = request.get_json() if request.data else None
    if not values:
        response = {
            'message': 'No data received.'
        }
        return jsonify(response), 400
    if 'node' not in values:
        response = {
            'message': 'No node data found.'
        }
        return jsonify(response), 400
    node = values.get('node')
    node = values['node']
    blockchain.add_peer_node(node)
    response = {
        'message': 'Node added successfully.',
        'all_nodes': blockchain.get_peer_nodes()
    }
    return jsonify(response), 201


# 删除节点
@app.route('/node/<node_url>', methods=['DELETE'])
def remove_node(node_url):
    if node_url == "" or node_url == None:
        response = {
            'message': 'No node found.'
        }
        return jsonify(response), 400
    blockchain.remove_peer_node(node_url)
    response = {
        'message': 'Node removed',
        'all_nodes': blockchain.get_peer_nodes()
    }
    return jsonify(response), 200


# 获得节点列表
@app.route('/nodes', methods=['GET'])
def get_nodes():
    nodes = blockchain.get_peer_nodes()
    response = {
        'all_nodes': nodes
    }
    return jsonify(response), 200


if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', type=int, default=5012)
    args = parser.parse_args()
    port = args.port
    wallet = Wallet(port)
    blockchain = Blockchain(wallet.public_key, port)
    app.run(host='0.0.0.0', port=port)
