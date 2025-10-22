# ui/add_transaction_window.py
import customtkinter as ctk
from datetime import datetime
from models.transaction import Transaction
from utils.validators import validate_datetime_br, convert_datetime_br_to_db, validate_amount


class AddTransactionWindow(ctk.CTkToplevel):
    def __init__(self, parent, db_service, on_save_callback=None):
        super().__init__(parent)
        self.parent = parent
        self.db_service = db_service
        self.on_save_callback = on_save_callback

        self.title("Adicionar Transação")
        self.geometry("400x550")  # Aumentei a altura para caber o campo de hora
        self.resizable(False, False)
        self.grab_set()

        self.create_widgets()
        self.load_categories()

    def create_widgets(self):
        # Tipo de transação
        ctk.CTkLabel(self, text="Tipo:", font=('Arial', 14, 'bold')).pack(pady=(20, 5))
        self.type_var = ctk.StringVar(value="Receita")

        self.type_combobox = ctk.CTkComboBox(self,
                                             values=["Receita", "Despesa"],
                                             variable=self.type_var,
                                             command=self.on_type_change,
                                             state="readonly",
                                             dropdown_font=('Arial', 12))
        self.type_combobox.pack(pady=5, padx=20, fill='x')

        # Categoria
        ctk.CTkLabel(self, text="Categoria:", font=('Arial', 14, 'bold')).pack(pady=(15, 5))
        self.category_var = ctk.StringVar()

        self.category_combobox = ctk.CTkComboBox(self,
                                                 variable=self.category_var,
                                                 state="readonly",
                                                 dropdown_font=('Arial', 12))
        self.category_combobox.pack(pady=5, padx=20, fill='x')

        # Valor (mantém editável)
        ctk.CTkLabel(self, text="Valor (R$):", font=('Arial', 14, 'bold')).pack(pady=(15, 5))
        self.value_entry = ctk.CTkEntry(self, placeholder_text="0,00")
        self.value_entry.pack(pady=5, padx=20, fill='x')

        # Data e Hora - NOVO CAMPO
        ctk.CTkLabel(self, text="Data e Hora (dd/mm/aaaa hh:mm):", font=('Arial', 14, 'bold')).pack(pady=(15, 5))
        self.datetime_entry = ctk.CTkEntry(self, placeholder_text="dd/mm/aaaa hh:mm")
        # Data e hora atual como padrão
        now_br = datetime.now().strftime('%d/%m/%Y %H:%M')
        self.datetime_entry.insert(0, now_br)
        self.datetime_entry.pack(pady=5, padx=20, fill='x')

        # Descrição (mantém editável)
        ctk.CTkLabel(self, text="Descrição:", font=('Arial', 14, 'bold')).pack(pady=(15, 5))
        self.description_entry = ctk.CTkEntry(self, placeholder_text="Descrição opcional...")
        self.description_entry.pack(pady=5, padx=20, fill='x')

        # Botões
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(pady=20, padx=20, fill='x')

        self.save_button = ctk.CTkButton(button_frame, text="Salvar",
                                         command=self.save_transaction)
        self.save_button.pack(side='left', padx=(0, 10), fill='x', expand=True)

        self.cancel_button = ctk.CTkButton(button_frame, text="Cancelar",
                                           fg_color="gray", command=self.destroy)
        self.cancel_button.pack(side='right', fill='x', expand=True)

        # Forçar abertura do dropdown ao clicar em qualquer lugar do combobox
        self.setup_dropdown_behavior()

    def setup_dropdown_behavior(self):
        """Configura o comportamento de abrir dropdown ao clicar em qualquer lugar"""

        def open_dropdown(combobox):
            def handler(event):
                combobox.focus()
                # Pequeno delay para garantir que abre o dropdown
                self.after(50, lambda: combobox._open_dropdown_menu())

            return handler

        # Aplicar aos dois comboboxes
        self.type_combobox.bind("<Button-1>", open_dropdown(self.type_combobox))
        self.category_combobox.bind("<Button-1>", open_dropdown(self.category_combobox))

    def load_categories(self):
        """Carrega categorias baseadas no tipo selecionado"""
        transaction_type = self.type_var.get()
        categories = self.db_service.get_categories_by_type(transaction_type)
        self.category_combobox.configure(values=categories)
        if categories:
            self.category_combobox.set(categories[0])
        else:
            self.category_combobox.set("")

    def on_type_change(self, *args):
        """Atualiza categorias quando o tipo muda"""
        self.load_categories()

    def save_transaction(self):
        """Salva a transação no banco de dados - COM DATA E HORA"""
        try:
            # Dados do formulário
            transaction_type = self.type_var.get()
            category = self.category_var.get()
            value_str = self.value_entry.get().strip()
            datetime_br = self.datetime_entry.get().strip()  # Data e hora em formato BR
            description = self.description_entry.get().strip()

            # VALIDAÇÃO DO VALOR
            if not value_str:
                self.show_error("Por favor, insira um valor.")
                return

            is_valid_amount, amount_value = validate_amount(value_str)
            if not is_valid_amount:
                self.show_error("Por favor, insira um valor numérico válido.\nEx: 100,50 ou 100.50")
                return

            # VALIDAÇÃO DA DATA E HORA - FORMATO BR
            if not validate_datetime_br(datetime_br):
                self.show_error("Data e hora inválidas! Use o formato dd/mm/aaaa hh:mm.\nEx: 25/12/2024 14:30")
                return

            # CONVERTER DATA E HORA BR para formato banco
            datetime_db = convert_datetime_br_to_db(datetime_br)
            if not datetime_db:
                self.show_error("Erro ao converter data e hora.")
                return

            if not category:
                self.show_error("Por favor, selecione uma categoria.")
                return

            # Criar e salvar transação
            transaction = Transaction(
                type=transaction_type,
                category=category,
                value=amount_value,
                date=datetime_db,  # Salva no banco com data E hora
                description=description
            )

            success = self.db_service.add_transaction(transaction)

            if success:
                if self.on_save_callback:
                    self.on_save_callback()
                self.destroy()
            else:
                self.show_error("Erro ao salvar transação.")

        except Exception as e:
            self.show_error(f"Erro: {str(e)}")

    def show_error(self, message):
        """Exibe mensagem de erro"""
        error_window = ctk.CTkToplevel(self)
        error_window.title("Erro")
        error_window.geometry("300x150")
        error_window.grab_set()

        ctk.CTkLabel(error_window, text="❌", font=('Arial', 24)).pack(pady=10)
        ctk.CTkLabel(error_window, text=message, wraplength=250).pack(pady=5)
        ctk.CTkButton(error_window, text="OK", command=error_window.destroy).pack(pady=10)


