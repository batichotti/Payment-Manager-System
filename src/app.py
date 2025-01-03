import os
import tkinter as tk
from tkinter import ttk, messagebox
from dotenv import load_dotenv
from supabase import create_client, Client
from tkcalendar import DateEntry

# Carregar variáveis de ambiente
load_dotenv()

# Obter URL e chave do Supabase
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

# Criar cliente Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class PaymentApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Pagamentos")
        self.root.geometry("1400x600")  # Define a geometria fixa

        # Tabela para exibir pagamentos
        self.table_frame = tk.Frame(self.root)
        self.table_frame.pack(fill='both', expand=True, padx=10, pady=20)

        self.table = ttk.Treeview(self.table_frame, columns=("ID", "Cliente", "Telefone", "Valor", "Data de Vencimento", "Pagamento"), show="headings")
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

        # Configura a expansão da tabela
        self.table_frame.grid_rowconfigure(0, weight=1)
        self.table_frame.grid_columnconfigure(0, weight=1)

        # Carregar dados na tabela de pagamentos
        self.load_data()

        # Frame superior com botões
        self.top_frame = tk.Frame(self.root)
        self.top_frame.pack(pady=10)

        # Botões de CRUD
        self.button_client_crud = tk.Button(self.top_frame, text="Gerenciar Clientes", command=self.open_client_crud)
        self.button_client_crud.grid(row=0, column=0, padx=10, pady=10)

        self.button_payment_crud = tk.Button(self.top_frame, text="Gerenciar Pagamentos", command=self.open_payment_crud)
        self.button_payment_crud.grid(row=0, column=1, padx=10, pady=10)

        # Botão para atualizar lista
        self.button_refresh = tk.Button(self.top_frame, text="Atualizar Lista", command=self.load_data)
        self.button_refresh.grid(row=0, column=2, padx=10, pady=10)

    def sort_table(self, table, column):
        """Ordenar a tabela com base na coluna clicada"""
        rows = list(table.get_children())
        rows.sort(key=lambda row: table.item(row)["values"][table["columns"].index(column)])
        
        for index, row in enumerate(rows):
            table.move(row, '', index)

    def load_data(self):
        """Carregar pagamentos na tabela"""
        for row in self.table.get_children():
            self.table.delete(row)

        # Obter os dados dos clientes e pagamentos
        payments = supabase.table("payments").select("*").execute()

        for payment in payments.data:
            client = supabase.table("clients").select("name, phone").eq("id", payment['client_id']).execute().data[0]
            # Ajuste na exibição de 'Pago': 'Quitado' para True e 'Pendente' para False
            is_paid = "Quitado" if payment['is_paid'] else "Pendente"
            self.table.insert("", "end", values=(payment['id'], client['name'], client['phone'], payment['amount'], payment['due_date'], is_paid))

    def open_client_crud(self):
        """Abrir a tela de CRUD de clientes"""
        ClientCRUD(self.root, self)

    def open_payment_crud(self):
        """Abrir a tela de CRUD de pagamentos"""
        PaymentCRUD(self.root, self)

