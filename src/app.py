import os
import json
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from dotenv import load_dotenv
from supabase import create_client, Client
from tkcalendar import DateEntry
from datetime import datetime

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
        self.root.resizable(False, False)  # Impede o redimensionamento da janela

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

        # Frame superior com botões
        self.top_frame = tk.Frame(self.root)
        self.top_frame.pack(pady=10)

        # Botões de CRUD
        self.button_client_crud = tk.Button(self.top_frame, text="Gerenciar Clientes", command=self.open_client_crud)
        self.button_client_crud.grid(row=0, column=0, padx=10, pady=10)

        self.button_payment_crud = tk.Button(self.top_frame, text="Gerenciar Pagamentos", command=self.open_payment_crud)
        self.button_payment_crud.grid(row=0, column=1, padx=10, pady=10)

        # Botão para atualizar lista
        self.button_refresh = tk.Button(self.top_frame, text="Atualizar Lista", command=self.refresh_data)
        self.button_refresh.grid(row=0, column=2, padx=10, pady=10)

        # Combobox para selecionar cliente
        self.client_names = self.load_client_names()
        self.combobox_client_filter = ttk.Combobox(self.top_frame, values=self.client_names, width=28)
        self.combobox_client_filter.grid(row=0, column=3, padx=10, pady=10)

        # Botão para filtrar por cliente
        self.button_filter = tk.Button(self.top_frame, text="Filtrar por Cliente", command=self.filter_by_client)
        self.button_filter.grid(row=0, column=4, padx=10, pady=10)

        # Botão para esconder/mostrar pagamentos quitados
        self.show_paid_var = tk.BooleanVar(value=True)
        self.button_toggle_paid = tk.Button(self.top_frame, text="Esconder Pagamentos Quitados", command=self.toggle_paid)
        self.button_toggle_paid.grid(row=0, column=5, padx=10, pady=10)

        # Carregar dados na tabela de pagamentos
        self.load_data()

    def sort_table(self, table, column):
        """Ordenar a tabela com base na coluna clicada"""
        rows = list(table.get_children())
        if column == "Valor":
            rows.sort(key=lambda row: float(table.item(row)["values"][table["columns"].index(column)].replace(',', '')))
        else:
            rows.sort(key=lambda row: table.item(row)["values"][table["columns"].index(column)])
        
        for index, row in enumerate(rows):
            table.move(row, '', index)
            
    def load_data(self):
        """Carregar pagamentos na tabela"""
        for row in self.table.get_children():
            self.table.delete(row)

        # Obter os dados dos pagamentos
        payments = supabase.table("payments").select("*").execute()

        for payment in payments.data:
            # Obter os dados do cliente
            client = supabase.table("clients").select("name, phone").eq("id", payment['client_id']).execute().data[0]
            
            # Ajustar o status de pagamento
            is_paid = "Quitado" if payment['is_paid'] else "Pendente"
            
            # Verificar e formatar a data de vencimento, se necessário
            try:
                due_date = datetime.strptime(payment['due_date'], "%Y-%m-%d").strftime("%d/%m/%Y")  # Ajuste da data
            except ValueError:
                # Caso a data não esteja no formato esperado, atribuir um valor padrão
                due_date = "Data inválida"

            # Formatar o valor com duas casas decimais e trocar . por ,
            amount = f"{float(payment['amount']):.2f}".replace('.', ',')

            # Inserir os dados na tabela, se a exibição de quitados estiver habilitada ou se o pagamento não estiver quitado
            if self.show_paid_var.get() or not payment['is_paid']:
                self.table.insert("", "end", values=(payment['id'], client['name'], client['phone'], amount, due_date, is_paid))

    def refresh_data(self):
        """Atualizar dados da tabela e combobox de clientes"""
        self.load_data()
        self.update_client_combobox()

    def update_client_combobox(self):
        """Atualizar os nomes dos clientes na combobox"""
        self.client_names = self.load_client_names()
        self.combobox_client_filter['values'] = self.client_names

    def open_client_crud(self):
        """Abrir a tela de CRUD de clientes"""
        client_crud = ClientCRUD(self.root, self)
        self.root.wait_window(client_crud.top)
        self.refresh_data()

    def open_payment_crud(self):
        """Abrir a tela de CRUD de pagamentos"""
        payment_crud = PaymentCRUD(self.root, self)
        self.root.wait_window(payment_crud.top)
        self.refresh_data()

    def load_client_names(self):
        """Carregar os nomes dos clientes do banco de dados"""
        clients = supabase.table("clients").select("name").execute().data
        return [client['name'] for client in clients]

    def filter_by_client(self):
        """Filtrar pagamentos por cliente"""
        client_name = self.combobox_client_filter.get()
        if not client_name:
            messagebox.showerror("Erro", "Selecione um cliente para filtrar.")
            return

        client_id = supabase.table("clients").select("id").eq("name", client_name).execute().data[0]['id']
        payments = supabase.table("payments").select("*").eq("client_id", client_id).execute()

        for row in self.table.get_children():
            self.table.delete(row)

        for payment in payments.data:
            client = supabase.table("clients").select("name, phone").eq("id", payment['client_id']).execute().data[0]
            is_paid = "Quitado" if payment['is_paid'] else "Pendente"
            try:
                due_date = datetime.strptime(payment['due_date'], "%Y-%m-%d").strftime("%d/%m/%Y")
            except ValueError:
                due_date = "Data inválida"
            self.table.insert("", "end", values=(payment['id'], client['name'], client['phone'], payment['amount'], due_date, is_paid))

    def toggle_paid(self):
        """Alternar a exibição de pagamentos quitados"""
        self.show_paid_var.set(not self.show_paid_var.get())
        if self.show_paid_var.get():
            self.button_toggle_paid.config(text="Esconder Pagamentos Quitados")
        else:
            self.button_toggle_paid.config(text="Mostrar Pagamentos Quitados")
        self.refresh_data()

