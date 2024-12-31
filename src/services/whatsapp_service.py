import pywhatkit as kit

class WhatsAppService:
    @staticmethod
    def send_message(phone, message):
        kit.sendwhatmsg_instantly(phone, message, wait_time=20)
