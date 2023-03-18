from Crypto.PublicKey import RSA  # pycrypto 包
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
import Crypto.Random
import binascii

class Wallet:
    def __init__(self):
        self.private_key = None
        self.public_key = None  # 公钥作为每个钱包的地址

    # 将公私钥保存到变量中
    def create_keys(self):
        private_kay, public_key = self.generate_keys()
        self.private_key = private_kay
        self.public_key = public_key
    
    # 把公私钥存起来
    def save_keys(self):
        if self.public_key != None and self.private_key != None:
            try:
                with open('wallet.txt', mode='w') as f:
                    f.write(str(self.public_key))
                    f.write('\n')
                    f.write(str(self.private_key))
            except (IOError, IndexError):
                print('Saving wallet failed...')

    # 从本地文件加载公私钥
    def load_keys(self):
        try:
            with open('wallet.txt', mode='r') as f:
                keys = f.readlines()
                public_key = keys[0][:-1]  # 因为写公钥的时候加了'\n'，所以最后一位不读
                private_key = keys[1]
                self.public_key = public_key
                self.private_key = private_key
        except (IOError, IndexError):
            print('Loading wallet failed...')

    # 用RSA生成并返回公私钥对
    def generate_keys(self):
        private_key = RSA.generate(1024, Crypto.Random.new().read)
        public_key = private_key.publickey()
        return binascii.hexlify(private_key.exportKey(format='DER')).decode('ascii'), binascii.hexlify(public_key.exportKey(format='DER')).decode('ascii')
    
    # 生成签名
    def sign_transaction(self, sender, recipient, amount):
        signer = PKCS1_v1_5.new(RSA.importKey(binascii.unhexlify(self.private_key)))
        h = SHA256.new((str(sender) + str(recipient) + str(amount)).encode('utf8'))
        signature = signer.sign(h) # 生成出来的签名的二进制的
        return binascii.hexlify(signature).decode('ascii') # 用 hexlify 转成十六进制，使用 ascii 编码

    # 验证签名
    @staticmethod
    def verify_transaction(transaction):
        # if transaction.sender == 'MINING':
        #     return True
        public_key = RSA.importKey(binascii.unhexlify(transaction.sender))
        verifier = PKCS1_v1_5.new(public_key)
        h = SHA256.new((str(transaction.sender) + str(transaction.recipient) + str(transaction.amount)).encode('utf8'))
        return verifier.verify(h, binascii.unhexlify(transaction.signature))
