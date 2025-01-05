import pywhatkit as kit
from datetime import datetime, timedelta
from time import sleep
import webbrowser
import time

def open_whatsapp_web():
    webbrowser.open("https://web.whatsapp.com")
    time.sleep(45)

def send_payment_reminder(payments, method='pywhatkit'):
    if method == 'pywhatkit':
        open_whatsapp_web()
    
    for payment in payments:
        client_name = payment['client_name']
        phone = payment['client_phone']
        if len(phone) <= 11:
            phone = "+55" + phone
        amount = float(payment['amount'])
        due_date = datetime.strptime(payment['due_date'], "%Y-%m-%d")
        today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)

        message = ""
        
        if today > due_date:
            days_late = (today - due_date).days
            late_fee = amount * 0.05
            daily_interest = (amount * 0.03) / 30
            total_interest = daily_interest * days_late
            total_amount = amount + late_fee + total_interest
            message = (f"Olá {client_name}, sua parcela de R${amount:.2f} está atrasada desde {due_date.strftime('%d/%m/%Y')}. "
                       f"Com multa e juros, o valor total é de R${total_amount:.2f}. Por favor, efetue o pagamento o quanto antes.")
        
        elif today == due_date:
            message = f"Olá {client_name}, sua parcela de R${amount:.2f} vence hoje, {due_date.strftime('%d/%m/%Y')}. Por favor, efetue o pagamento."
        
        elif today >= due_date - timedelta(days=3):
            message = f"Olá {client_name}, lembramos que sua parcela de R${amount:.2f} vence em breve, no dia {due_date.strftime('%d/%m/%Y')}."
        
        elif today < due_date:
            message = f"Olá {client_name}, lembramos que sua parcela de R${amount:.2f} vence no dia {due_date.strftime('%d/%m/%Y')}."
        
        # Apenas envia a mensagem se foi criada
        if message:
            if method == 'pywhatkit':
                send_with_pywhatkit(phone, message)
            elif method == 'selenium':
                send_with_selenium(phone, message)
            elif method == 'wa_link':
                send_with_wa_link(phone, message)
            elif method == 'print':
                print_message(phone, message)

def send_with_pywhatkit(phone, message):
    kit.sendwhatmsg_instantly(phone, message, wait_time=10, tab_close=True)

def send_with_selenium(phone, message):
    pass

def send_with_wa_link(phone, message):
    pass

def print_message(phone, message):
    print(f"Phone: {phone}")
    print(f"Message: {message}")

if __name__ == "__main__":
    payments = [
        {
            'client_name': 'John Doe',
            'client_phone': '44998385898',
            'amount': '100.00',
            'due_date': '2024-12-29'
        },
        {
            'client_name': 'Jane Smith',
            'client_phone': '44998385898',
            'amount': '100.00',
            'due_date': '2025-01-04'
        },
        {
            'client_name': 'Alice Johnson',
            'client_phone': '44998385898',
            'amount': '100.00',
            'due_date': '2025-01-05'
        }
    ]
    send_payment_reminder(payments)