class ClientCRUD:
    def __init__(self, root, app):
        self.app = app
        self.top = tk.Toplevel(root)
        self.top.title("Gerenciar Clientes")
        self.top.geometry("600x400")

        self.frame_inputs = tk.Frame(self.top)
        self.frame_inputs.pack(pady=20)

        # Campos de entrada para cliente
        self.label_name = tk.Label(self.frame_inputs, text="Nome do Cliente")
        self.label_name.grid(row=0, column=0, padx=10, pady=10)
        self.entry_name = tk.Entry(self.frame_inputs, width=30)
        self.entry_name.grid(row=0, column=1, padx=10, pady=10)

        self.label_phone = tk.Label(self.frame_inputs, text="Telefone")
        self.label_phone.grid(row=1, column=0, padx=10, pady=10)
        self.entry_phone = tk.Entry(self.frame_inputs, width=30)
        self.entry_phone.grid(row=1, column=1, padx=10, pady=10)

        # Botões de CRUD
        self.button_add = tk.Button(self.top, text="Adicionar Cliente", command=self.add_client)
        self.button_add.pack(pady=5)

        self.button_edit = tk.Button(self.top, text="Editar Cliente", command=self.edit_client)
        self.button_edit.pack(pady=5)

        self.button_delete = tk.Button(self.top, text="Excluir Clientes", command=self.delete_clients)
        self.button_delete.pack(pady=5)

        # Botão para atualizar lista
        self.button_refresh = tk.Button(self.top, text="Atualizar Lista", command=self.load_clients)
        self.button_refresh.pack(pady=5)

        # Tabela de clientes
        self.client_table_frame = tk.Frame(self.top)
        self.client_table_frame.pack(fill='both', expand=True, padx=10, pady=10)

        self.client_table_canvas = tk.Canvas(self.client_table_frame)
        self.client_table_canvas.grid(row=0, column=0)

        self.client_table = ttk.Treeview(self.client_table_canvas, columns=("ID", "Nome", "Telefone"), show="headings", selectmode="extended")
        self.client_table.heading("ID", text="ID", command=lambda: self.sort_table(self.client_table, "ID"))
        self.client_table.heading("Nome", text="Nome", command=lambda: self.sort_table(self.client_table, "Nome"))
        self.client_table.heading("Telefone", text="Telefone", command=lambda: self.sort_table(self.client_table, "Telefone"))
        
        self.client_table.column("ID", width=50, anchor="center")
        self.client_table.column("Nome", width=200, anchor="w")
        self.client_table.column("Telefone", width=150, anchor="center")

        self.client_table.grid(row=0, column=0, sticky='nsew')

        self.client_table_frame.grid_rowconfigure(0, weight=1)
        self.client_table_frame.grid_columnconfigure(0, weight=1)

        self.client_table_scrollbar = ttk.Scrollbar(self.client_table_frame, orient="vertical", command=self.client_table_canvas.yview)
        self.client_table_scrollbar.grid(row=0, column=1, sticky="ns")
        self.client_table_canvas.configure(yscrollcommand=self.client_table_scrollbar.set)

        self.client_table_canvas.create_window((0, 0), window=self.client_table, anchor="nw")

        self.client_table.bind('<<TreeviewSelect>>', self.on_select)

        self.load_clients()

    def sort_table(self, table, column):
        """Ordenar a tabela com base na coluna clicada"""
        rows = list(table.get_children())
        rows.sort(key=lambda row: table.item(row)["values"][table["columns"].index(column)])
        
        for index, row in enumerate(rows):
            table.move(row, '', index)

    def load_clients(self):
        """Carregar clientes na tabela"""
        for row in self.client_table.get_children():
            self.client_table.delete(row)

        clients = supabase.table("clients").select("*").execute()

        for client in clients.data:
            self.client_table.insert("", "end", values=(client['id'], client['name'], client['phone']))

    def add_client(self):
        """Adicionar cliente"""
        name = self.entry_name.get()
        phone = self.entry_phone.get()

        if not name or not phone:
            messagebox.showerror("Erro", "Preencha todos os campos.")
            return

        data = {"name": name, "phone": phone}
        supabase.table("clients").insert(data).execute()

        self.entry_name.delete(0, tk.END)
        self.entry_phone.delete(0, tk.END)

        self.load_clients()

    def edit_client(self):
        """Editar cliente selecionado"""
        selected_items = self.client_table.selection()
        if len(selected_items) != 1:
            messagebox.showerror("Erro", "Selecione apenas um cliente para editar.")
            return
        
        selected_item = selected_items[0]
        client_id = self.client_table.item(selected_item, 'values')[0]
        client = supabase.table("clients").select("*").eq("id", client_id).execute().data[0]

        self.entry_name.delete(0, tk.END)
        self.entry_phone.delete(0, tk.END)

        self.entry_name.insert(0, client["name"])
        self.entry_phone.insert(0, client["phone"])

        self.button_add.config(text="Salvar Alterações", command=lambda: self.save_changes(client_id))

    def save_changes(self, client_id):
        """Salvar as alterações feitas no cliente"""
        name = self.entry_name.get()
        phone = self.entry_phone.get()

        if not name or not phone:
            messagebox.showerror("Erro", "Preencha todos os campos.")
            return

        supabase.table("clients").update({"name": name, "phone": phone}).eq("id", client_id).execute()
        self.load_clients()

        self.entry_name.delete(0, tk.END)
        self.entry_phone.delete(0, tk.END)

        self.button_add.config(text="Adicionar Cliente", command=self.add_client)

    def delete_clients(self):
        """Excluir clientes selecionados"""
        selected_items = self.client_table.selection()
        if not selected_items:
            messagebox.showerror("Erro", "Selecione ao menos um cliente para excluir.")
            return

        confirm = messagebox.askyesno("Excluir", "Tem certeza que deseja excluir os clientes selecionados?")
        if not confirm:
            return

        for selected_item in selected_items:
            client_id = self.client_table.item(selected_item, 'values')[0]
            supabase.table("clients").delete().eq("id", client_id).execute()

        self.load_clients()

    def on_select(self, event):
        """Ação ao selecionar um cliente"""
        selected_items = self.client_table.selection()
        if selected_items:
            self.button_edit.config(state="normal")
            self.button_delete.config(state="normal")
        else:
            self.button_edit.config(state="disabled")
            self.button_delete.config(state="disabled")

