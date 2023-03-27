from Crypto.PublicKey import ECC  # pycrypto 包
from Crypto.Signature import DSS
from Crypto.Hash import SHA256
import Crypto.Random
import binascii

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
        private_key = ECC.generate(curve='P-256')
        public_key = private_key.public_key()
        return binascii.hexlify(private_key.export_key(format='DER')).decode('ascii'), binascii.hexlify(public_key.export_key(format='DER')).decode('ascii')
    
    # 生成签名
    def sign_transaction(self, sender, recipient, amount):
        signer = DSS.new(ECC.import_key(binascii.unhexlify(self.private_key)), 'fips-186-3')
        h = SHA256.new((str(sender) + str(recipient) + str(amount)).encode('utf8'))
        signature = signer.sign(h) # 生成出来的签名的二进制的
        return binascii.hexlify(signature).decode('ascii') # 用 hexlify 转成十六进制，使用 ascii 编码

    # 验证签名
    @staticmethod
    def verify_transaction(transaction):
        # if transaction.sender == 'MINING':
        #     return True
        public_key = ECC.import_key(binascii.unhexlify(transaction.sender))
        verifier = DSS.new(public_key, 'fips-186-3')
        h = SHA256.new((str(transaction.sender) + str(transaction.recipient) + str(transaction.amount)).encode('utf8'))
        return verifier.verify(h, binascii.unhexlify(transaction.signature))
