#!/usr/bin/env python3

from blockchain.loaf import Loaf

def main():
    data = {"pik": 3, "søren": "glemmer"}
    l = Loaf("2314", data)

    new_loaf = Loaf.create_loaf_from_json(l.json())
    print (new_loaf.validate())

if __name__ == '__main__':
    main()
