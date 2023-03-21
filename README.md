# 7200block-chain
Use python to build a blockchain system.
## Install packages
Run the command
```
pip install -r requirements.txt
```
## Run single node
```
python node.py
```
After installing packages, open the browser with the URL `localhost:5000` (default)
## Run multiple nodes
For example, if we want to run 2 nodes in the network. Open two terminals and input the following commands for the corresponding terminal.
Node 1 (This node runs in port 5000)
```
python node.py
```
Node 2 (This node runs in port 5001, you can change the port by yourself)
```
python node.py -p 5001
```
## Notice
There are two `node.py` files. One is `OLD_node.py`, which is the legacy version of `node.py` and it only enable users to interact with the blockchain locally in the terminal. The new `node.py` achieves APIs server, and the Web UI is allowed.
## Install Pycrypto
In the project, package `pycrypto` is needed. When installing it, install `pycryptodome` rather than `pycrypto`. The usages is the same.
```
pip install pycryptodome
```
## Contributors
5 handsome students
## Reference
https://www.udemy.com/course/learn-python-by-building-a-blockchain-cryptocurrency/?couponCode=D_0323
