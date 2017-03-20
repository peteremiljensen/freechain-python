#!/usr/bin/env python3

from blockchain.loaf import Loaf

def main():
    data = {"pik": 3, "soren": "glemmer"}
    l = Loaf("2314", data)
    print (l.json())

if __name__ == '__main__':
    main()