class ClientCRUD:
    def __init__(self, root, app):
        self.app = app
        self.top = tk.Toplevel(root)
        self.top.title("Gerenciar Clientes")
        self.top.geometry("600x400")
        self.top.resizable(False, False)

        self.frame_inputs = tk.Frame(self.top)
        self.frame_inputs.pack(pady=20)

        # Campos de entrada para cliente
        self.label_name = tk.Label(self.frame_inputs, text="Nome do Cliente")
        self.label_name.grid(row=0, column=0, padx=10, pady=10)
        self.entry_name = tk.Entry(self.frame_inputs, width=30)
        self.entry_name.grid(row=0, column=1, padx=10, pady=10)

        # Botão para filtrar por cliente ao lado do campo de entrada
        self.button_filter = tk.Button(self.frame_inputs, text="Buscar", command=self.filter_by_client)
        self.button_filter.grid(row=0, column=2, padx=10, pady=10)

        self.label_phone = tk.Label(self.frame_inputs, text="Telefone")
        self.label_phone.grid(row=1, column=0, padx=10, pady=10)
        self.entry_phone = tk.Entry(self.frame_inputs, width=30)
        self.entry_phone.grid(row=1, column=1, padx=10, pady=10)

        # Botões de CRUD
        self.frame_buttons = tk.Frame(self.top)
        self.frame_buttons.pack(pady=5)

        self.button_add = tk.Button(self.frame_buttons, text="Adicionar Cliente", command=self.add_client)
        self.button_add.grid(row=0, column=0, padx=5)

        self.button_edit_name = tk.Button(self.frame_buttons, text="Editar Nome", command=self.edit_client_name)
        self.button_edit_name.grid(row=0, column=1, padx=5)

        self.button_edit_phone = tk.Button(self.frame_buttons, text="Editar Telefone", command=self.edit_client_phone)
        self.button_edit_phone.grid(row=0, column=2, padx=5)

        self.button_delete = tk.Button(self.frame_buttons, text="Excluir Clientes", command=self.delete_clients)
        self.button_delete.grid(row=0, column=3, padx=5)

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

    def edit_client_name(self):
        """Editar nome do cliente selecionado"""
        selected_items = self.client_table.selection()
        if len(selected_items) != 1:
            messagebox.showerror("Erro", "Selecione apenas um cliente para editar.")
            return
        
        selected_item = selected_items[0]
        client_id = self.client_table.item(selected_item, 'values')[0]
        new_name = self.entry_name.get()

        if not new_name:
            messagebox.showerror("Erro", "Preencha o novo nome do cliente.")
            return

        supabase.table("clients").update({"name": new_name}).eq("id", client_id).execute()
        self.load_clients()

    def edit_client_phone(self):
        """Editar telefone do cliente selecionado"""
        selected_items = self.client_table.selection()
        if len(selected_items) != 1:
            messagebox.showerror("Erro", "Selecione apenas um cliente para editar.")
            return
        
        selected_item = selected_items[0]
        client_id = self.client_table.item(selected_item, 'values')[0]
        new_phone = self.entry_phone.get()

        if not new_phone:
            messagebox.showerror("Erro", "Preencha o novo telefone do cliente.")
            return

        supabase.table("clients").update({"phone": new_phone}).eq("id", client_id).execute()
        self.load_clients()

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
            self.button_edit_name.config(state="normal")
            self.button_edit_phone.config(state="normal")
            self.button_delete.config(state="normal")
        else:
            self.button_edit_name.config(state="disabled")
            self.button_edit_phone.config(state="disabled")
            self.button_delete.config(state="disabled")

    def filter_by_client(self):
        """Filtrar clientes por nome similar"""
        client_name = self.entry_name.get()
        if not client_name:
            messagebox.showerror("Erro", "Digite um nome para filtrar.")
            return

        clients = supabase.table("clients").select("*").ilike("name", f"%{client_name}%").execute()

        for row in self.client_table.get_children():
            self.client_table.delete(row)

        for client in clients.data:
            self.client_table.insert("", "end", values=(client['id'], client['name'], client['phone']))

