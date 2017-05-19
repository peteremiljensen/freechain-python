# freechain-python
A blockchain framework for Python-3

[![Build Status](https://img.shields.io/travis/peteremiljensen/freechain-python/master.svg?maxAge=0)](https://travis-ci.org/peteremiljensen/freechain-python) [![Coverage Status](https://img.shields.io/coveralls/peteremiljensen/freechain-python/master.svg?maxAge=0)](https://coveralls.io/github/peteremiljensen/freechain-python)

The Python framework is developed as a Python3-module that is easily imported to
a new or existing application. The framework makes heavy use of threadding and
asynchronous sockets to make it more production-friendly in applications of
heavier demands. This means that the framework can potentially handle a high
amount of concurrent connections and deliver a greater throughput.

# Usage Example
Special care is been taken to assure its easy use without compromising
applicability and throughput. The uncomplicated use of the framework is
demonstrated by the following simple python script, which starts a minimal
blockchain node listening on port 9000&mdash;ready to receive loaves and
blocks.

```python
from freechain.node import *

node = Node(9000)
genesis_block = Block([], 0, "-1")
if node.add_block(genesis_block):
  node.start()
```

More elaborate examples can be found in the following repository on github:
[freechain-python-example](https://www.github.com/peteremiljensen/freechain-python-example)
