
class Request:
    def __init__(self, command, params):
        self.type = command
        self.params = params

class Response:
    def __init__(self, status, payload):
        self.status = status
        self.payload = payload