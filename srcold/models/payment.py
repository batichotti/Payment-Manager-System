class Payment:
    def __init__(self, id, client_id, amount, due_date, status, visible=True):
        self.id = id
        self.client_id = client_id
        self.amount = amount
        self.due_date = due_date
        self.status = status
        self.visible = visible

    @staticmethod
    def from_dict(data):
        return Payment(
            data["id"],
            data["client_id"],
            data["amount"],
            data["due_date"],
            data["status"],
            data["visible"],
        )

    @staticmethod
    def from_db(row):
        return Payment(
            id=row['id'],
            client_id=row['client_id'],
            amount=row['amount'],
            due_date=row['due_date'],
            is_paid=row['is_paid'],
            visible=row['visible']
        )
