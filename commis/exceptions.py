class ChefAPIError(Exception):
    def __init__(self, code, msg, *args):
        self.code = code
        self.msg = msg%args


class InsuffcientPermissions(Exception):
    """Token error for permissions failure."""

    def __init__(self, model, action):
        self.model = model
        self.action = action
