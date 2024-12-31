from datetime import datetime

class DateUtils:
    @staticmethod
    def days_until(date):
        return (date - datetime.today()).days

    @staticmethod
    def days_past(date):
        return (datetime.today() - date).days
