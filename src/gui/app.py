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

        # Exibição de pagamentos
        self.payment_list = tk.Text(self.master, height=15, width=50)
        self.payment_list.pack()

        # Botões
        process_button = tk.Button(
            self.master,
            text="Processar Cobranças",
            command=self.process_payments,
            width=30,
            height=2,
            bg="lightblue",
        )
        process_button.pack()

        mark_paid_button = tk.Button(
            self.master,
            text="Marcar como Quitado",
            command=self.mark_payment_as_paid,
            width=30,
            height=2,
            bg="lightgreen",
        )
        mark_paid_button.pack()

        add_payment_button = tk.Button(
            self.master,
            text="Adicionar Pagamento",
            command=self.add_payment,
            width=30,
            height=2,
            bg="lightyellow",
        )
        add_payment_button.pack()

        delete_payment_button = tk.Button(
            self.master,
            text="Deletar Pagamento",
            command=self.delete_payment,
            width=30,
            height=2,
            bg="salmon",
        )
        delete_payment_button.pack()

        fetch_button = tk.Button(
            self.master,
            text="Atualizar Lista de Pagamentos",
            command=self.fetch_payments,
            width=30,
            height=2,
            bg="lightgray",
        )
        fetch_button.pack()

        # Inicializa a lista de pagamentos
        self.fetch_payments()

    def fetch_payments(self):
        """Carrega a lista de pagamentos do banco de dados."""
        self.payment_list.delete("1.0", tk.END)
        payments = PaymentService.fetch_all_payments()
        for payment in payments:
            self.payment_list.insert(
                tk.END,
                f"ID: {payment['id']} | Cliente: {payment['client_name']} | Valor: {payment['amount']} | Status: {'Quitado' if payment['paid'] else 'Pendente'} | Visível: {payment['visible']}\n",
            )

    def process_payments(self):
        """Processa as cobranças e envia mensagens pelo WhatsApp."""
        try:
            PaymentService.process_payments()
            messagebox.showinfo("Cobranças", "Cobranças processadas com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao processar cobranças: {e}")

    def mark_payment_as_paid(self):
        """Marca um pagamento como quitado."""
        payment_id = self.get_payment_id()
        if payment_id:
            try:
                PaymentService.mark_payment_as_paid(payment_id)
                messagebox.showinfo("Pagamento Quitado", "O pagamento foi marcado como quitado.")
                self.fetch_payments()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao marcar pagamento como quitado: {e}")
        else:
            messagebox.showwarning("Atenção", "Por favor, selecione um pagamento válido.")

    def add_payment(self):
        """Adiciona um novo pagamento."""
        try:
            client_name = self.prompt_user_input("Nome do Cliente:")
            phone = self.prompt_user_input("Telefone:")
            amount = float(self.prompt_user_input("Valor:"))
            due_date = self.prompt_user_input("Data de Vencimento (YYYY-MM-DD):")

            if client_name and phone and amount and due_date:
                PaymentService.add_payment(client_name, phone, amount, due_date)
                messagebox.showinfo("Adicionar Pagamento", "Pagamento adicionado com sucesso.")
                self.fetch_payments()
            else:
                messagebox.showwarning("Atenção", "Todos os campos são obrigatórios.")
        except ValueError:
            messagebox.showerror("Erro", "Por favor, insira um valor válido.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao adicionar pagamento: {e}")

    def delete_payment(self):
        """Altera a visibilidade de um pagamento para 'invisível'."""
        payment_id = self.get_payment_id()
        if payment_id:
            try:
                PaymentService.delete_payment(payment_id)
                messagebox.showinfo("Deletar Pagamento", "Pagamento marcado como invisível.")
                self.fetch_payments()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao deletar pagamento: {e}")
        else:
            messagebox.showwarning("Atenção", "Por favor, selecione um pagamento válido.")

    def get_payment_id(self):
        """Obtém o ID do pagamento selecionado."""
        try:
            payment_id = self.payment_list.get("1.0", tk.END).strip().split("ID: ")[1].split(" ")[0]
            return int(payment_id)
        except (IndexError, ValueError):
            return None

    def prompt_user_input(self, prompt_text):
        """Exibe um prompt para o usuário inserir informações."""
        return tk.simpledialog.askstring("Entrada", prompt_text)


if __name__ == "__main__":
    root = tk.Tk()
    app = PaymentGUI(root)
    root.mainloop()
