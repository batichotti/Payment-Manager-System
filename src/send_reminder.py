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

def send_with_selenium(phone, message):
    driver = webdriver.Chrome()
    driver.get("https://web.whatsapp.com")
    
    # Esperar até que o QR code seja escaneado
    WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, "canvas[aria-label='Scan me!']")))
    print("Please scan the QR code to log in to WhatsApp Web.")
    
    WebDriverWait(driver, 300).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[title='Search input textbox']")))
    print("Logged in to WhatsApp Web.")
    
    for payment in payments:
        phone = payment['client_phone']
        if not phone.startswith("+55"):
            phone = "+55" + phone
        message = payment['message']
        
        # Navegar para o chat do contato
        driver.get(f"https://web.whatsapp.com/send?phone={phone}&text={urllib.parse.quote(message)}")
        
        # Esperar até que o campo de mensagem esteja presente
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[contenteditable='true']")))
        
        # Enviar a mensagem
        input_box = driver.find_element(By.CSS_SELECTOR, "div[contenteditable='true']")
        input_box.send_keys(Keys.ENTER)
        sleep(5)  # Esperar um pouco para garantir que a mensagem foi enviada
    
    driver.quit()

def send_with_pywhatkit(phone, message):
    kit.sendwhatmsg_instantly(phone, message, wait_time=15, tab_close=True)

def send_with_wa_link(phone, message):
    driver = webdriver.Chrome()
    driver.get(f"https://wa.me/{phone}?text={urllib.parse.quote(message)}")
    
    # Esperar até que o botão de enviar esteja presente
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='send']")))
    
    # Clicar no botão de enviar
    send_button = driver.find_element(By.CSS_SELECTOR, "a[href*='send']")
    send_button.click()
    
    # Esperar até que o campo de mensagem esteja presente
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[contenteditable='true']")))
    
    # Enviar a mensagem
    input_box = driver.find_element(By.CSS_SELECTOR, "div[contenteditable='true']")
    input_box.send_keys(Keys.ENTER)
    sleep(5)  # Esperar um pouco para garantir que a mensagem foi enviada
    
    driver.quit()

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
    send_payment_reminder(payments, method='print')
