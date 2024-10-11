class Users:
    def __init__(self, name: str, email:str, password: str):
        self.name = name
        self.email = email
        self.password = password

class Messages:
    def __init__(self, sender: str, recipient: str, message: str):
        self.sender = sender
        self.recipient = recipient
        self.message = message