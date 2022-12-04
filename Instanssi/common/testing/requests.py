class FakeResponse(object):
    """
    Fake response for requests lib testing
    """

    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message

    def json(self):
        return self.message
