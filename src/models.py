"""
models.py
"""

class Person:
    def __init__(self, args):
        self.name = args[0]
        self.username = args[1]
        self.id = None
        self.cuid = None
        self.major = None
        self.class_standing = None
        self.friends = []
        self.transactions = []

    def dump(self):
        return self.name, self.username, self.id, self.cuid, self.major, \
               self.class_standing, self.friends, self.transactions