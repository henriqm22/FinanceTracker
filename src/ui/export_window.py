# ui/export_window.py
import customtkinter as ctk
import tkinter.messagebox as messagebox
from tkinter import filedialog
from datetime import datetime
import os
import csv
import json


class ExportWindow(ctk.CTkToplevel):
    def __init__(self, parent, db_service):
        super().__init__(parent)
        self.db_service = db_service
        self.parent = parent

        # Configurações da janela
        self.title("Exportar Dados")
        self.geometry("450x550")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        # Focar nesta janela
        self.focus_force()

        self.create_widgets()
        self.center_window()

    def center_window(self):
        """Centraliza a janela na tela"""
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (450 // 2)
        y = (self.winfo_screenheight() // 2) - (550 // 2)
        self.geometry(f"450x550+{x}+{y}")

    def create_widgets(self):
        """Cria os widgets da janela de exportação de forma mais compacta"""
        # Frame principal
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)

        # Título
        title_label = ctk.CTkLabel(main_frame, text="📊 Exportar Dados",
                                   font=ctk.CTkFont(size=18, weight="bold"))
        title_label.pack(pady=(0, 15))

        # === FORMATO DE EXPORTAÇÃO ===
        format_label = ctk.CTkLabel(main_frame, text="Formato de Exportação:",
                                    font=ctk.CTkFont(weight="bold"))
        format_label.pack(anchor="w", pady=(5, 5))

        self.format_var = ctk.StringVar(value="csv")

        format_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        format_frame.pack(fill="x", pady=(0, 10))

        formats = [("CSV (Excel)", "csv"), ("JSON", "json"), ("PDF", "pdf")]
        for text, value in formats:
            radio = ctk.CTkRadioButton(format_frame, text=text, variable=self.format_var, value=value)
            radio.pack(anchor="w", pady=2)

        # === DADOS PARA EXPORTAR ===
        data_label = ctk.CTkLabel(main_frame, text="Dados para Exportar:",
                                  font=ctk.CTkFont(weight="bold"))
        data_label.pack(anchor="w", pady=(5, 5))

        self.include_summary = ctk.BooleanVar(value=True)
        self.include_transactions = ctk.BooleanVar(value=True)

        data_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        data_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkCheckBox(data_frame, text="Incluir resumo financeiro",
                        variable=self.include_summary).pack(anchor="w", pady=2)
        ctk.CTkCheckBox(data_frame, text="Incluir transações",
                        variable=self.include_transactions).pack(anchor="w", pady=2)

        # === PERÍODO ===
        period_label = ctk.CTkLabel(main_frame, text="Período:",
                                    font=ctk.CTkFont(weight="bold"))
        period_label.pack(anchor="w", pady=(5, 5))

        self.period_var = ctk.StringVar(value="all")

        period_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        period_frame.pack(fill="x", pady=(0, 20))

        periods = [
            ("Todos os dados", "all"),
            ("Últimos 30 dias", "30days"),
            ("Este mês", "this_month")
        ]

        for text, value in periods:
            radio = ctk.CTkRadioButton(period_frame, text=text, variable=self.period_var, value=value)
            radio.pack(anchor="w", pady=2)

        # === BOTÕES ===
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(20, 10))

        # Botão Exportar (grande e destacado)
        export_btn = ctk.CTkButton(
            button_frame,
            text="📁 EXPORTAR AGORA",
            command=self.export_data,
            fg_color="#28a745",
            hover_color="#218838",
            height=40,
            font=ctk.CTkFont(weight="bold", size=14)
        )
        export_btn.pack(fill="x", pady=(0, 10))

        # Botão Cancelar
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancelar",
            command=self.destroy,
            fg_color="#6c757d",
            hover_color="#5a6268",
            height=35
        )
        cancel_btn.pack(fill="x")

        # Informação adicional
        info_text = ctk.CTkLabel(
            main_frame,
            text="💡 Você poderá escolher onde salvar o arquivo",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        info_text.pack(pady=(15, 0))

    def get_save_path(self, default_filename, file_types):
        """Abre diálogo para escolher onde salvar o arquivo"""
        try:
            # Se for PDF, mudamos para .txt mas mantemos a opção .pdf
            if self.format_var.get() == "pdf":
                file_types = [
                    ("Arquivos de Texto (Recomendado)", "*.txt"),
                    ("Arquivos PDF", "*.pdf"),
                    ("Todos os arquivos", "*.*")
                ]
                # Mudar extensão padrão para .txt
                default_filename = default_filename.replace('.pdf', '.txt')

            # Abrir diálogo de salvamento
            filepath = filedialog.asksaveasfilename(
                title="Salvar arquivo como...",
                defaultextension=file_types[0][1].replace("*", ""),
                initialfile=default_filename,
                filetypes=file_types
            )

            return filepath if filepath else None

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao selecionar local: {e}")
            return None

    def export_data(self):
        """Executa a exportação dos dados"""
        try:
            format_type = self.format_var.get()
            default_filename = self.generate_filename(format_type)

            # Definir tipos de arquivo para cada formato
            file_types = {
                "csv": [("Arquivos CSV", "*.csv"), ("Todos os arquivos", "*.*")],
                "json": [("Arquivos JSON", "*.json"), ("Todos os arquivos", "*.*")],
                "pdf": [("Arquivos de Texto (Recomendado)", "*.txt"),
                        ("Arquivos PDF", "*.pdf"),
                        ("Todos os arquivos", "*.*")]
            }

            # Abrir diálogo para escolher onde salvar
            filepath = self.get_save_path(default_filename, file_types[format_type])

            if not filepath:
                return  # Usuário cancelou

            print(f"📁 Exportando para: {filepath}")

            # Buscar dados do banco
            transactions = self.db_service.get_all_transactions()
            summary = self.db_service.get_financial_summary()

            if not transactions:
                messagebox.showwarning("Aviso", "Não há transações para exportar.")
                return

            # Mostrar mensagem de processamento
            self.withdraw()  # Esconde a janela temporariamente

            # Exportar baseado no formato
            success = False
            if format_type == "csv":
                success = self.export_to_csv(filepath, transactions, summary)
            elif format_type == "json":
                success = self.export_to_json(filepath, transactions, summary)
            elif format_type == "pdf":
                success = self.export_to_pdf(filepath, transactions, summary)

            if success:
                # Mensagem de sucesso já foi mostrada nos métodos específicos
                self.destroy()
            else:
                self.deiconify()  # Mostra a janela novamente
                messagebox.showerror("Erro", "Falha ao exportar os dados.")

        except Exception as e:
            self.deiconify()  # Mostra a janela novamente em caso de erro
            messagebox.showerror("Erro", f"Erro ao exportar dados: {str(e)}")
            print(f"❌ Erro detalhado: {e}")

    def generate_filename(self, format_type):
        """Gera nome do arquivo com timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        extensions = {
            "csv": "csv",
            "json": "json",
            "pdf": "pdf"
        }
        return f"financas_{timestamp}.{extensions[format_type]}"

    def export_to_csv(self, filepath, transactions, summary):
        """Exporta dados para CSV"""
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file, delimiter=';')

                # Escrever resumo
                if self.include_summary.get():
                    writer.writerow(["RESUMO FINANCEIRO"])
                    writer.writerow(["Receitas Total:", f"R$ {summary['total_revenue']:.2f}"])
                    writer.writerow(["Despesas Total:", f"R$ {summary['total_expense']:.2f}"])
                    writer.writerow(["Saldo:", f"R$ {summary['balance']:.2f}"])
                    writer.writerow([])
                    writer.writerow([])

                # Escrever transações
                if self.include_transactions.get():
                    writer.writerow(["TRANSAÇÕES"])
                    writer.writerow(["ID", "Data", "Tipo", "Categoria", "Valor", "Descrição"])

                    for transaction in transactions:
                        writer.writerow([
                            transaction['id'],
                            transaction['date'],
                            transaction['type'],
                            transaction['category'],
                            f"R$ {transaction['value']:.2f}",
                            transaction['description'] or ''
                        ])

            messagebox.showinfo(
                "✅ CSV Exportado",
                f"📊 Arquivo CSV salvo com sucesso!\n\n"
                f"Arquivo: {os.path.basename(filepath)}\n"
                f"Local: {filepath}\n\n"
                "📖 Pode ser aberto no Excel ou qualquer editor"
            )
            print(f"✅ CSV exportado: {filepath}")
            return True

        except Exception as e:
            print(f"❌ Erro ao exportar CSV: {e}")
            return False

    def export_to_json(self, filepath, transactions, summary):
        """Exporta dados para JSON"""
        try:
            export_data = {
                "export_info": {
                    "export_date": datetime.now().isoformat(),
                    "total_transactions": len(transactions),
                    "format": "FinanceTracker Export"
                }
            }

            if self.include_summary.get():
                export_data["summary"] = summary

            if self.include_transactions.get():
                export_data["transactions"] = transactions

            with open(filepath, 'w', encoding='utf-8') as file:
                json.dump(export_data, file, indent=2, ensure_ascii=False, default=str)

            messagebox.showinfo(
                "✅ JSON Exportado",
                f"📄 Arquivo JSON salvo com sucesso!\n\n"
                f"Arquivo: {os.path.basename(filepath)}\n"
                f"Local: {filepath}\n\n"
                "📖 Pode ser usado para integrações e APIs"
            )
            print(f"✅ JSON exportado: {filepath}")
            return True

        except Exception as e:
            print(f"❌ Erro ao exportar JSON: {e}")
            return False

    def export_to_pdf(self, filepath, transactions, summary):
        """Exporta dados para PDF/Texto formatado"""
        try:
            # Verificar se o usuário escolheu .pdf mesmo sabendo que é texto
            is_pdf_extension = filepath.lower().endswith('.pdf')

            # Se for .pdf, avisar o usuário
            if is_pdf_extension:
                result = messagebox.askyesno(
                    "Aviso - Formato PDF",
                    "📄 O arquivo será salvo como TEXTO FORMATADO com extensão .pdf\n\n"
                    "Isso significa que:\n"
                    "• ✅ Funciona perfeitamente em editores de texto\n"
                    "• ❌ Pode não abrir em navegadores/leitores PDF\n\n"
                    "Recomendamos usar a extensão .txt para melhor compatibilidade.\n\n"
                    "Deseja continuar com .pdf mesmo assim?"
                )

                if not result:
                    # Usuário quer mudar para .txt
                    new_filepath = filepath.replace('.pdf', '.txt')
                    return self.export_to_pdf(new_filepath, transactions, summary)

            with open(filepath, 'w', encoding='utf-8') as file:
                # Cabeçalho do relatório
                file.write("╔" + "═" * 58 + "╗\n")
                file.write("║                RELATÓRIO FINANCEIRO                ║\n")
                file.write("║                 OrçaFácil                    ║\n")
                file.write("╚" + "═" * 58 + "╝\n\n")

                # Informações da exportação
                file.write(f"📅 Data de exportação: {datetime.now().strftime('%d/%m/%Y às %H:%M')}\n")
                file.write(f"📊 Total de transações: {len(transactions)}\n\n")

                # Resumo financeiro
                if self.include_summary.get():
                    file.write("┌─ RESUMO FINANCEIRO ──────────────────────────────────┐\n")
                    file.write("│                                                    │\n")

                    # Calcular larguras para alinhamento
                    receita = f"R$ {summary['total_revenue']:,.2f}".replace(',', 'X').replace('.', ',').replace('X',
                                                                                                                '.')
                    despesa = f"R$ {summary['total_expense']:,.2f}".replace(',', 'X').replace('.', ',').replace('X',
                                                                                                                '.')
                    saldo = f"R$ {summary['balance']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

                    file.write(f"│    💰 Receitas Total: {receita:>20}    │\n")
                    file.write(f"│    💸 Despesas Total: {despesa:>20}    │\n")
                    file.write(f"│    ⚖️  Saldo Final:   {saldo:>20}    │\n")
                    file.write("│                                                    │\n")
                    file.write("└────────────────────────────────────────────────────┘\n\n")

                # Transações
                if self.include_transactions.get():
                    file.write("┌─ LISTA DE TRANSAÇÕES ───────────────────────────────┐\n")
                    file.write("│ ID  Data        Tipo     Categoria      Valor       Descrição       │\n")
                    file.write("├─────────────────────────────────────────────────────┤\n")

                    for transaction in transactions:
                        # Formatar data (apenas data, não hora)
                        data_br = transaction['date'][:10]  # Apenas data

                        # Formatar valor
                        valor = transaction['value']
                        if transaction['type'] == 'Receita':
                            valor_str = f"+R$ {valor:7.2f}"
                            simbolo = "⬆️"
                        else:
                            valor_str = f"-R$ {valor:7.2f}"
                            simbolo = "⬇️"

                        # Formatar moeda brasileira
                        valor_str = valor_str.replace('.', ',')

                        # Limitar tamanho dos campos
                        categoria = transaction['category'][:12].ljust(12)
                        descricao = (transaction['description'] or '')[:15].ljust(15)

                        # Escrever linha formatada
                        file.write(
                            f"│ {transaction['id']:2}  {data_br}  {simbolo}  {categoria}  {valor_str:>9}  {descricao} │\n")

                    file.write("└─────────────────────────────────────────────────────┘\n\n")

                # Rodapé
                file.write("\n" + "─" * 60 + "\n")
                file.write("Relatório gerado automaticamente pelo OrçaFácil\n")
                file.write("💙 Controle suas finanças com facilidade!\n")
                file.write("─" * 60 + "\n")

            print(f"✅ Arquivo de texto exportado: {filepath}")

            # Mensagem final baseada na extensão
            if is_pdf_extension:
                messagebox.showinfo(
                    "Exportação Concluída",
                    f"📄 Arquivo salvo como: {os.path.basename(filepath)}\n\n"
                    "💡 Este é um arquivo de TEXTO com extensão .pdf\n"
                    "📖 Para abrir: Use Bloco de Notas, VS Code ou Word\n"
                    "❌ Navegadores podem não abrir corretamente\n\n"
                    "Sugestão: Na próxima vez use a extensão .txt"
                )
            else:
                messagebox.showinfo(
                    "✅ Exportação Concluída",
                    f"📄 Arquivo de texto salvo com sucesso!\n\n"
                    f"Arquivo: {os.path.basename(filepath)}\n"
                    f"Local: {filepath}\n\n"
                    "📖 Pode ser aberto em qualquer editor de texto"
                )

            return True

        except Exception as e:
            print(f"❌ Erro ao exportar arquivo de texto: {e}")
            return False


if __name__ == "__main__":
    # Teste da janela
    app = ctk.CTk()
    app.withdraw()


    class MockDBService:
        def get_all_transactions(self):
            return [
                {'id': 1, 'date': '2024-10-18 10:00:00', 'type': 'Receita', 'category': 'Salário', 'value': 2500.00,
                 'description': 'Salário mensal'},
                {'id': 2, 'date': '2024-10-18 12:00:00', 'type': 'Despesa', 'category': 'Alimentação', 'value': 45.50,
                 'description': 'Almoço'},
            ]

        def get_financial_summary(self):
            return {'total_revenue': 2500.00, 'total_expense': 45.50, 'balance': 2454.50}


    export_win = ExportWindow(app, MockDBService())
    app.mainloop()