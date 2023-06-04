
class UserFunctions():
    def __init__(self):
        super().__init__()

    def start(self):
        name = 'John Doe'
        id = 1
        return ({'name': name, 'id': id})

    def checkTrack(self, order_number):
        if order_number == '12345':
            return 'Pedido saiu para entrega'
        else:
            return None

    def unlockCard(self, card_number, code):
        if card_number == '12345' and code == '123':
            return True
        else:
            return None