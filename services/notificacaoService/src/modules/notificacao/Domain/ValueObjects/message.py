class Message:
    def __init__(self, message):
        self.message = self.verify(message)

    def verify(message):
        return message  
    def __str__(self):
        return self.message 
    def __repr__(self):
        return self.message
    @staticmethod
    def create(message):
        return Message(message)