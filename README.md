# 7200block-chain
Use python to build a blockchain system.
## Install packages
Run the command
```
pip install -r requirements.txt
```
## Run
```
python node.py
```
After installing packages, open the browser with the URL `localhost:5000`
## Notice
There are two `node.py` files. One is `OLD_node.py`, which is the legacy version of `node.py` and it only enable users to interact with the blockchain locally in the terminal. The new `node.py` achieves APIs server, and the Web UI is allowed.
## Install Pycrypto
In the project, package `pycrypto` is needed. When installing it, install `pycryptodome` rather than `pycrypto`. The usages is the same.
```
pip install pycryptodome
```
## Reference
https://www.bilibili.com/video/BV1Hb411c7oH/
