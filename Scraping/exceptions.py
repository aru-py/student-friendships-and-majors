class NonFatalException(Exception):
    """Harmless exceptions."""
    def __init__(self, person):
        if isinstance(person, Person):
            self.message = "{name} ({username})".format(name=person.name, username=person.username)
        else:
            self.message = 'Person'


class PersonInDirectory(NonFatalException):
    """Person is already in directory/"""

    def __str__(self):
        return "{person} has already been scraped!".format(person=self.message)


class PersonNotAtClemson(NonFatalException):
    """Person is not a Clemson student."""
    def __str__(self):
        return "{person} is not a Clemson student!".format(person=self.message)


class FatalException(Exception):
    """Major Exceptions"""
    pass


class TooManyRequests(FatalException):
    """Too many requests sent to Venmo Server."""
    def __str__(self):
        return "Too many requests sent to Venmo server!"


class SessionTimeOut(FatalException):
    """Venmo session timed out."""
    def __str__(self):
        return "Venmo session timed out!"


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
        return self.name, self.username, self.id, self.cuid, self.major, self.class_standing, self.friends, self.transactions
