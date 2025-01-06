import tkinter as tk
from os import getlogin
from platform import system, version, processor
from socket import gethostname
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from send_reminder import send_payment_reminder
from supabase_client import supabase
from layout_config import *
from clientcrud import ClientCRUD
from paymentcrud import PaymentCRUD

class PaymentApp:
    """
    Main application class for the Payment Manager System.
    Handles the main window and its components.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Pagamentos")
        self.root.geometry(MAIN_WINDOW_SIZE)
        self.root.resizable(*MAIN_WINDOW_RESIZABLE)
        self.root.configure(bg=WINDOW_BG_COLOR)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.current_page = 0

        self.filter_frame = tk.Frame(self.root, bg=FRAME_BG_COLOR)
        self.filter_frame.pack(pady=PADY)

        self.client_names = self.load_client_names()
        self.combobox_client_filter = ttk.Combobox(self.filter_frame, values=self.client_names, width=28, font=FONT)
        self.combobox_client_filter.grid(row=0, column=1, padx=PADX, pady=PADY)
        self.combobox_client_filter.bind("<KeyRelease>", self.filter_items)

        self.button_send_reminder = tk.Button(self.filter_frame, text="Enviar Cobrança", command=self.send_reminder, font=FONT, bg=SEND_REMINDER_BUTTON_BG_COLOR, fg=BUTTON_FG_COLOR)
        self.button_send_reminder.grid(row=0, column=0, padx=PADX, pady=PADY)

        self.button_filter = tk.Button(self.filter_frame, text="Filtrar por Cliente", command=self.filter_by_client, font=FONT, bg=FILTER_CLIENT_BUTTON_BG_COLOR, fg=BUTTON_FG_COLOR)
        self.button_filter.grid(row=0, column=2, padx=PADX, pady=PADY)

        self.show_paid_var = tk.BooleanVar(value=True)
        self.button_toggle_paid = tk.Button(self.filter_frame, text="Esconder Pagamentos Quitados", command=self.toggle_paid, font=FONT, bg=TOGGLE_PAID_BUTTON_BG_COLOR, fg=BUTTON_FG_COLOR)
        self.button_toggle_paid.grid(row=0, column=3, padx=PADX, pady=PADY)

        self.reminder_within_32_days_var = tk.BooleanVar(value=False)
        self.checkbox_reminder_within_32_days = tk.Checkbutton(self.filter_frame, text="Cobranças até 1 mês", variable=self.reminder_within_32_days_var, bg=FRAME_BG_COLOR, font=FONT)
        self.checkbox_reminder_within_32_days.grid(row=0, column=4, padx=PADX, pady=PADY)

        self.table_frame = tk.Frame(self.root, bg=FRAME_BG_COLOR)
        self.table_frame.pack(fill='both', expand=True, padx=PADX, pady=FRAME_PADY)

        self.table = ttk.Treeview(self.table_frame, columns=("ID", "Cliente", "Telefone", "Valor", "Data de Vencimento", "Pagamento"), show="headings", style="mystyle.Treeview")
        self.table.heading("ID", text="ID", command=lambda: self.sort_table(self.table, "ID"))
        self.table.heading("Cliente", text="Cliente", command=lambda: self.sort_table(self.table, "Cliente"))
        self.table.heading("Telefone", text="Telefone", command=lambda: self.sort_table(self.table, "Telefone"))
        self.table.heading("Valor", text="Valor", command=lambda: self.sort_table(self.table, "Valor"))
        self.table.heading("Data de Vencimento", text="Data de Vencimento", command=lambda: self.sort_table(self.table, "Data de Vencimento"))
        self.table.heading("Pagamento", text="Pagamento", command=lambda: self.sort_table(self.table, "Pagamento"))
        self.table.grid(row=0, column=0, sticky='nsew')

        self.scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.table.yview)
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.table.configure(yscrollcommand=self.scrollbar.set)

        self.table_frame.grid_rowconfigure(0, weight=1)
        self.table_frame.grid_columnconfigure(0, weight=1)

        self.bottom_frame = tk.Frame(self.root, bg=FRAME_BG_COLOR)
        self.bottom_frame.pack(pady=BOTTOM_FRAME_PADY)

        self.button_client_crud = tk.Button(self.bottom_frame, text="Gerenciar Clientes", command=self.open_client_crud, font=FONT, bg=CLIENT_CRUD_BUTTON_BG_COLOR, fg=BUTTON_FG_COLOR)
        self.button_client_crud.grid(row=0, column=0, padx=PADX, pady=PADY)

        self.button_payment_crud = tk.Button(self.bottom_frame, text="Gerenciar Pagamentos", command=self.open_payment_crud, font=FONT, bg=PAYMENT_CRUD_BUTTON_BG_COLOR, fg=BUTTON_FG_COLOR)
        self.button_payment_crud.grid(row=0, column=1, padx=PADX, pady=PADY)

        self.button_refresh = tk.Button(self.bottom_frame, text="Atualizar Lista", command=self.refresh_data, font=FONT, bg=REFRESH_BUTTON_BG_COLOR, fg=BUTTON_FG_COLOR)
        self.button_refresh.grid(row=0, column=2, padx=PADX, pady=PADY)

        self.load_data()
        self.sort_order = {}
        self.user = f"""{getlogin()}@{gethostname()} - {system()} : {version()} - {processor()}"""
        self.root.bind('<Control-a>', self.select_all)

    def on_closing(self):
        """Handle the closing of the main window"""
        if messagebox.askokcancel("Sair", "Tem certeza que deseja fechar o aplicativo? Isso fechará todas as janelas abertas."):
            for window in self.root.winfo_children():
                if isinstance(window, tk.Toplevel):
                    window.destroy()
            self.root.destroy()

    def sort_table(self, table, column):
        """Sort the table based on the clicked column"""
        rows = list(table.get_children())
        if column not in self.sort_order:
            self.sort_order[column] = False  # Default to ascending order

        if column == "Valor":
            rows.sort(key=lambda row: float(table.item(row)["values"][table["columns"].index(column)].replace(',', '')), reverse=self.sort_order[column])
        else:
            rows.sort(key=lambda row: table.item(row)["values"][table["columns"].index(column)], reverse=self.sort_order[column])
        
        for index, row in enumerate(rows):
            table.move(row, '', index)
        
        self.sort_order[column] = not self.sort_order[column]  # Toggle sort order for next click

    def load_data(self):
        """Load payments into the table"""
        for row in self.table.get_children():
            self.table.delete(row)

        payments = supabase.table("payments").select("*").execute()

        self.all_payments = payments.data
        self.display_page(self.current_page)

    def display_page(self, page):
        """Display a specific page of payments in the table"""
        for payment in self.all_payments:
            client = supabase.table("clients").select("name, phone").eq("id", payment['client_id']).execute().data[0]
            is_paid = "Quitado" if payment['is_paid'] else "Pendente"
            try:
                due_date = datetime.strptime(payment['due_date'], "%Y-%m-%d").strftime("%d/%m/%Y")
            except ValueError:
                due_date = "Data inválida"
            amount = f"{float(payment['amount']):.2f}".replace('.', ',')

            if self.show_paid_var.get() or not payment['is_paid']:
                self.table.insert("", "end", values=(payment['id'], client['name'], client['phone'], amount, due_date, is_paid))

    def refresh_data(self):
        """Refresh table data and client combobox"""
        self.load_data()
        self.update_client_combobox()

    def update_client_combobox(self):
        """Update client names in the combobox"""
        self.client_names = self.load_client_names()
        self.combobox_client_filter['values'] = self.client_names

    def open_client_crud(self):
        """Open the client CRUD screen"""
        client_crud = ClientCRUD(self.root, self)
        self.root.wait_window(client_crud.top)
        self.refresh_data()

    def open_payment_crud(self):
        """Open the payment CRUD screen"""
        payment_crud = PaymentCRUD(self.root, self)
        self.root.wait_window(payment_crud.top)
        self.refresh_data()

    def load_client_names(self):
        """Load client names from the database"""
        clients = supabase.table("clients").select("name").execute().data
        return [client['name'] for client in clients]

    def filter_items(self, event):
        """Filter client names in the combobox while typing"""
        query = self.combobox_client_filter.get().lower()
        filtered_names = [name for name in self.client_names if query in name.lower()]
        self.combobox_client_filter['values'] = filtered_names

    def filter_by_client(self):
        """Filter payments by client"""
        client_name = self.combobox_client_filter.get()
        if not client_name:
            messagebox.showerror("Erro", "Selecione um cliente para filtrar.")
            return

        client_id = supabase.table("clients").select("id").eq("name", client_name).execute().data
        if not client_id:
            messagebox.showerror("Erro", "Cliente não encontrado.")
            return

        client_id = client_id[0]['id']
        payments = supabase.table("payments").select("*").eq("client_id", client_id).execute()

        self.all_payments = payments.data
        self.current_page = 0
        
        # Clear the table before displaying filtered payments
        for row in self.table.get_children():
            self.table.delete(row)
        
        self.display_page(self.current_page)

    def toggle_paid(self):
        """Toggle the display of paid payments"""
        self.show_paid_var.set(not self.show_paid_var.get())
        if self.show_paid_var.get():
            self.button_toggle_paid.config(text="Esconder Pagamentos Quitados")
        else:
            self.button_toggle_paid.config(text="Mostrar Pagamentos Quitados")
        self.refresh_data()

    def send_reminder(self):
        """Send reminder to selected clients"""
        selected_items = self.table.selection()
        if not selected_items:
            self.root.lift()
            messagebox.showerror("Erro", "Selecione pelo menos um pagamento para enviar a cobrança.")
            return

        payments = []
        for item in selected_items:
            payment_id = self.table.item(item, 'values')[0]
            payment = supabase.table("payments").select("*").eq("id", payment_id).execute().data[0]
            if payment['is_paid']:
                continue

            if self.reminder_within_32_days_var.get():
                due_date = datetime.strptime(payment['due_date'], "%Y-%m-%d")
                if due_date > datetime.now() + timedelta(days=32):
                    continue

            client = supabase.table("clients").select("name, phone").eq("id", payment['client_id']).execute().data[0]
            
            payment_details = {
                'client_name': client['name'],
                'client_phone': client['phone'],
                'amount': payment['amount'],
                'due_date': payment['due_date']
            }
            payments.append(payment_details)

        if payments:
            send_payment_reminder(payments, method='pywhatkit')
            self.root.lift()
            messagebox.showinfo("Sucesso", "Cobranças enviadas com sucesso.")
            self.log_backlog(f"Sent reminder for payments: {[payment['client_name'] for payment in payments]}")
        else:
            self.root.lift()
            messagebox.showinfo("Informação", "Nenhum pagamento pendente selecionado para cobrança.")

    def log_backlog(self, description):
        """Log a new entry in the backlog table"""
        data = {
            "responsible_user": self.user,
            "description": description
        }
        supabase.table("backlog").insert(data).execute()

    def select_all(self, event):
        """Select all rows in the table"""
        self.table.selection_set(self.table.get_children())

