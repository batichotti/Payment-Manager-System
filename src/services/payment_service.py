from config import supabase
from models.payment import Payment
from models.backlog import Backlog
from os import getlogin
from platform import platform

class PaymentService:
    @staticmethod
    def get_due_payments():
        result = supabase.table("payments").select("*").eq("is_paid", False).execute()
        return [Payment.from_db(row) for row in result['data']]

    @staticmethod
    def update_visibility(payment_id, visible):
        supabase.table("payments").update({"visible": visible}).eq("id", payment_id).execute()
        PaymentService.log_change(payment_id, f"Visibilidade alterada para {'visível' if visible else 'invisível'}.")

    @staticmethod
    def mark_payment_as_paid(payment_id):
        supabase.table("payments").update({"is_paid": True}).eq("id", payment_id).execute()
        PaymentService.log_change(payment_id, "Pagamento marcado como quitado.")

    @staticmethod
    def log_change(payment_id, description):
        supabase.table("backlog").insert({
            "payment_id": payment_id,
            "responsible_user": f"{getlogin()}@{platform()}",
            "description": description
        }).execute()

    def get_backlogs():
        result = supabase.table("backlog").select("*").execute()
        return result['data']
    
    def get_backlog_by_payment_id(payment_id):
        result = supabase.table("backlog").select("*").eq("payment_id", payment_id).execute()
        return result['data']