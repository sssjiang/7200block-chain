import json
import hashlib as hl

def hash_string_256(string):
    return hl.sha256(string).hexdigest()


# 使用 SHA256 对区块进行 hash 计算
def hash_block(block):
    """Hashes a block and returns a string representation of it

    Arguments
        block: The block that should be hashed 
    """
    # 加 copy 是因为 hashable_block 要被 json.dumps 用来转换为 String
    # 为了不让原数据被修改，使用 copy
    hashable_block = block.__dict__.copy()
    hashable_block['transactions'] = [tx.to_ordered_dict() for tx in hashable_block['transactions']]

    # sort_keys 设置为 True 是因为要避免因为某种原因，字典里的 key 顺序发生了改变，而导致同一个字典（里面的 key 顺序不一致）的 hash 值不一样，进而验证失败
    return hash_string_256(json.dumps(hashable_block, sort_keys=True).encode())
    