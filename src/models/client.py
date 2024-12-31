class Client:
    def __init__(self, id, name, phone):
        self.id = id
        self.name = name
        self.phone = phone

    @staticmethod
    def from_dict(data):
        return Client(data["id"], data["name"], data["phone"])
