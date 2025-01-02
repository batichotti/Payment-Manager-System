class Backlog:
    def __init__(self, id, payment_id, change_date, responsible_user, description):
        self.id = id
        self.payment_id = payment_id
        self.change_date = change_date
        self.responsible_user = responsible_user
        self.description = description

    @staticmethod
    def from_dict(data):
        return Backlog(
            data["id"],
            data["payment_id"],
            data["change_date"],
            data["responsible_user"],
            data["description"]
        )
