from ecdsa import SigningKey, VerifyingKey, SECP256k1
import binascii
import transaction

class Wallet:
    def __init__(self, node_id):
        self.private_key = None
        self.public_key = None  # 公钥作为每个钱包的地址
        self.node_id = node_id

    # 将公私钥保存到变量中
    def create_keys(self):
        private_kay, public_key = self.generate_keys()
        self.private_key = private_kay
        self.public_key = public_key
    
    # 把公私钥存起来
    def save_keys(self):
        if self.public_key != None and self.private_key != None:
            try:
                with open('wallet-{}.txt'.format(self.node_id), mode='w') as f:
                    f.write(self.public_key)
                    f.write('\n')
                    f.write(self.private_key)
                return True
            except (IOError, IndexError):
                print('Saving wallet failed...')
                return False

    # 从本地文件加载公私钥
    def load_keys(self):
        try:
            with open('wallet-{}.txt'.format(self.node_id), mode='r') as f:
                keys = f.readlines()
                public_key = keys[0][:-1]  # 因为写公钥的时候加了'\n'，所以最后一位不读
                private_key = keys[1]
                self.public_key = public_key
                self.private_key = private_key
            return True
        except (IOError, IndexError):
            print('Loading wallet failed...')
            return False

    # 用ECC生成并返回公私钥对
    def generate_keys(self):
        sk = SigningKey.generate(curve=SECP256k1)
        vk = sk.get_verifying_key()
        return (binascii.hexlify(sk.to_string()).decode('ascii'),
                binascii.hexlify(vk.to_string()).decode('ascii'))
    # 生成签名 签名的时候的 DER 编码转成 uncompressed 编码
    def sign_transaction(self, sender, recipient, amount):

        sk = SigningKey.from_string(binascii.unhexlify(self.private_key), curve=SECP256k1)
        h = (str(sender) + str(recipient) + str(amount)).encode('utf8')
        signature = sk.sign(h) # 生成出来的签名的二进制的
        #signature的格式是DER编码的，需要转成uncompressed编码
        return binascii.hexlify(signature).decode('ascii') 
    # 验证签名
    @staticmethod
    def verify_transaction(transaction):
        vk = VerifyingKey.from_string(binascii.unhexlify(transaction.sender), curve=SECP256k1)
        h = (str(transaction.sender) + str(transaction.recipient) + str(transaction.amount)).encode('utf8')
        return vk.verify(binascii.unhexlify(transaction.signature), h)
        #verify always return True or False
        

#test code
if __name__ == '__main__':
    wallet = Wallet(5001)
    wallet.create_keys()
    wallet.save_keys()
    wallet.load_keys()
    print("-----",wallet.public_key)
    print(wallet.private_key)
    #__init__(self, sender, recipient, signature, amount)
    signature = wallet.sign_transaction(wallet.public_key, wallet.public_key, 10)
    transaction1 = transaction.Transaction(wallet.public_key,wallet.public_key,signature,10)
    print("signigngingi",signature)
    print("transaction1transaction1",transaction1)
    print(Wallet.verify_transaction(transaction1))
