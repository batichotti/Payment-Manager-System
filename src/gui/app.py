import tkinter as tk
from tkinter import messagebox
from services.payment_service import PaymentService
from services.client_service import ClientService
from services.whatsapp_service import WhatsAppService
from utils.date_utils import DateUtils
from utils.calculations import Calculations

class PaymentProcessor:
    def process_payments(self):
        self.payment_list.config(state=tk.NORMAL)
        self.payment_list.delete("1.0", tk.END)

        payments = PaymentService.get_due_payments()
        if not payments:
            self.payment_list.insert(tk.END, "Nenhum pagamento encontrado.\n")
        else:
            for payment in payments:
                days_until_due = DateUtils.days_until(payment.due_date)
                client = ClientService.get_client_by_id(payment.client_id)
                if not client:
                    continue

                # Mensagens baseadas no status do pagamento
                if days_until_due <= 3 and days_until_due > 0:
                    message = f"Cliente: {client.name} - Parcela de R${payment.amount} vence em {days_until_due} dias.\n"
                elif days_until_due == 0:
                    message = f"Cliente: {client.name} - Parcela de R${payment.amount} vence hoje.\n"
                elif days_until_due < 0:
                    days_late = abs(days_until_due)
                    fine = Calculations.calculate_fine(payment.amount)
                    interest = Calculations.calculate_daily_interest(payment.amount, days_late)
                    corrected_value = payment.amount + fine + interest
                    message = (f"Cliente: {client.name} - Parcela atrasada há {days_late} dias. "
                              f"Valor corrigido: R${corrected_value:.2f}.\n")
                else:
                    continue

                self.payment_list.insert(tk.END, message)

                WhatsAppService.send_message(client.phone, message.strip())
                PaymentService.log_change(payment.id, f"Cobrança enviada: {message.strip()}")

        self.payment_list.config(state=tk.DISABLED)
        messagebox.showinfo("Cobranças Processadas", "Todas as cobranças foram processadas com sucesso!")

class PaymentGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Sistema de Cobranças")

        self.payment_list = tk.Text(self.master, height=15, width=50)
        self.payment_list.pack()

        process_button = tk.Button(self.master, text="Processar Cobranças", command=self.process_payments, width=30, height=2, bg="lightblue")
        process_button.pack()

        mark_paid_button = tk.Button(self.master, text="Marcar como Quitado", command=self.mark_payment_as_paid, width=30, height=2, bg="lightgreen")
        mark_paid_button.pack()

    def process_payments(self):
        payment_processor = PaymentProcessor()
        payment_processor.process_payments()

    def mark_payment_as_paid(self):
        payment_id = self.get_payment_id()
        PaymentService.mark_payment_as_paid(payment_id)
        messagebox.showinfo("Pagamento Quitado", "O pagamento foi marcado como quitado.")

    def get_payment_id(self):
        payment_id = self.payment_list.get("1.0", tk.END).strip().split("\n")[0]
        return int(payment_id) if payment_id.isdigit() else None

if __name__ == "__main__":
    root = tk.Tk()
    app = PaymentGUI(root)
    root.mainloop()
