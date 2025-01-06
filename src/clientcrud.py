import re
import tkinter as tk
from tkinter import ttk, messagebox
from supabase_client import supabase
from layout_config import *

class ClientCRUD:
    """
    Class for managing client CRUD operations.
    Handles the client management window and its components.
    """
    def __init__(self, root, app):
        self.app = app
        self.top = tk.Toplevel(root)
        self.top.title("Gerenciar Clientes")
        self.top.geometry(CLIENT_CRUD_WINDOW_SIZE)
        self.top.resizable(*CLIENT_CRUD_WINDOW_RESIZABLE)
        self.top.configure(bg=WINDOW_BG_COLOR)

        self.current_page = 0

        self.sort_order = {}

        self.frame_inputs = tk.Frame(self.top, bg=WINDOW_BG_COLOR)
        self.frame_inputs.pack(pady=FRAME_PADY)

        self.label_name = tk.Label(self.frame_inputs, text="Nome do Cliente", font=FONT, bg=WINDOW_BG_COLOR)
        self.label_name.grid(row=0, column=0, padx=PADX, pady=PADY)
        self.entry_name = tk.Entry(self.frame_inputs, width=30, font=FONT)
        self.entry_name.grid(row=0, column=1, padx=PADX, pady=PADY)

        self.button_filter = tk.Button(self.frame_inputs, text="Buscar", command=self.filter_by_client, font=FONT, bg=FILTER_BUTTON_BG_COLOR, fg=BUTTON_FG_COLOR)
        self.button_filter.grid(row=0, column=2, padx=PADX, pady=PADY)

        self.label_phone = tk.Label(self.frame_inputs, text="Telefone", font=FONT, bg=WINDOW_BG_COLOR)
        self.label_phone.grid(row=1, column=0, padx=PADX, pady=PADY)
        self.entry_phone = tk.Entry(self.frame_inputs, width=30, fg='gray', validate="key", validatecommand=(self.top.register(self.validate_phone), '%P'), font=FONT)
        self.entry_phone.insert(0, "(XX)XXXXX-XXXX")
        self.entry_phone.grid(row=1, column=1, padx=PADX, pady=PADY)
        self.entry_phone.bind("<FocusIn>", self.on_focus_in)
        self.entry_phone.bind("<FocusOut>", self.on_focus_out)
        self.entry_phone.bind("<KeyRelease>", self.format_phone_number)

        self.frame_buttons = tk.Frame(self.top, bg=WINDOW_BG_COLOR)
        self.frame_buttons.pack(pady=PADY)

        self.button_add = tk.Button(self.frame_buttons, text="Adicionar Cliente", command=self.add_client, font=FONT, bg=ADD_BUTTON_BG_COLOR, fg=BUTTON_FG_COLOR)
        self.button_add.grid(row=0, column=0, padx=PADX)

        self.button_delete = tk.Button(self.frame_buttons, text="Excluir Clientes", command=self.delete_clients, font=FONT, bg=DELETE_BUTTON_BG_COLOR, fg=BUTTON_FG_COLOR)
        self.button_delete.grid(row=0, column=1, padx=PADX)

        self.button_edit_name = tk.Button(self.frame_buttons, text="Alterar Nome", command=self.edit_client_name, font=FONT, bg=EDIT_BUTTON_BG_COLOR, fg=BUTTON_FG_COLOR)
        self.button_edit_name.grid(row=0, column=2, padx=PADX)

        self.button_edit_phone = tk.Button(self.frame_buttons, text="Alterar Telefone", command=self.edit_client_phone, font=FONT, bg=EDIT_BUTTON_BG_COLOR, fg=BUTTON_FG_COLOR)
        self.button_edit_phone.grid(row=0, column=3, padx=PADX)

        self.button_refresh = tk.Button(self.top, text="Atualizar Lista", command=self.load_clients, font=FONT, bg=FILTER_BUTTON_BG_COLOR, fg=BUTTON_FG_COLOR)
        self.button_refresh.pack(pady=PADY)

        self.client_table_frame = tk.Frame(self.top, bg=WINDOW_BG_COLOR)
        self.client_table_frame.pack(fill='both', expand=True, padx=PADX, pady=PADY)

        self.client_table = ttk.Treeview(self.client_table_frame, columns=("ID", "Nome", "Telefone"), show="headings", selectmode="extended", style="mystyle.Treeview")
        self.client_table.heading("ID", text="ID", command=lambda: self.sort_table(self.client_table, "ID"))
        self.client_table.heading("Nome", text="Nome", command=lambda: self.sort_table(self.client_table, "Nome"))
        self.client_table.heading("Telefone", text="Telefone", command=lambda: self.sort_table(self.client_table, "Telefone"))
        
        self.client_table.column("ID", width=110, anchor="center")
        self.client_table.column("Nome", width=350, anchor="w")
        self.client_table.column("Telefone", width=300, anchor="center")

        self.client_table.grid(row=0, column=0, sticky='nsew')

        self.client_table_frame.grid_rowconfigure(0, weight=1)
        self.client_table_frame.grid_columnconfigure(0, weight=1)

        self.client_table_scrollbar = ttk.Scrollbar(self.client_table_frame, orient="vertical", command=self.client_table.yview)
        self.client_table_scrollbar.grid(row=0, column=1, sticky="ns")
        self.client_table.configure(yscrollcommand=self.client_table_scrollbar.set)

        self.client_table.bind('<<TreeviewSelect>>', self.on_select)

        self.load_clients()

    def validate_phone(self, new_value):
        """Validate the phone input to accept only numbers and allowed special characters"""
        return all(char.isdigit() or char in "X()-+" for char in new_value)

    def format_phone_number(self, event):
        """Format the phone number input"""
        phone_number = self.entry_phone.get()
        phone_number = re.sub(r'\D', '', phone_number)
        if len(phone_number) == 10:
            formatted = '({}{}){}{}{}{}-{}{}{}{}'.format(*phone_number)
        elif len(phone_number) == 11:
            formatted = '({}{}){}{}{}{}{}-{}{}{}{}'.format(*phone_number)
        elif len(phone_number) == 13:
            formatted = '+{}{}({}{}){}{}{}{}{}-{}{}{}{}'.format(*phone_number)
        elif len(phone_number) == 14:
            formatted = '+{}{}{}({}{}){}{}{}{}{}-{}{}{}{}'.format(*phone_number)
        else:
            formatted = phone_number
        self.entry_phone.delete(0, tk.END)
        self.entry_phone.insert(0, formatted)

    def on_focus_in(self, event):
        """Handle focus in event for the phone entry"""
        if self.entry_phone.get() == "(XX)XXXXX-XXXX":
            self.entry_phone.delete(0, tk.END)
            self.entry_phone.config(fg='black')

    def on_focus_out(self, event):
        """Handle focus out event for the phone entry"""
        phone_number = re.sub(r'\D', '', self.entry_phone.get())
        if len(phone_number) < 10 or len(phone_number) > 14:
            self.entry_phone.delete(0, tk.END)
            self.entry_phone.insert(0, "(XX)XXXXX-XXXX")
            self.entry_phone.config(fg='gray')

    def sort_table(self, table, column):
        """Sort the table based on the clicked column"""
        rows = list(table.get_children())
        if column not in self.sort_order:
            self.sort_order[column] = False  # Default to ascending order

        rows.sort(key=lambda row: table.item(row)["values"][table["columns"].index(column)], reverse=self.sort_order[column])
        
        for index, row in enumerate(rows):
            table.move(row, '', index)
        
        self.sort_order[column] = not self.sort_order[column]  # Toggle sort order for next click

    def load_clients(self):
        """Load clients into the table"""
        for row in self.client_table.get_children():
            self.client_table.delete(row)

        clients = supabase.table("clients").select("*").execute()

        self.all_clients = clients.data
        self.display_page(self.current_page)

    def display_page(self, page):
        """Display a specific page of clients in the table"""
        for client in self.all_clients:
            self.client_table.insert("", "end", values=(client['id'], client['name'], client['phone']))

    def add_client(self):
        """Add a client"""
        name = self.entry_name.get()
        phone = re.sub(r'\D', '', self.entry_phone.get())

        if not name or not phone or len(phone) < 10 or len(phone) > 14:
            self.top.lift()
            self.show_messagebox("Erro", "Telefone Inválido. Preencha todos os campos corretamente.")
            return

        existing_client = supabase.table("clients").select("*").eq("name", name).execute().data
        if existing_client:
            if not messagebox.askyesno("Cliente Existente", "O cliente já existe. Deseja continuar?"):
                self.top.lift()
                return

        data = {"name": name, "phone": phone}
        response = supabase.table("clients").insert(data).execute()
        client_id = response.data[0]['id']

        self.entry_name.delete(0, tk.END)
        self.entry_phone.delete(0, tk.END)

        self.load_clients()
        self.app.log_backlog(f"Added client: {name} with ID {client_id}")

    def edit_client_name(self):
        """Edit the selected client's name"""
        selected_items = self.client_table.selection()
        if len(selected_items) != 1:
            self.top.lift()
            self.show_messagebox("Erro", "Selecione exatamente um cliente para editar.")
            return
        
        selected_item = selected_items[0]
        client_id = self.client_table.item(selected_item, 'values')[0]
        new_name = self.entry_name.get()

        if not new_name:
            self.top.lift()
            self.show_messagebox("Erro", "Preencha o novo nome do cliente.")
            return

        existing_client = supabase.table("clients").select("*").eq("name", new_name).execute().data
        if existing_client:
            if not messagebox.askyesno("Cliente Existente", "O cliente já existe. Deseja continuar?"):
                self.top.lift()
                return

        old_name = self.client_table.item(selected_item, 'values')[1]
        supabase.table("clients").update({"name": new_name}).eq("id", client_id).execute()
        self.load_clients()
        self.app.log_backlog(f"Edited client name: ID {client_id}, from {old_name} to {new_name}")

    def edit_client_phone(self):
        """Edit the selected client's phone"""
        selected_items = self.client_table.selection()
        if len(selected_items) != 1:
            self.top.lift()
            self.show_messagebox("Erro", "Selecione exatamente um cliente para editar.")
            return
        
        selected_item = selected_items[0]
        client_id = self.client_table.item(selected_item, 'values')[0]
        new_phone = re.sub(r'\D', '', self.entry_phone.get())

        if not new_phone or len(new_phone) < 10 or len(new_phone) > 14:
            self.top.lift()
            self.show_messagebox("Erro", "Preencha o novo telefone do cliente corretamente. O telefone deve ter entre 10 e 14 dígitos.")
            return

        old_phone = self.client_table.item(selected_item, 'values')[2]
        supabase.table("clients").update({"phone": new_phone}).eq("id", client_id).execute()
        self.load_clients()
        self.app.log_backlog(f"Edited client phone: ID {client_id}, from {old_phone} to {new_phone}")

    def delete_clients(self):
        """Delete selected clients"""
        selected_items = self.client_table.selection()
        if not selected_items:
            self.top.lift()
            self.show_messagebox("Erro", "Selecione ao menos um cliente para excluir.")
            return

        confirm = messagebox.askyesno(
            "Excluir",
            "Tem certeza que deseja excluir os clientes selecionados? "
            "Esta operação irá excluir TODOS os pagamentos relacionados a este(s) cliente(s)."
        )
        if not confirm:
            self.top.lift()
            return

        for selected_item in selected_items:
            client_id = self.client_table.item(selected_item, 'values')[0]
            client_name = self.client_table.item(selected_item, 'values')[1]
            supabase.table("clients").delete().eq("id", client_id).execute()
            self.app.log_backlog(f"Deleted client: ID {client_id}, Name {client_name}")

        self.top.lift()
        self.load_clients()

    def on_select(self, event):
        """Action when selecting a client"""
        selected_items = self.client_table.selection()
        if len(selected_items) == 1:
            self.button_edit_name.config(state="normal")
            self.button_edit_phone.config(state="normal")
            self.button_delete.config(state="normal")
        else:
            self.button_edit_name.config(state="disabled")
            self.button_edit_phone.config(state="disabled")

    def filter_by_client(self):
        """Filter clients by similar name without generating a new query to the database"""
        client_name = self.entry_name.get().lower()
        if not client_name:
            self.top.lift()
            self.show_messagebox("Erro", "Digite um nome para filtrar.")
            return

        filtered_clients = [client for client in self.all_clients if client_name in client['name'].lower()]
        self.display_filtered_clients(filtered_clients)

    def display_filtered_clients(self, filtered_clients):
        """Display filtered clients in the table"""
        self.client_table.delete(*self.client_table.get_children())
        for client in filtered_clients:
            self.client_table.insert("", "end", values=(client['id'], client['name'], client['phone']))

    def show_messagebox(self, title, message, icon=messagebox.ERROR):
        """Show a messagebox and keep the CRUD window in front"""
        self.top.lift()
        messagebox.showerror(title, message, parent=self.top)