class EditTransactionWindow(ctk.CTkToplevel):
    def __init__(self, parent, db_service, transaction_data, on_save_callback=None):
        super().__init__(parent)
        self.parent = parent
        self.db_service = db_service
        self.transaction_data = transaction_data
        self.on_save_callback = on_save_callback
        self.transaction_id = transaction_data['id']

        self.title("Editar Transação")
        self.geometry("400x550")  # Aumentei a altura
        self.resizable(False, False)
        self.grab_set()

        self.create_widgets()
        self.load_form_data()

    def create_widgets(self):
        # Tipo de transação
        ctk.CTkLabel(self, text="Tipo:", font=('Arial', 14, 'bold')).pack(pady=(20, 5))
        self.type_var = ctk.StringVar()

        self.type_combobox = ctk.CTkComboBox(self,
                                             values=["Receita", "Despesa"],
                                             variable=self.type_var,
                                             command=self.on_type_change,
                                             state="readonly",
                                             dropdown_font=('Arial', 12))
        self.type_combobox.pack(pady=5, padx=20, fill='x')

        # Categoria
        ctk.CTkLabel(self, text="Categoria:", font=('Arial', 14, 'bold')).pack(pady=(15, 5))
        self.category_var = ctk.StringVar()

        self.category_combobox = ctk.CTkComboBox(self,
                                                 variable=self.category_var,
                                                 state="readonly",
                                                 dropdown_font=('Arial', 12))
        self.category_combobox.pack(pady=5, padx=20, fill='x')

        # Valor
        ctk.CTkLabel(self, text="Valor (R$):", font=('Arial', 14, 'bold')).pack(pady=(15, 5))
        self.value_entry = ctk.CTkEntry(self, placeholder_text="0,00")
        self.value_entry.pack(pady=5, padx=20, fill='x')

        # Data e Hora - NOVO CAMPO
        ctk.CTkLabel(self, text="Data e Hora (dd/mm/aaaa hh:mm):", font=('Arial', 14, 'bold')).pack(pady=(15, 5))
        self.datetime_entry = ctk.CTkEntry(self, placeholder_text="dd/mm/aaaa hh:mm")
        self.datetime_entry.pack(pady=5, padx=20, fill='x')

        # Descrição
        ctk.CTkLabel(self, text="Descrição:", font=('Arial', 14, 'bold')).pack(pady=(15, 5))
        self.description_entry = ctk.CTkEntry(self, placeholder_text="Descrição opcional...")
        self.description_entry.pack(pady=5, padx=20, fill='x')

        # Botões
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(pady=20, padx=20, fill='x')

        self.save_button = ctk.CTkButton(button_frame, text="Atualizar",
                                         fg_color="#2b5b84",
                                         command=self.update_transaction)
        self.save_button.pack(side='left', padx=(0, 10), fill='x', expand=True)

        self.cancel_button = ctk.CTkButton(button_frame, text="Cancelar",
                                           fg_color="gray", command=self.destroy)
        self.cancel_button.pack(side='right', fill='x', expand=True)

        # Forçar abertura do dropdown ao clicar em qualquer lugar do combobox
        self.setup_dropdown_behavior()

    def setup_dropdown_behavior(self):
        """Configura o comportamento de abrir dropdown ao clicar em qualquer lugar"""

        def open_dropdown(combobox):
            def handler(event):
                combobox.focus()
                self.after(50, lambda: combobox._open_dropdown_menu())

            return handler

        self.type_combobox.bind("<Button-1>", open_dropdown(self.type_combobox))
        self.category_combobox.bind("<Button-1>", open_dropdown(self.category_combobox))

    def load_form_data(self):
        """Carrega os dados da transação nos campos do formulário"""
        try:
            # Converter data e hora do banco para formato BR
            from utils.validators import convert_datetime_db_to_br
            datetime_br = convert_datetime_db_to_br(self.transaction_data['date'])

            # Preencher campos
            self.type_var.set(self.transaction_data['type'])
            self.category_var.set(self.transaction_data['category'])
            self.value_entry.insert(0, str(self.transaction_data['value']).replace('.', ','))
            self.datetime_entry.insert(0, datetime_br)
            self.description_entry.insert(0, self.transaction_data['description'] or '')

            # Carregar categorias baseadas no tipo
            self.load_categories()

        except Exception as e:
            self.show_error(f"Erro ao carregar dados: {e}")

    def load_categories(self):
        """Carrega categorias baseadas no tipo selecionado"""
        transaction_type = self.type_var.get()
        categories = self.db_service.get_categories_by_type(transaction_type)
        self.category_combobox.configure(values=categories)

        # Manter a categoria atual selecionada
        current_category = self.transaction_data['category']
        if current_category in categories:
            self.category_combobox.set(current_category)
        elif categories:
            self.category_combobox.set(categories[0])

    def on_type_change(self, *args):
        """Atualiza categorias quando o tipo muda"""
        self.load_categories()

    def update_transaction(self):
        """Atualiza a transação no banco de dados"""
        try:
            # Dados do formulário
            transaction_type = self.type_var.get()
            category = self.category_var.get()
            value_str = self.value_entry.get().strip()
            datetime_br = self.datetime_entry.get().strip()
            description = self.description_entry.get().strip()

            # VALIDAÇÕES
            if not value_str:
                self.show_error("Por favor, insira um valor.")
                return

            is_valid_amount, amount_value = validate_amount(value_str)
            if not is_valid_amount:
                self.show_error("Por favor, insira um valor numérico válido.\nEx: 100,50 ou 100.50")
                return

            if not validate_datetime_br(datetime_br):
                self.show_error("Data e hora inválidas! Use o formato dd/mm/aaaa hh:mm.\nEx: 25/12/2024 14:30")
                return

            datetime_db = convert_datetime_br_to_db(datetime_br)
            if not datetime_db:
                self.show_error("Erro ao converter data e hora.")
                return

            if not category:
                self.show_error("Por favor, selecione uma categoria.")
                return

            # Atualizar transação
            success = self.db_service.update_transaction(
                self.transaction_id,
                transaction_type,
                category,
                amount_value,
                datetime_db,
                description
            )

            if success:
                if self.on_save_callback:
                    self.on_save_callback()
                self.destroy()
                from tkinter import messagebox
                messagebox.showinfo("Sucesso", "Transação atualizada com sucesso!")
            else:
                self.show_error("Erro ao atualizar transação.")

        except Exception as e:
            self.show_error(f"Erro: {str(e)}")

    def show_error(self, message):
        """Exibe mensagem de erro"""
        error_window = ctk.CTkToplevel(self)
        error_window.title("Erro")
        error_window.geometry("300x150")
        error_window.grab_set()

        ctk.CTkLabel(error_window, text="❌", font=('Arial', 24)).pack(pady=10)
        ctk.CTkLabel(error_window, text=message, wraplength=250).pack(pady=5)
        ctk.CTkButton(error_window, text="OK", command=error_window.destroy).pack(pady=10)


if __name__ == "__main__":
    # Teste simples da janela
    app = ctk.CTk()
    window = AddTransactionWindow(app, None)
    app.mainloop()