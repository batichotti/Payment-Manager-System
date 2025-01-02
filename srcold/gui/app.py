import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
from services.payment_service import PaymentService
from services.client_service import ClientService
from services.whatsapp_service import WhatsAppService
from utils.date_utils import DateUtils
from utils.calculations import Calculations

class PaymentProcessor:
    def process_payments(self):
        self.payment_list.config(state=tk.NORMAL)
        self.payment_list.delete(*self.payment_list.get_children())

        payments = PaymentService.get_due_payments()
        if not payments:
            self.payment_list.insert("", "end", values=("Nenhum pagamento encontrado.",))
        else:
            for payment in payments:
                days_until_due = DateUtils.days_until(payment.due_date)
                client = ClientService.get_client_by_id(payment.client_id)
                if not client:
                    continue

                if days_until_due <= 3 and days_until_due > 0:
                    message = f"Cliente: {client.name} - Parcela de R${payment.amount} vence em {days_until_due} dias."
                elif days_until_due == 0:
                    message = f"Cliente: {client.name} - Parcela de R${payment.amount} vence hoje."
                elif days_until_due < 0:
                    days_late = abs(days_until_due)
                    fine = Calculations.calculate_fine(payment.amount)
                    interest = Calculations.calculate_daily_interest(payment.amount, days_late)
                    corrected_value = payment.amount + fine + interest
                    message = (f"Cliente: {client.name} - Parcela atrasada há {days_late} dias. "
                              f"Valor corrigido: R${corrected_value:.2f}.")
                else:
                    continue

                self.payment_list.insert("", "end", values=(payment.id, client.name, payment.amount, message))

                WhatsAppService.send_message(client.phone, message.strip())
                PaymentService.log_change(payment.id, f"Cobrança enviada: {message.strip()}")

        self.payment_list.config(state=tk.DISABLED)
        messagebox.showinfo("Cobranças Processadas", "Todas as cobranças foram processadas com sucesso!")


class PaymentGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Sistema de Cobranças")
        self.master.resizable(False, False)

        # Título
        title_label = tk.Label(self.master, text="Gestão de Pagamentos", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=4, pady=10)

        # Tabela de pagamentos
        self.payment_list = ttk.Treeview(self.master, columns=("ID", "Cliente", "Valor", "Mensagem"), show="headings", height=15)
        self.payment_list.heading("ID", text="ID")
        self.payment_list.heading("Cliente", text="Cliente")
        self.payment_list.heading("Valor", text="Valor")
        self.payment_list.heading("Mensagem", text="Mensagem")
        self.payment_list.grid(row=1, column=0, columnspan=4, padx=10, pady=10)

        # Barra de rolagem
        scrollbar = tk.Scrollbar(self.master, orient="vertical", command=self.payment_list.yview)
        scrollbar.grid(row=1, column=4, sticky="ns", padx=5)
        self.payment_list.config(yscrollcommand=scrollbar.set)

        # Botões
        button_frame = tk.Frame(self.master)
        button_frame.grid(row=2, column=0, columnspan=4, pady=10)

        process_button = tk.Button(button_frame, text="Processar Cobranças", command=self.process_payments, width=20, height=2, bg="lightblue")
        process_button.grid(row=0, column=0, padx=5, sticky="ew")

        mark_paid_button = tk.Button(button_frame, text="Marcar como Quitado", command=self.mark_payment_as_paid, width=20, height=2, bg="lightgreen")
        mark_paid_button.grid(row=0, column=1, padx=5, sticky="ew")

        add_payment_button = tk.Button(button_frame, text="Adicionar Pagamento", command=self.add_payment, width=20, height=2, bg="lightyellow")
        add_payment_button.grid(row=0, column=2, padx=5, sticky="ew")

        delete_payment_button = tk.Button(button_frame, text="Deletar Pagamento", command=self.delete_payment, width=20, height=2, bg="salmon")
        delete_payment_button.grid(row=0, column=3, padx=5, sticky="ew")

        fetch_button = tk.Button(button_frame, text="Atualizar Lista de Pagamentos", command=self.fetch_payments, width=20, height=2, bg="lightgray")
        fetch_button.grid(row=1, column=0, columnspan=4, pady=5, sticky="ew")

        self.fetch_payments()

    def fetch_payments(self):
        """Carrega a lista de pagamentos do banco de dados."""
        for row in self.payment_list.get_children():
            self.payment_list.delete(row)
        payments = PaymentService.fetch_all_payments()
        for payment in payments:
            client = ClientService.get_client_by_id(payment['client_id'])
            self.payment_list.insert(
                "",
                "end",
                values=(payment['id'], client.name, payment['amount'], "Quitado" if payment['is_paid'] else "Pendente"),
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
            selected_item = self.payment_list.selection()[0]
            payment_id = self.payment_list.item(selected_item, "values")[0]
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
