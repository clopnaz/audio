import time 
import pprint

"""
context managers still __exit__() when we ctrl+c

usage: run it, and then quickly ctrl+c it.
"""

class Session:
    def __enter__(self):
        print("entered") 
    def __exit__(*args): 
        print("exited") 
        print("") 
        pprint.pp(args) 
        print("") 
        print("\nbut I can still make you wait...\n") 
        time.sleep(3)

if __name__ == "__main__":
    with Session() as session:
        time.sleep(2)
