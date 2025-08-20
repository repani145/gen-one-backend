class SerializerError(Exception):
    
    def __init__(self, data):
        error_messages = []
        for field, error in data.items():
            error_message = str(error[0])
            error_messages.append(error_message)
        self.data = error_messages[0]
    
    def __str__(self):
        return self.data