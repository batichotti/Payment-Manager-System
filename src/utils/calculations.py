class Calculations:
    @staticmethod
    def calculate_fine(amount):
        return amount * 0.05

    @staticmethod
    def calculate_daily_interest(amount, days):
        return (amount * 0.03 / 30) * days
