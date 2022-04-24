
class UserFunctions():
    def __init__(self):
        super().__init__()

    def start(self):
        name = 'John Doe'
        id = 1
        return ({'name': name, 'id': id})

    def checkHistory(self, id):
        return 'Today: U$: 1000.00'

    def checkCredit(self, id, branchName):
        return None

    def creditCardOffer(self, id):
        return {'limit': 2000, 'tax': 20}