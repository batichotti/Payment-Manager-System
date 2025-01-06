import re
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime
from supabase_client import supabase
from layout_config import *

class PaymentCRUD:
    """
    Class for managing payment CRUD operations.
    Handles the payment management window and its components.
    """
    def __init__(self, root, app):
        self.app = app
        self.top = tk.Toplevel(root)
        self.top.title("Gerenciar Pagamentos")
        self.top.geometry(PAYMENT_CRUD_WINDOW_SIZE)
        self.top.resizable(*PAYMENT_CRUD_WINDOW_RESIZABLE)

        self.current_page = 0

        self.sort_order = {}

        self.frame_inputs = tk.Frame(self.top)
        self.frame_inputs.pack(pady=20)

        self.label_amount = tk.Label(self.frame_inputs, text="Valor", font=FONT)
        self.label_amount.grid(row=0, column=0, padx=10, pady=10)
        self.entry_amount = tk.Entry(self.frame_inputs, width=30, validate="key", validatecommand=(self.top.register(self.validate_amount), '%P'), font=FONT)
        self.entry_amount.grid(row=0, column=1, padx=10, pady=10)

        self.label_due_date = tk.Label(self.frame_inputs, text="Data de Vencimento", font=FONT)
        self.label_due_date.grid(row=1, column=0, padx=10, pady=10)
        self.entry_due_date = DateEntry(self.frame_inputs, width=30, background='darkblue', foreground='white', borderwidth=2, locale='pt_BR', font=FONT)
        self.entry_due_date.grid(row=1, column=1, padx=10, pady=10)

        self.label_client = tk.Label(self.frame_inputs, text="Cliente", font=FONT)
        self.label_client.grid(row=2, column=0, padx=10, pady=10)
        self.client_names = self.load_client_names()
        self.combobox_client = ttk.Combobox(self.frame_inputs, values=self.client_names, width=28, font=FONT)
        self.combobox_client.grid(row=2, column=1, padx=10, pady=10)
        self.combobox_client.bind("<KeyRelease>", self.filter_items)

        self.button_filter = tk.Button(self.frame_inputs, text="Filtrar por Cliente", command=self.filter_by_client, font=FONT, bg=FILTER_BUTTON_BG_COLOR, fg=BUTTON_FG_COLOR)
        self.button_filter.grid(row=2, column=2, padx=10, pady=10)

        self.frame_buttons = tk.Frame(self.top)
        self.frame_buttons.pack(pady=5)

        self.button_add = tk.Button(self.frame_buttons, text="Adicionar Pagamento", command=self.add_payment, font=FONT, bg=ADD_BUTTON_BG_COLOR, fg=BUTTON_FG_COLOR)
        self.button_add.grid(row=0, column=0, padx=5)

        self.button_delete = tk.Button(self.frame_buttons, text="Excluir Pagamentos", command=lambda: [self.delete_payments(), root.lift()], font=FONT, bg=DELETE_BUTTON_BG_COLOR, fg=BUTTON_FG_COLOR)
        self.button_delete.grid(row=0, column=1, padx=5)

        self.button_edit_client = tk.Button(self.frame_buttons, text="Alterar Cliente", command=self.edit_client, font=FONT, bg=EDIT_BUTTON_BG_COLOR, fg=BUTTON_FG_COLOR)
        self.button_edit_client.grid(row=0, column=2, padx=5)

        self.button_edit = tk.Button(self.frame_buttons, text="Alterar Valor", command=self.edit_payment, font=FONT, bg=EDIT_BUTTON_BG_COLOR, fg=BUTTON_FG_COLOR)
        self.button_edit.grid(row=0, column=3, padx=5)

        self.button_edit_due_date = tk.Button(self.frame_buttons, text="Alterar Data", command=self.edit_due_date, font=FONT, bg=EDIT_BUTTON_BG_COLOR, fg=BUTTON_FG_COLOR)
        self.button_edit_due_date.grid(row=0, column=4, padx=5)

        self.button_change_status = tk.Button(self.frame_buttons, text="Alterar Status", command=self.change_status, font=FONT, bg=EDIT_BUTTON_BG_COLOR, fg=BUTTON_FG_COLOR)
        self.button_change_status.grid(row=0, column=5, padx=5)

        self.button_refresh = tk.Button(self.top, text="Atualizar Lista", command=self.load_payments, font=FONT, bg=FILTER_BUTTON_BG_COLOR, fg=BUTTON_FG_COLOR)
        self.button_refresh.pack(pady=5)

        self.payment_table_frame = tk.Frame(self.top)
        self.payment_table_frame.pack(fill='both', expand=True, padx=10, pady=10)

        self.payment_table = ttk.Treeview(self.payment_table_frame, columns=("ID", "Cliente", "Valor", "Data de Vencimento", "Status"), show="headings", selectmode="extended", style="mystyle.Treeview")
        self.payment_table.heading("ID", text="ID", command=lambda: self.sort_table(self.payment_table, "ID"))
        self.payment_table.heading("Cliente", text="Cliente", command=lambda: self.sort_table(self.payment_table, "Cliente"))
        self.payment_table.heading("Valor", text="Valor", command=lambda: self.sort_table(self.payment_table, "Valor"))
        self.payment_table.heading("Data de Vencimento", text="Data de Vencimento", command=lambda: self.sort_table(self.payment_table, "Data de Vencimento"))
        self.payment_table.heading("Status", text="Status", command=lambda: self.sort_table(self.payment_table, "Status"))

        self.payment_table.column("ID", width=60, anchor="center")
        self.payment_table.column("Cliente", width=200, anchor="w")
        self.payment_table.column("Valor", width=160, anchor="center")
        self.payment_table.column("Data de Vencimento", width=150, anchor="center")
        self.payment_table.column("Status", width=100, anchor="center")

        self.payment_table.grid(row=0, column=0, sticky='nsew')

        self.payment_table_frame.grid_rowconfigure(0, weight=1)
        self.payment_table_frame.grid_columnconfigure(0, weight=1)

        self.payment_table_scrollbar = ttk.Scrollbar(self.payment_table_frame, orient="vertical", command=self.payment_table.yview)
        self.payment_table_scrollbar.grid(row=0, column=1, sticky="ns")
        self.payment_table.configure(yscrollcommand=self.payment_table_scrollbar.set)

        self.payment_table.bind('<<TreeviewSelect>>', self.on_select)

        self.show_paid_var = tk.BooleanVar(value=True)
        self.button_toggle_paid = tk.Button(self.top, text="Esconder Pagamentos Quitados", command=self.toggle_paid, font=FONT, bg=TOGGLE_BUTTON_BG_COLOR, fg=BUTTON_FG_COLOR)
        self.button_toggle_paid.pack(pady=5)

        self.top.bind('<Control-a>', self.select_all)

        self.load_payments()

    def validate_amount(self, new_value):
        """Validate the amount input to accept only numbers and up to two decimal places"""
        if not new_value:
            return True
        try:
            new_value = new_value.replace(',', '.')
            float_value = float(new_value)
            if float_value < 0:
                return False
            parts = new_value.split('.')
            if len(parts) > 2 or (len(parts) == 2 and len(parts[1]) > 2):
                return False
            return True
        except ValueError:
            return False

    def load_client_names(self):
        """Load client names from the database"""
        clients = supabase.table("clients").select("name").execute().data
        return [client['name'] for client in clients]

    def filter_items(self, event):
        """Filter client names in the combobox while typing"""
        query = self.combobox_client.get().lower()
        filtered_names = [name for name in self.client_names if query in name.lower()]
        self.combobox_client['values'] = filtered_names

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

    def load_payments(self):
        """Load payments into the table"""
        for row in self.payment_table.get_children():
            self.payment_table.delete(row)

        payments = supabase.table("payments").select("*").execute()

        self.all_payments = payments.data
        self.display_page(self.current_page)

    def display_page(self, page):
        """Display a specific page of payments in the table"""
        for payment in self.all_payments:
            client = supabase.table("clients").select("name").eq("id", payment['client_id']).execute().data[0]
            status = "Quitado" if payment['is_paid'] else "Pendente"
            try:
                due_date = datetime.strptime(payment['due_date'], "%Y-%m-%d").strftime("%d/%m/%Y")
            except ValueError:
                due_date = "Data inválida"
            amount = f"{float(payment['amount']):.2f}".replace('.', ',')

            if self.show_paid_var.get() or not payment['is_paid']:
                self.payment_table.insert("", "end", values=(payment['id'], client['name'], amount, due_date, status))

    def add_payment(self):
        """Add a payment"""
        amount = self.entry_amount.get().replace(',', '.')
        due_date = self.entry_due_date.get_date()
        client_name = self.combobox_client.get()

        if not amount or not due_date or not client_name:
            self.top.lift()
            self.show_messagebox("Erro", "Preencha todos os campos.")
            return

        client_id = supabase.table("clients").select("id").eq("name", client_name).execute().data[0]['id']
        due_date_str = due_date.strftime("%Y-%m-%d")

        data = {"amount": float(amount), "due_date": due_date_str, "client_id": client_id, "is_paid": False}
        supabase.table("payments").insert(data).execute()

        self.entry_amount.delete(0, tk.END)
        self.entry_due_date.set_date(None)
        self.combobox_client.set('')

        self.load_payments()
        self.app.log_backlog(f"Added payment: Amount {amount} for client ID {client_id}")

    def edit_payment(self):
        """Edit the selected payment amount"""
        selected_items = self.payment_table.selection()
        if len(selected_items) != 1:
            self.top.lift()
            self.show_messagebox("Erro", "Selecione exatamente um pagamento para editar.")
            return

        payment_id = self.payment_table.item(selected_items[0], 'values')[0]
        amount = self.entry_amount.get().replace(',', '.')

        if not amount:
            self.top.lift()
            self.show_messagebox("Erro", "Preencha o valor do pagamento.")
            return

        old_amount = self.payment_table.item(selected_items[0], 'values')[2]
        data = {"amount": float(amount)}
        supabase.table("payments").update(data).eq("id", payment_id).execute()

        self.load_payments()
        self.app.log_backlog(f"Edited payment: ID {payment_id}, from {old_amount} to {amount}")

    def edit_client(self):
        """Edit the client of the selected payment"""
        selected_items = self.payment_table.selection()
        if len(selected_items) != 1:
            self.top.lift()
            self.show_messagebox("Erro", "Selecione exatamente um pagamento para editar.")
            return

        payment_id = self.payment_table.item(selected_items[0], 'values')[0]
        client_name = self.combobox_client.get()

        if not client_name:
            self.top.lift()
            self.show_messagebox("Erro", "Preencha o nome do cliente.")
            return

        old_client_id = self.payment_table.item(selected_items[0], 'values')[1]
        old_client_name = supabase.table("clients").select("name").eq("id", old_client_id).execute().data[0]['name']
        client_id = supabase.table("clients").select("id").eq("name", client_name).execute().data[0]['id']
        new_client_name = supabase.table("clients").select("name").eq("id", client_id).execute().data[0]['name']
        data = {"client_id": client_id}
        supabase.table("payments").update(data).eq("id", payment_id).execute()

        self.load_payments()
        self.app.log_backlog(f"Edited payment client: ID {payment_id}, from {old_client_name} (ID {old_client_id}) to {new_client_name} (ID {client_id})")

    def edit_due_date(self):
        """Edit the due date of the selected payment"""
        selected_items = self.payment_table.selection()
        if len(selected_items) != 1:
            self.top.lift()
            self.show_messagebox("Erro", "Selecione exatamente um pagamento para editar.")
            return

        payment_id = self.payment_table.item(selected_items[0], 'values')[0]
        due_date = self.entry_due_date.get_date()

        if not due_date:
            self.top.lift()
            self.show_messagebox("Erro", "Preencha a data de vencimento.")
            return

        old_due_date = self.payment_table.item(selected_items[0], 'values')[3]
        due_date_str = due_date.strftime("%Y-%m-%d")
        data = {"due_date": due_date_str}
        supabase.table("payments").update(data).eq("id", payment_id).execute()

        self.load_payments()
        self.app.log_backlog(f"Edited payment due date: ID {payment_id}, from {old_due_date} to {due_date_str}")

    def delete_payments(self):
        """Delete selected payments"""
        selected_items = self.payment_table.selection()
        if not selected_items:
            self.top.lift()
            self.show_messagebox("Erro", "Selecione ao menos um pagamento para excluir.")
            return

        confirm = messagebox.askyesno("Excluir", "Tem certeza que deseja excluir os pagamentos selecionados?")
        if not confirm:
            return

        for selected_item in selected_items:
            payment_id = self.payment_table.item(selected_item, 'values')[0]
            client_id = self.payment_table.item(selected_item, 'values')[1]
            client_name = supabase.table("clients").select("name").eq("id", client_id).execute().data[0]['name']
            supabase.table("payments").delete().eq("id", payment_id).execute()
            self.app.log_backlog(f"Deleted payment: ID {payment_id} for client {client_name} (ID {client_id})")

        self.load_payments()

    def change_status(self):
        """Change the status of the selected payment"""
        selected_items = self.payment_table.selection()
        if len(selected_items) != 1:
            self.top.lift()
            self.show_messagebox("Erro", "Selecione exatamente um pagamento para alterar o status.")
            return

        payment_id = self.payment_table.item(selected_items[0], 'values')[0]
        current_status = self.payment_table.item(selected_items[0], 'values')[4]

        new_status = "Pendente" if current_status == "Quitado" else "Quitado"
        is_paid = new_status == "Quitado"

        supabase.table("payments").update({"is_paid": is_paid}).eq("id", payment_id).execute()
        self.load_payments()
        self.app.log_backlog(f"Changed payment status: ID {payment_id}, from {current_status} to {new_status}")

    def on_select(self, event):
        """Action when selecting a payment"""
        selected_items = self.payment_table.selection()
        if len(selected_items) == 1:
            self.button_edit.config(state="normal")
            self.button_edit_client.config(state="normal")
            self.button_edit_due_date.config(state="normal")
            self.button_delete.config(state="normal")
            self.button_change_status.config(state="normal")
        else:
            self.button_edit.config(state="disabled")
            self.button_edit_client.config(state="disabled")
            self.button_edit_due_date.config(state="disabled")
            self.button_change_status.config(state="disabled")

    def filter_by_client(self):
        """Filter payments by client"""
        client_name = self.combobox_client.get()
        if not client_name:
            self.top.lift()
            self.show_messagebox("Erro", "Selecione um cliente para filtrar.")
            return

        client_id = supabase.table("clients").select("id").eq("name", client_name).execute().data[0]['id']
        payments = supabase.table("payments").select("*").eq("client_id", client_id).execute()

        self.all_payments = payments.data
        self.current_page = 0
        self.display_page(self.current_page)

    def toggle_paid(self):
        """Toggle the display of paid payments"""
        self.show_paid_var.set(not self.show_paid_var.get())
        if self.show_paid_var.get():
            self.button_toggle_paid.config(text="Esconder Pagamentos Quitados")
        else:
            self.button_toggle_paid.config(text="Mostrar Pagamentos Quitados")
        self.load_payments()

    def select_all(self, event):
        """Select all rows in the table"""
        self.payment_table.selection_set(self.payment_table.get_children())

    def show_messagebox(self, title, message, icon=messagebox.ERROR):
        """Show a messagebox and keep the CRUD window in front"""
        self.top.lift()
        messagebox.showerror(title, message, parent=self.top)