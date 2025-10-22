# ui/main_window.py
import customtkinter as ctk
from ui.add_transaction_window import AddTransactionWindow, EditTransactionWindow
from services.database_service import DatabaseService
import tkinter.messagebox as messagebox
from datetime import datetime


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.db_service = DatabaseService()

        # Variáveis para ordenação
        self.current_sort_column = 'id'
        self.sort_ascending = True

        # Configuração da janela
        self.title("■ FinanceTracker")
        self.geometry("1200x650")
        self.resizable(True, True)

        # Configurar tema
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.create_widgets()
        self.update_display()

    def create_widgets(self):
        """Cria todos os widgets da interface"""
        # Frame principal
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Título
        self.title_label = ctk.CTkLabel(main_frame, text='FinanceTracker',
                                        font=('Arial', 28, 'bold'))
        self.title_label.pack(pady=20)

        # Resumo financeiro
        self.create_summary_frame(main_frame)

        # Frame de botões
        self.create_button_frame(main_frame)

        # Lista de transações
        self.create_transactions_frame(main_frame)

        # Rodapé
        self.footer = ctk.CTkLabel(main_frame,
                                   text='Controle suas finanças pessoais com facilidade 💰',
                                   font=('Arial', 14))
        self.footer.pack(side='bottom', pady=10)

    def create_summary_frame(self, parent):
        """Cria o frame de resumo financeiro"""
        self.summary_frame = ctk.CTkFrame(parent)
        self.summary_frame.pack(fill='x', padx=20, pady=10)

        self.revenue_label = ctk.CTkLabel(self.summary_frame, text="Receitas: R$ 0,00",
                                          font=('Arial', 16), text_color="green")
        self.revenue_label.grid(row=0, column=0, padx=20, pady=10)

        self.expense_label = ctk.CTkLabel(self.summary_frame, text="Despesas: R$ 0,00",
                                          font=('Arial', 16), text_color="red")
        self.expense_label.grid(row=0, column=1, padx=20, pady=10)

        self.balance_label = ctk.CTkLabel(self.summary_frame, text="Saldo: R$ 0,00",
                                          font=('Arial', 18, 'bold'))
        self.balance_label.grid(row=0, column=2, padx=20, pady=10)

    def create_button_frame(self, parent):
        """Cria o frame com botões de ação"""
        self.button_frame = ctk.CTkFrame(parent)
        self.button_frame.pack(pady=20)

        self.add_button = ctk.CTkButton(self.button_frame, text='+ Adicionar Transação',
                                        width=200, command=self.open_add_transaction)
        self.add_button.grid(row=0, column=0, padx=10, pady=10)

        self.refresh_button = ctk.CTkButton(self.button_frame, text='🔄 Atualizar',
                                            width=200, command=self.update_display)
        self.refresh_button.grid(row=0, column=1, padx=10, pady=10)

        # NOVO BOTÃO: Gráficos
        self.charts_button = ctk.CTkButton(self.button_frame, text='📊 Gráficos',
                                           width=200, command=self.open_charts)
        self.charts_button.grid(row=0, column=2, padx=10, pady=10)

        self.export_button = ctk.CTkButton(self.button_frame, text='📁 Exportar',
                                           width=200, command=self.export_data)
        self.export_button.grid(row=0, column=3, padx=10, pady=10)

    def create_transactions_frame(self, parent):
        """Cria o frame da lista de transações"""
        transactions_frame = ctk.CTkFrame(parent)
        transactions_frame.pack(fill='both', expand=True, padx=20, pady=10)

        ctk.CTkLabel(transactions_frame, text="Últimas Transações",
                     font=('Arial', 18, 'bold')).pack(pady=10)

        # Frame para a lista
        self.tree_frame = ctk.CTkFrame(transactions_frame)
        self.tree_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Scrollable frame para as transações
        self.scrollable_frame = ctk.CTkScrollableFrame(self.tree_frame)
        self.scrollable_frame.pack(fill='both', expand=True)

    def create_transactions_header(self):
        """Cria o cabeçalho clicável da tabela"""
        header_frame = ctk.CTkFrame(self.scrollable_frame)
        header_frame.pack(fill='x', pady=5)

        # Colunas clicáveis
        columns = [
            ('ID', 'id'),
            ('Data/Hora', 'date'),
            ('Tipo', 'type'),
            ('Categoria', 'category'),
            ('Valor', 'value'),
            ('Descrição', 'description'),
            ('Ações', 'actions')
        ]

        for i, (display_name, column_name) in enumerate(columns):
            if column_name != 'actions':  # Ações não é clicável
                btn = ctk.CTkButton(
                    header_frame,
                    text=display_name,
                    font=('Arial', 12, 'bold'),
                    width=120 if column_name == 'date' else (100 if column_name != 'description' else 150),
                    height=30,
                    command=lambda col=column_name: self.sort_transactions(col)
                )
                btn.grid(row=0, column=i, padx=2, pady=2, sticky='ew')
            else:
                # Coluna Ações não é clicável
                label = ctk.CTkLabel(
                    header_frame,
                    text=display_name,
                    font=('Arial', 12, 'bold'),
                    width=80
                )
                label.grid(row=0, column=i, padx=2, pady=2)

        # Configurar pesos das colunas para melhor distribuição
        for i in range(len(columns)):
            header_frame.grid_columnconfigure(i, weight=1)

    def sort_transactions(self, column):
        """Ordena as transações pela coluna clicada"""
        print(f"🔀 Ordenando por: {column}")

        # Se clicar na mesma coluna, inverte a direção
        if column == self.current_sort_column:
            self.sort_ascending = not self.sort_ascending
        else:
            # Nova coluna, ordena ascendente por padrão
            self.current_sort_column = column
            self.sort_ascending = True

        # Atualizar a exibição
        self.update_transactions_list()

        print(f"📊 Ordem: {column} {'↑' if self.sort_ascending else '↓'}")

    def open_add_transaction(self):
        """Abre janela para adicionar transação"""
        AddTransactionWindow(self, self.db_service, on_save_callback=self.update_display)

    def open_charts(self):
        """Abre janela de gráficos"""
        try:
            from ui.charts_window import ChartsWindow
            ChartsWindow(self, self.db_service)
        except ImportError as e:
            messagebox.showerror("Erro", f"Biblioteca de gráficos não disponível: {e}")
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível abrir os gráficos: {e}")

    def edit_transaction(self, transaction_id):
        """Abre janela para editar transação existente"""
        try:
            # Buscar transação pelo ID
            transactions = self.db_service.get_all_transactions()
            transaction_to_edit = None

            for transaction in transactions:
                if transaction['id'] == transaction_id:
                    transaction_to_edit = transaction
                    break

            if transaction_to_edit:
                # Abrir janela de edição
                EditTransactionWindow(
                    self,
                    self.db_service,
                    transaction_to_edit,
                    on_save_callback=self.update_display
                )
            else:
                messagebox.showerror("Erro", "Transação não encontrada!")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao editar transação: {e}")

    def update_display(self):
        """Atualiza toda a exibição"""
        self.update_summary()
        self.update_transactions_list()

    def update_summary(self):
        """Atualiza o resumo financeiro"""
        try:
            summary = self.db_service.get_financial_summary()

            # Formatação BR
            self.revenue_label.configure(text=f"Receitas: {self.format_currency_brl(summary['total_revenue'])}")
            self.expense_label.configure(text=f"Despesas: {self.format_currency_brl(summary['total_expense'])}")
            self.balance_label.configure(text=f"Saldo: {self.format_currency_brl(summary['balance'])}")

            # Cor do saldo
            if summary['balance'] >= 0:
                self.balance_label.configure(text_color="green")
            else:
                self.balance_label.configure(text_color="red")

        except Exception as e:
            print(f"Erro ao atualizar resumo: {e}")

    def update_transactions_list(self):
        """Atualiza a lista de transações com ordenação - CORRIGIDO PARA EVITAR SOBREPOSIÇÃO"""
        try:
            # LIMPEZA COMPLETA do scrollable_frame - CORREÇÃO PRINCIPAL
            for widget in self.scrollable_frame.winfo_children():
                widget.destroy()

            # Criar cabeçalho clicável
            self.create_transactions_header()

            # Buscar transações com ordenação
            transactions = self.db_service.get_all_transactions_sorted(
                self.current_sort_column,
                self.sort_ascending
            )

            if not transactions:
                # Mensagem centralizada quando não há transações
                no_data_frame = ctk.CTkFrame(self.scrollable_frame)
                no_data_frame.pack(expand=True, fill='both', pady=50)

                ctk.CTkLabel(no_data_frame,
                             text="Nenhuma transação encontrada.",
                             font=('Arial', 14)).pack(expand=True)
                return

            # Adicionar transações - CORRIGIDO: criar uma linha por vez
            for transaction in transactions:
                self.create_transaction_row(transaction)

            # Forçar atualização da interface
            self.scrollable_frame.update_idletasks()

        except Exception as e:
            print(f"Erro ao atualizar lista de transações: {e}")
            messagebox.showerror("Erro", f"Erro ao carregar transações: {e}")

    def format_currency_brl(self, value):
        """Formata valor como moeda brasileira (R$ 1.234,56)"""
        if value is None:
            value = 0
        return f"R$ {value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

    def convert_datetime_db_to_br(self, datetime_db):
        """Converte aaaa-mm-dd hh:mm:ss (banco) para dd/mm/aaaa hh:mm (exibição)"""
        try:
            from utils.validators import convert_datetime_db_to_br
            return convert_datetime_db_to_br(datetime_db)
        except:
            return datetime_db

    def create_tooltip(self, widget, text):
        """Cria uma tooltip (dica) para um widget"""

        def on_enter(event):
            tooltip = ctk.CTkToplevel(self)
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root + 10}+{event.y_root + 10}")

            label = ctk.CTkLabel(tooltip, text=text, font=('Arial', 10))
            label.pack(ipadx=5, ipady=2)

            widget.tooltip = tooltip

        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                delattr(widget, 'tooltip')

        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)

    def create_transaction_row(self, transaction):
        """Cria uma linha para transação - COM BOTÕES EDITAR (TEXTO) E EXCLUIR (ÍCONE)"""
        try:
            row_frame = ctk.CTkFrame(self.scrollable_frame)
            row_frame.pack(fill='x', pady=1)

            # Lógica de cores e sinais
            if transaction['type'] == 'Receita':
                color = "green"
                value_text = f"+{self.format_currency_brl(transaction['value'])}"
            else:  # Despesa
                color = "red"
                value_text = f"-{self.format_currency_brl(transaction['value'])}"

            # CONVERTER DATA E HORA para formato BR na exibição
            datetime_display = self.convert_datetime_db_to_br(transaction['date'])

            # Dados - manter alinhamento com cabeçalho
            labels_data = [
                str(transaction['id']),
                datetime_display,
                transaction['type'],
                transaction['category'],
                value_text,
                transaction['description'] or '-'
            ]

            # Adicionar labels
            for i, text in enumerate(labels_data):
                label = ctk.CTkLabel(
                    row_frame,
                    text=text,
                    text_color=color if i == 4 else None,
                    width=120 if i == 1 else (100 if i != 5 else 150),
                    anchor='w'
                )
                label.grid(row=0, column=i, padx=2, pady=1, sticky='w')

            # BOTÕES DE AÇÃO - EDITAR (TEXTO) E EXCLUIR (ÍCONE)
            button_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            button_frame.grid(row=0, column=6, padx=2, pady=1)

            # Botão Editar - COM TEXTO
            edit_btn = ctk.CTkButton(
                button_frame,
                text="Editar",
                width=60,
                height=25,
                font=('Arial', 10),
                fg_color="#2b5b84",
                hover_color="#1e4161",
                command=lambda id=transaction['id']: self.edit_transaction(id)
            )
            edit_btn.pack(side='left', padx=(0, 5))

            # Botão Excluir - COM ÍCONE X
            delete_btn = ctk.CTkButton(
                button_frame,
                text="❌",
                width=30,
                height=25,
                font=('Arial', 12),
                fg_color="#8b0000",
                hover_color="#600000",
                command=lambda id=transaction['id']: self.delete_transaction(id)
            )
            delete_btn.pack(side='left')

            # REMOVIDO: Tooltips dos botões (não são necessárias)

            # Configurar pesos das colunas
            for i in range(7):  # 7 colunas
                row_frame.grid_columnconfigure(i, weight=1)

        except Exception as e:
            print(f"Erro ao criar linha da transação: {e}")

    def delete_transaction(self, transaction_id):
        """Exclui uma transação"""
        if messagebox.askyesno("Confirmar", "Deseja excluir esta transação?"):
            success = self.db_service.delete_transaction(transaction_id)
            if success:
                self.update_display()
                messagebox.showinfo("Sucesso", "Transação excluída com sucesso!")
            else:
                messagebox.showerror("Erro", "Erro ao excluir transação.")

    def export_data(self):
        """Exporta dados para diferentes formatos"""
        try:
            from ui.export_window import ExportWindow
            ExportWindow(self, self.db_service)
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível abrir a janela de exportação: {e}")


if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()