class PaymentCRUD:
    def __init__(self, root, app):
        self.app = app
        self.top = tk.Toplevel(root)
        self.top.title("Gerenciar Pagamentos")
        self.top.geometry("800x400")
        self.top.resizable(False, False)

        self.frame_inputs = tk.Frame(self.top)
        self.frame_inputs.pack(pady=20)

        # Campos de entrada para pagamento
        self.label_amount = tk.Label(self.frame_inputs, text="Valor")
        self.label_amount.grid(row=0, column=0, padx=10, pady=10)
        self.entry_amount = tk.Entry(self.frame_inputs, width=30, validate="key", validatecommand=(self.top.register(self.validate_amount), '%P'))
        self.entry_amount.grid(row=0, column=1, padx=10, pady=10)

        self.label_due_date = tk.Label(self.frame_inputs, text="Data de Vencimento")
        self.label_due_date.grid(row=1, column=0, padx=10, pady=10)
        self.entry_due_date = DateEntry(self.frame_inputs, width=30, background='darkblue', foreground='white', borderwidth=2, locale='pt_BR')
        self.entry_due_date.grid(row=1, column=1, padx=10, pady=10)

        self.label_client = tk.Label(self.frame_inputs, text="Cliente")
        self.label_client.grid(row=2, column=0, padx=10, pady=10)
        self.client_names = self.load_client_names()
        self.combobox_client = ttk.Combobox(self.frame_inputs, values=self.client_names, width=28)
        self.combobox_client.grid(row=2, column=1, padx=10, pady=10)
        self.combobox_client.bind("<KeyRelease>", self.filter_items)

        # Botão para filtrar por cliente usando a combobox existente
        self.button_filter = tk.Button(self.frame_inputs, text="Filtrar por Cliente", command=self.filter_by_client)
        self.button_filter.grid(row=2, column=2, padx=10, pady=10)

        # Botões de CRUD
        self.frame_buttons = tk.Frame(self.top)
        self.frame_buttons.pack(pady=5)

        self.button_add = tk.Button(self.frame_buttons, text="Adicionar Pagamento", command=self.add_payment)
        self.button_add.grid(row=0, column=0, padx=5)

        self.button_edit = tk.Button(self.frame_buttons, text="Alterar Valor", command=self.edit_payment)
        self.button_edit.grid(row=0, column=1, padx=5)

        self.button_edit_client = tk.Button(self.frame_buttons, text="Alterar Cliente", command=self.edit_client)
        self.button_edit_client.grid(row=0, column=2, padx=5)

        self.button_edit_due_date = tk.Button(self.frame_buttons, text="Alterar Data", command=self.edit_due_date)
        self.button_edit_due_date.grid(row=0, column=3, padx=5)

        self.button_delete = tk.Button(self.frame_buttons, text="Excluir Pagamentos", command=lambda: [self.delete_payments(), root.lift()])
        self.button_delete.grid(row=0, column=4, padx=5)

        self.button_change_status = tk.Button(self.frame_buttons, text="Alterar Status", command=self.change_status)
        self.button_change_status.grid(row=0, column=5, padx=5)

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
        self.payment_table.column("ID", width=60, anchor="center")
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

        # Botão para esconder/mostrar pagamentos quitados
        self.show_paid_var = tk.BooleanVar(value=True)
        self.button_toggle_paid = tk.Button(self.top, text="Esconder Pagamentos Quitados", command=self.toggle_paid)
        self.button_toggle_paid.pack(pady=5)

        self.load_payments()

    def validate_amount(self, new_value):
        """Validar o valor do campo de entrada para aceitar apenas números e até duas casas decimais"""
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
        """Carregar os nomes dos clientes do banco de dados"""
        clients = supabase.table("clients").select("name").execute().data
        return [client['name'] for client in clients]

    def sort_table(self, table, column):
        """Ordenar a tabela com base na coluna clicada"""
        rows = list(table.get_children())
        if column == "Valor":
            rows.sort(key=lambda row: float(table.item(row)["values"][table["columns"].index(column)].replace(',', '')))
        else:
            rows.sort(key=lambda row: table.item(row)["values"][table["columns"].index(column)])
        
        for index, row in enumerate(rows):
            table.move(row, '', index)
            
    def filter_items(self, event):
        """Filtrar os nomes dos clientes na combobox"""
        query = self.combobox_client.get().lower()
        filtered_names = [name for name in self.client_names if query in name.lower()]
        self.combobox_client['values'] = filtered_names

    def load_payments(self):
        """Carregar pagamentos na tabela"""
        for row in self.payment_table.get_children():
            self.payment_table.delete(row)

        payments = supabase.table("payments").select("*").execute()

        for payment in payments.data:
            client = supabase.table("clients").select("name").eq("id", payment['client_id']).execute().data[0]
            status = "Pago" if payment['is_paid'] else "Pendente"
            
            # Verificar e formatar a data de vencimento, se necessário
            try:
                due_date = datetime.strptime(payment['due_date'], "%Y-%m-%d").strftime("%d/%m/%Y")  # Ajuste da data
            except ValueError:
                due_date = "Data inválida"

            # Formatar o valor com duas casas decimais e trocar . por ,
            amount = f"{float(payment['amount']):.2f}".replace('.', ',')

            # Inserir os dados na tabela, se a exibição de quitados estiver habilitada ou se o pagamento não estiver quitado
            if self.show_paid_var.get() or not payment['is_paid']:
                self.payment_table.insert("", "end", values=(payment['id'], client['name'], amount, due_date, status))

    def add_payment(self):
        """Adicionar pagamento"""
        amount = self.entry_amount.get().replace(',', '.')
        due_date = self.entry_due_date.get_date()
        client_name = self.combobox_client.get()

        if not amount or not due_date or not client_name:
            messagebox.showerror("Erro", "Preencha todos os campos.")
            return

        client_id = supabase.table("clients").select("id").eq("name", client_name).execute().data[0]['id']
        
        # Converter due_date para string no formato correto (ano-mês-dia)
        due_date_str = due_date.strftime("%Y-%m-%d")

        data = {"amount": float(amount), "due_date": due_date_str, "client_id": client_id, "is_paid": False}
        supabase.table("payments").insert(data).execute()

        self.entry_amount.delete(0, tk.END)
        self.entry_due_date.set_date(None)
        self.combobox_client.set('')

        self.load_payments()

    def edit_payment(self):
        """Editar valor do pagamento selecionado"""
        selected_items = self.payment_table.selection()
        if not selected_items:
            messagebox.showerror("Erro", "Selecione um pagamento para editar.")
            return

        payment_id = self.payment_table.item(selected_items[0], 'values')[0]
        amount = self.entry_amount.get().replace(',', '.')

        if not amount:
            messagebox.showerror("Erro", "Preencha o valor do pagamento.")
            return

        data = {"amount": float(amount)}
        supabase.table("payments").update(data).eq("id", payment_id).execute()

        self.load_payments()

    def edit_client(self):
        """Editar cliente do pagamento selecionado"""
        selected_items = self.payment_table.selection()
        if not selected_items:
            messagebox.showerror("Erro", "Selecione um pagamento para editar.")
            return

        payment_id = self.payment_table.item(selected_items[0], 'values')[0]
        client_name = self.combobox_client.get()

        if not client_name:
            messagebox.showerror("Erro", "Preencha o nome do cliente.")
            return

        client_id = supabase.table("clients").select("id").eq("name", client_name).execute().data[0]['id']
        data = {"client_id": client_id}
        supabase.table("payments").update(data).eq("id", payment_id).execute()

        self.load_payments()

    def edit_due_date(self):
        """Editar data de vencimento do pagamento selecionado"""
        selected_items = self.payment_table.selection()
        if not selected_items:
            messagebox.showerror("Erro", "Selecione um pagamento para editar.")
            return

        payment_id = self.payment_table.item(selected_items[0], 'values')[0]
        due_date = self.entry_due_date.get_date()

        if not due_date:
            messagebox.showerror("Erro", "Preencha a data de vencimento.")
            return

        due_date_str = due_date.strftime("%Y-%m-%d")
        data = {"due_date": due_date_str}
        supabase.table("payments").update(data).eq("id", payment_id).execute()

        self.load_payments()

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

    def change_status(self):
        """Alterar o status do pagamento selecionado"""
        selected_items = self.payment_table.selection()
        if not selected_items:
            messagebox.showerror("Erro", "Selecione um pagamento para alterar o status.")
            return

        payment_id = self.payment_table.item(selected_items[0], 'values')[0]
        current_status = self.payment_table.item(selected_items[0], 'values')[4]

        new_status = "Pendente" if current_status == "Pago" else "Pago"
        is_paid = new_status == "Pago"

        supabase.table("payments").update({"is_paid": is_paid}).eq("id", payment_id).execute()
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

    def filter_by_client(self):
        """Filtrar pagamentos por cliente"""
        client_name = self.combobox_client.get()
        if not client_name:
            messagebox.showerror("Erro", "Selecione um cliente para filtrar.")
            return

        client_id = supabase.table("clients").select("id").eq("name", client_name).execute().data[0]['id']
        payments = supabase.table("payments").select("*").eq("client_id", client_id).execute()

        for row in self.payment_table.get_children():
            self.payment_table.delete(row)

        for payment in payments.data:
            client = supabase.table("clients").select("name").eq("id", payment['client_id']).execute().data[0]
            status = "Pago" if payment['is_paid'] else "Pendente"
            try:
                due_date = datetime.strptime(payment['due_date'], "%Y-%m-%d").strftime("%d/%m/%Y")
            except ValueError:
                due_date = "Data inválida"
            self.payment_table.insert("", "end", values=(payment['id'], client['name'], payment['amount'], due_date, status))

    def toggle_paid(self):
        """Alternar a exibição de pagamentos quitados"""
        self.show_paid_var.set(not self.show_paid_var.get())
        if self.show_paid_var.get():
            self.button_toggle_paid.config(text="Esconder Pagamentos Quitados")
        else:
            self.button_toggle_paid.config(text="Mostrar Pagamentos Quitados")
        self.load_payments()

# Criando a janela principal
root = tk.Tk()
app = PaymentApp(root)
root.mainloop()