class PaymentCRUD:
    def __init__(self, root, app):
        self.app = app
        self.top = tk.Toplevel(root)
        self.top.title("Gerenciar Pagamentos")
        self.top.geometry("800x400")  # Ajuste a largura da janela conforme necessário

        self.frame_inputs = tk.Frame(self.top)
        self.frame_inputs.pack(pady=20)

        # Campos de entrada para pagamento
        self.label_amount = tk.Label(self.frame_inputs, text="Valor")
        self.label_amount.grid(row=0, column=0, padx=10, pady=10)
        self.entry_amount = tk.Entry(self.frame_inputs, width=30)
        self.entry_amount.grid(row=0, column=1, padx=10, pady=10)

        self.label_due_date = tk.Label(self.frame_inputs, text="Data de Vencimento")
        self.label_due_date.grid(row=1, column=0, padx=10, pady=10)
        self.entry_due_date = DateEntry(self.frame_inputs, width=30, background='darkblue', foreground='white', borderwidth=2)
        self.entry_due_date.grid(row=1, column=1, padx=10, pady=10)

        self.label_client = tk.Label(self.frame_inputs, text="ID do Cliente")
        self.label_client.grid(row=2, column=0, padx=10, pady=10)
        self.entry_client = tk.Entry(self.frame_inputs, width=30)
        self.entry_client.grid(row=2, column=1, padx=10, pady=10)

        # Botões de CRUD
        self.button_add = tk.Button(self.top, text="Adicionar Pagamento", command=self.add_payment)
        self.button_add.pack(pady=5)

        self.button_edit = tk.Button(self.top, text="Editar Pagamento", command=self.edit_payment)
        self.button_edit.pack(pady=5)

        self.button_delete = tk.Button(self.top, text="Excluir Pagamentos", command=self.delete_payments)
        self.button_delete.pack(pady=5)

        # Botão para atualizar lista
        self.button_refresh = tk.Button(self.top, text="Atualizar Lista", command=self.load_payments)
        self.button_refresh.pack(pady=5)

        # Tabela de pagamentos
        self.payment_table_frame = tk.Frame(self.top)
        self.payment_table_frame.pack(fill='both', expand=True, padx=10, pady=10)

        self.payment_table_canvas = tk.Canvas(self.payment_table_frame)
        self.payment_table_canvas.grid(row=0, column=0, sticky='nsew')

        self.payment_table = ttk.Treeview(self.payment_table_canvas, columns=("ID", "Cliente", "Valor", "Data de Vencimento", "Status"), show="headings", selectmode="extended")
        self.payment_table.heading("ID", text="ID", command=lambda: self.sort_table(self.payment_table, "ID"))
        self.payment_table.heading("Cliente", text="Cliente", command=lambda: self.sort_table(self.payment_table, "Cliente"))
        self.payment_table.heading("Valor", text="Valor", command=lambda: self.sort_table(self.payment_table, "Valor"))
        self.payment_table.heading("Data de Vencimento", text="Data de Vencimento", command=lambda: self.sort_table(self.payment_table, "Data de Vencimento"))
        self.payment_table.heading("Status", text="Status", command=lambda: self.sort_table(self.payment_table, "Status"))

        # Ajustar o tamanho das colunas para torná-las visíveis
        self.payment_table.column("ID", width=50, anchor="center")
        self.payment_table.column("Cliente", width=250, anchor="w")
        self.payment_table.column("Valor", width=150, anchor="center")
        self.payment_table.column("Data de Vencimento", width=150, anchor="center")
        self.payment_table.column("Status", width=150, anchor="center")

        self.payment_table.grid(row=0, column=0, sticky='nsew')

        self.payment_table_frame.grid_rowconfigure(0, weight=1)
        self.payment_table_frame.grid_columnconfigure(0, weight=1)

        self.payment_table_scrollbar = ttk.Scrollbar(self.payment_table_frame, orient="vertical", command=self.payment_table_canvas.yview)
        self.payment_table_scrollbar.grid(row=0, column=1, sticky="ns")
        self.payment_table_canvas.configure(yscrollcommand=self.payment_table_scrollbar.set)

        self.payment_table_canvas.create_window((0, 0), window=self.payment_table, anchor="nw")

        self.payment_table.bind('<<TreeviewSelect>>', self.on_select)

        self.load_payments()

    def sort_table(self, table, column):
        """Ordenar a tabela com base na coluna clicada"""
        rows = list(table.get_children())
        rows.sort(key=lambda row: table.item(row)["values"][table["columns"].index(column)])
        
        for index, row in enumerate(rows):
            table.move(row, '', index)

    def load_payments(self):
        """Carregar pagamentos na tabela"""
        for row in self.payment_table.get_children():
            self.payment_table.delete(row)

        payments = supabase.table("payments").select("*").execute()

        for payment in payments.data:
            client = supabase.table("clients").select("name").eq("id", payment['client_id']).execute().data[0]
            status = "Pago" if payment['is_paid'] else "Pendente"
            self.payment_table.insert("", "end", values=(payment['id'], client['name'], payment['amount'], payment['due_date'], status))

    def add_payment(self):
        """Adicionar pagamento"""
        amount = self.entry_amount.get()
        due_date = self.entry_due_date.get_date()
        client_id = self.entry_client.get()

        if not amount or not due_date or not client_id:
            messagebox.showerror("Erro", "Preencha todos os campos.")
            return

        data = {"amount": amount, "due_date": due_date, "client_id": client_id, "is_paid": False}
        supabase.table("payments").insert(data).execute()

        self.entry_amount.delete(0, tk.END)
        self.entry_due_date.set_date('')
        self.entry_client.delete(0, tk.END)

        self.load_payments()

    def edit_payment(self):
        """Editar pagamento selecionado"""
        selected_items = self.payment_table.selection()
        if len(selected_items) != 1:
            messagebox.showerror("Erro", "Selecione apenas um pagamento para editar.")
            return
        
        selected_item = selected_items[0]
        payment_id = self.payment_table.item(selected_item, 'values')[0]
        payment = supabase.table("payments").select("*").eq("id", payment_id).execute().data[0]

        self.entry_amount.delete(0, tk.END)
        self.entry_due_date.set_date('')
        self.entry_client.delete(0, tk.END)

        self.entry_amount.insert(0, payment["amount"])
        self.entry_due_date.set_date(payment["due_date"])
        self.entry_client.insert(0, payment["client_id"])

        self.button_add.config(text="Salvar Alterações", command=lambda: self.save_changes(payment_id))

    def save_changes(self, payment_id):
        """Salvar as alterações feitas no pagamento"""
        amount = self.entry_amount.get()
        due_date = self.entry_due_date.get_date()
        client_id = self.entry_client.get()

        if not amount or not due_date or not client_id:
            messagebox.showerror("Erro", "Preencha todos os campos.")
            return

        supabase.table("payments").update({"amount": amount, "due_date": due_date, "client_id": client_id}).eq("id", payment_id).execute()
        self.load_payments()

        self.entry_amount.delete(0, tk.END)
        self.entry_due_date.set_date('')
        self.entry_client.delete(0, tk.END)

        self.button_add.config(text="Adicionar Pagamento", command=self.add_payment)

    def delete_payments(self):
        """Excluir pagamentos selecionados"""
        selected_items = self.payment_table.selection()
        if not selected_items:
            messagebox.showerror("Erro", "Selecione ao menos um pagamento para excluir.")
            return

        confirm = messagebox.askyesno("Excluir", "Tem certeza que deseja excluir os pagamentos selecionados?")
        if not confirm:
            return

        for selected_item in selected_items:
            payment_id = self.payment_table.item(selected_item, 'values')[0]
            supabase.table("payments").delete().eq("id", payment_id).execute()

        self.load_payments()

    def on_select(self, event):
        """Ação ao selecionar um pagamento"""
        selected_items = self.payment_table.selection()
        if selected_items:
            self.button_edit.config(state="normal")
            self.button_delete.config(state="normal")
        else:
            self.button_edit.config(state="disabled")
            self.button_delete.config(state="disabled")

# Criando a janela principal
root = tk.Tk()
app = PaymentApp(root)
root.mainloop()
