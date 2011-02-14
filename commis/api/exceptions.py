class ChefAPIError(Exception):
    def __init__(self, code, msg, *args):
        self.code = code
        self.msg = msg%args
