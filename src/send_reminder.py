import pywhatkit as kit
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import urllib.parse

def send_payment_reminder(payments, method='selenium'):
    for payment in payments:
        client_name = payment['client_name']
        phone = payment['client_phone']
        if not phone.startswith("+55"):
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
    kit.sendwhatmsg_instantly(phone, message, wait_time=20)

def send_with_selenium(phone, message):
    driver = webdriver.Chrome()
    driver.get("https://web.whatsapp.com")
    input("Escaneie o QR Code e pressione Enter.")

    try:
        # Wait for the search box to be clickable
        search_box = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]'))
        )
        search_box.click()
        search_box.send_keys(phone)
        search_box.send_keys(Keys.ENTER)

        # Wait for the message box to be clickable
        message_box = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, '//div[@contenteditable="true"][@data-tab="6"]'))
        )
        message_box.click()
        message_box.send_keys(message)
        message_box.send_keys(Keys.ENTER)

        sleep(5)  # Wait for the message to be sent
    finally:
        driver.quit()

def send_with_wa_link(phone, message):
    driver = webdriver.Chrome()
    driver.get("https://web.whatsapp.com")
    input("Escaneie o QR Code e pressione Enter.")

    try:
        encoded_message = urllib.parse.quote(message)
        wa_link = f"https://wa.me/{phone}?text={encoded_message}"
        driver.get(wa_link)

        # Wait for the send button to be clickable
        send_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, '//button[@data-testid="compose-btn-send"]'))
        )
        send_button.click()

        sleep(5)  # Wait for the message to be sent
    finally:
        driver.quit()

def print_message(phone, message):
    print(f"Phone: {phone}")
    print(f"Message: {message}")

if __name__ == "__main__":
    payments = [
        {
            'client_name': 'John Doe',
            'client_phone': '1234567890',
            'amount': '100.00',
            'due_date': '2024-12-29'
        },
        {
            'client_name': 'Jane Smith',
            'client_phone': '0987654321',
            'amount': '100.00',
            'due_date': '2025-01-04'
        },
        {
            'client_name': 'Alice Johnson',
            'client_phone': '1122334455',
            'amount': '100.00',
            'due_date': '2025-01-05'
        }
    ]
    send_payment_reminder(payments, method='print')
