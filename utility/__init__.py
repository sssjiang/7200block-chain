# Module bundles
from utility.hash_util import hash_string_256, hash_block

__all__ = ['hash_string_256', 'hash_block']  # __all__ 变量存储了可以被 export 出去的变量，当从外部访问的时候，只能访问这两个被变量
