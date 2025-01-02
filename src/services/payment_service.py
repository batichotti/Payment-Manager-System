from config import supabase
from models.payment import Payment
from models.backlog import Backlog
from os import getlogin
from platform import platform
from .whatsapp_service import WhatsAppService


class PaymentService:
    @staticmethod
    def fetch_all_payments():
        """Obtém todos os pagamentos visíveis."""
        result = supabase.table("payments").select("*").eq("visible", True).execute()
        return result.data

    @staticmethod
    def add_payment(client_name, phone, amount, due_date):
        """Adiciona um novo pagamento ao banco de dados."""
        payment_data = {
            "client_name": client_name,
            "phone": phone,
            "amount": amount,
            "due_date": due_date,
            "paid": False,
            "visible": True,
        }
        supabase.table("payments").insert(payment_data).execute()
        PaymentService.log_change(None, "Pagamento adicionado: " + str(payment_data))

    @staticmethod
    def mark_payment_as_paid(payment_id):
        """Marca um pagamento como quitado."""
        supabase.table("payments").update({"paid": True}).eq("id", payment_id).execute()
        PaymentService.log_change(payment_id, "Pagamento marcado como quitado.")

    @staticmethod
    def delete_payment(payment_id):
        """Altera a visibilidade de um pagamento para 'invisível'."""
        supabase.table("payments").update({"visible": False}).eq("id", payment_id).execute()
        PaymentService.log_change(payment_id, "Pagamento marcado como invisível.")

    @staticmethod
    def process_payments():
        """Processa os pagamentos para enviar mensagens de cobrança."""
        result = supabase.table("payments").select("*").eq("paid", False).execute()
        payments = result.data

        for payment in payments:
            message = PaymentService.generate_message(payment)
            phone = payment["phone"]

            try:
                WhatsAppService.send_message(phone, message)
                PaymentService.log_change(
                    payment["id"], f"Mensagem de cobrança enviada para {payment['client_name']}."
                )
            except Exception as e:
                PaymentService.log_change(
                    payment["id"], f"Falha ao enviar mensagem para {payment['client_name']}: {str(e)}"
                )

    @staticmethod
    def generate_message(payment):
        """Gera a mensagem de cobrança."""
        client_id = payment["client_id"]
        amount = payment["amount"]
        due_date = payment["due_date"]

        client_result = supabase.table("clients").select("name").eq("id", client_id).execute()
        client_name = client_result.data[0]["name"] if client_result.data else "Cliente"

        if payment["paid"]:
            return f"Olá {client_name}, seu pagamento já está quitado. Obrigado!"
        else:
            return (
                f"Olá {client_name}, lembrete de pagamento:\n"
                f"Valor: R${amount:.2f}\n"
                f"Vencimento: {due_date}\n"
                f"Por favor, efetue o pagamento o quanto antes."
            )

    @staticmethod
    def update_visibility(payment_id, visible):
        """Atualiza a visibilidade de um pagamento."""
        supabase.table("payments").update({"visible": visible}).eq("id", payment_id).execute()
        visibility_status = "visível" if visible else "invisível"
        PaymentService.log_change(payment_id, f"Visibilidade alterada para {visibility_status}.")

    @staticmethod
    def log_change(payment_id, description):
        """Registra alterações no backlog."""
        backlog_entry = {
            "payment_id": payment_id,
            "responsible_user": f"{getlogin()}@{platform()}",
            "description": description,
        }
        supabase.table("backlog").insert(backlog_entry).execute()

    @staticmethod
    def get_backlogs():
        """Obtém todos os registros do backlog."""
        result = supabase.table("backlog").select("*").execute()
        return result.data

    @staticmethod
    def get_backlog_by_payment_id(payment_id):
        """Obtém o backlog relacionado a um pagamento específico."""
        result = supabase.table("backlog").select("*").eq("payment_id", payment_id).execute()
        return result.data
