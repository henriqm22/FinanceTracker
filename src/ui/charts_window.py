# ui/charts_window.py
import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter.messagebox as messagebox
from datetime import datetime, timedelta


class ChartsWindow(ctk.CTkToplevel):
    def __init__(self, parent, db_service):
        super().__init__(parent)
        self.db_service = db_service
        self.parent = parent

        # Configurações da janela
        self.title("📊 Gráficos Financeiros")
        self.geometry("800x600")
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()

        self.create_widgets()
        self.center_window()

    def center_window(self):
        """Centraliza a janela na tela"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def create_widgets(self):
        """Cria os widgets da janela de gráficos"""
        # Frame principal
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)

        # Título
        title_label = ctk.CTkLabel(main_frame, text="📊 Análise Gráfica",
                                   font=ctk.CTkFont(size=20, weight="bold"))
        title_label.pack(pady=(0, 15))

        # Frame de controles
        controls_frame = ctk.CTkFrame(main_frame)
        controls_frame.pack(fill="x", pady=(0, 15))

        # Tipo de gráfico
        ctk.CTkLabel(controls_frame, text="Tipo de Gráfico:",
                     font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.chart_type = ctk.StringVar(value="pie")

        chart_types = [
            ("Pizza - Receitas vs Despesas", "pie"),
            ("Barras - Por Categoria", "bar"),
            ("Linhas - Evolução Mensal", "line")
        ]

        for i, (text, value) in enumerate(chart_types):
            radio = ctk.CTkRadioButton(controls_frame, text=text, variable=self.chart_type, value=value)
            radio.grid(row=0, column=i + 1, padx=10, pady=10)

        # Período
        ctk.CTkLabel(controls_frame, text="Período:",
                     font=ctk.CTkFont(weight="bold")).grid(row=1, column=0, padx=10, pady=10, sticky="w")

        self.period = ctk.StringVar(value="all")

        periods = [
            ("Todos os dados", "all"),
            ("Últimos 30 dias", "30days"),
            ("Este mês", "this_month")
        ]

        for i, (text, value) in enumerate(periods):
            radio = ctk.CTkRadioButton(controls_frame, text=text, variable=self.period, value=value)
            radio.grid(row=1, column=i + 1, padx=10, pady=10)

        # Botão atualizar
        update_btn = ctk.CTkButton(controls_frame, text="🔄 Atualizar Gráfico",
                                   command=self.update_chart)
        update_btn.grid(row=0, column=4, rowspan=2, padx=20, pady=10)

        # Configurar grid
        for i in range(5):
            controls_frame.grid_columnconfigure(i, weight=1)

        # Frame do gráfico
        self.chart_frame = ctk.CTkFrame(main_frame)
        self.chart_frame.pack(fill="both", expand=True)

        # Gerar gráfico inicial
        self.update_chart()

    def update_chart(self):
        """Atualiza o gráfico baseado nas seleções"""
        try:
            # Limpar frame do gráfico
            for widget in self.chart_frame.winfo_children():
                widget.destroy()

            # Buscar dados
            transactions = self.db_service.get_all_transactions()

            if not transactions:
                ctk.CTkLabel(self.chart_frame, text="📊 Não há dados suficientes para gerar gráficos",
                             font=ctk.CTkFont(size=16)).pack(expand=True)
                return

            # Filtrar por período se necessário
            transactions = self.filter_by_period(transactions)

            # Criar gráfico baseado no tipo selecionado
            chart_type = self.chart_type.get()

            if chart_type == "pie":
                self.create_pie_chart(transactions)
            elif chart_type == "bar":
                self.create_bar_chart(transactions)
            elif chart_type == "line":
                self.create_line_chart(transactions)

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar gráfico: {e}")

    def filter_by_period(self, transactions):
        """Filtra transações pelo período selecionado"""
        period = self.period.get()

        if period == "all":
            return transactions

        now = datetime.now()
        filtered = []

        for transaction in transactions:
            try:
                # Converter data da transação
                trans_date = datetime.strptime(transaction['date'][:10], '%Y-%m-%d')

                if period == "30days":
                    if now - trans_date <= timedelta(days=30):
                        filtered.append(transaction)
                elif period == "this_month":
                    if trans_date.year == now.year and trans_date.month == now.month:
                        filtered.append(transaction)

            except:
                filtered.append(transaction)  # Incluir se não conseguir converter data

        return filtered

    def create_pie_chart(self, transactions):
        """Cria gráfico de pizza - Receitas vs Despesas"""
        # Calcular totais
        total_receitas = sum(t['value'] for t in transactions if t['type'] == 'Receita')
        total_despesas = sum(t['value'] for t in transactions if t['type'] == 'Despesa')

        if total_receitas == 0 and total_despesas == 0:
            ctk.CTkLabel(self.chart_frame, text="📊 Não há dados para o gráfico",
                         font=ctk.CTkFont(size=16)).pack(expand=True)
            return

        # Criar figura
        fig, ax = plt.subplots(figsize=(8, 6))

        # Dados para o gráfico
        labels = ['Receitas', 'Despesas']
        sizes = [total_receitas, total_despesas]
        colors = ['#2ecc71', '#e74c3c']
        explode = (0.1, 0)  # Destacar receitas

        # Criar gráfico de pizza
        wedges, texts, autotexts = ax.pie(sizes, explode=explode, labels=labels, colors=colors,
                                          autopct='%1.1f%%', shadow=True, startangle=90)

        # Estilizar
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')

        ax.set_title('📊 Distribuição: Receitas vs Despesas', fontsize=14, fontweight='bold', pad=20)

        # Adicionar legenda com valores
        legend_labels = [f'Receitas: R$ {total_receitas:,.2f}', f'Despesas: R$ {total_despesas:,.2f}']
        ax.legend(wedges, legend_labels, title="Valores Totais", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))

        self.embed_chart(fig)

    def create_bar_chart(self, transactions):
        """Cria gráfico de barras - Gastos por categoria"""
        # Agrupar despesas por categoria
        categorias = {}
        for transaction in transactions:
            if transaction['type'] == 'Despesa':
                categoria = transaction['category']
                if categoria not in categorias:
                    categorias[categoria] = 0
                categorias[categoria] += transaction['value']

        if not categorias:
            ctk.CTkLabel(self.chart_frame, text="📊 Não há despesas para mostrar",
                         font=ctk.CTkFont(size=16)).pack(expand=True)
            return

        # Ordenar categorias por valor
        categorias_ordenadas = dict(sorted(categorias.items(), key=lambda x: x[1], reverse=True))

        # Criar figura
        fig, ax = plt.subplots(figsize=(10, 6))

        # Dados para o gráfico
        categorias_nomes = list(categorias_ordenadas.keys())
        categorias_valores = list(categorias_ordenadas.values())

        # Criar gráfico de barras
        bars = ax.bar(categorias_nomes, categorias_valores, color='#3498db', alpha=0.7)

        # Adicionar valores nas barras
        for bar, valor in zip(bars, categorias_valores):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2., height + 0.1,
                    f'R$ {valor:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.'),
                    ha='center', va='bottom', fontweight='bold')

        # Configurar eixo Y
        ax.set_ylabel('Valor (R$)', fontweight='bold')
        ax.set_xlabel('Categorias', fontweight='bold')
        ax.set_title('📈 Despesas por Categoria', fontsize=14, fontweight='bold', pad=20)

        # Rotacionar labels do eixo X se necessário
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        self.embed_chart(fig)

    def create_line_chart(self, transactions):
        """Cria gráfico de linhas - Evolução mensal"""
        # Agrupar por mês
        meses = {}
        for transaction in transactions:
            try:
                # Extrair ano-mês da data
                data_parts = transaction['date'][:7]  # YYYY-MM
                if data_parts not in meses:
                    meses[data_parts] = {'receitas': 0, 'despesas': 0}

                if transaction['type'] == 'Receita':
                    meses[data_parts]['receitas'] += transaction['value']
                else:
                    meses[data_parts]['despesas'] += transaction['value']
            except:
                continue

        if len(meses) < 2:
            ctk.CTkLabel(self.chart_frame,
                         text="📊 Dados insuficientes para gráfico de evolução\n(necessário pelo menos 2 meses)",
                         font=ctk.CTkFont(size=14)).pack(expand=True)
            return

        # Ordenar meses
        meses_ordenados = sorted(meses.items())

        # Extrair dados
        labels = [f"{mes[5:7]}/{mes[2:4]}" for mes, _ in meses_ordenados]  # Formato MM/AA
        receitas = [dados['receitas'] for _, dados in meses_ordenados]
        despesas = [dados['despesas'] for _, dados in meses_ordenados]
        saldos = [receitas[i] - despesas[i] for i in range(len(receitas))]

        # Criar figura
        fig, ax = plt.subplots(figsize=(10, 6))

        # Criar gráfico de linhas
        ax.plot(labels, receitas, marker='o', linewidth=2, label='Receitas', color='#2ecc71')
        ax.plot(labels, despesas, marker='s', linewidth=2, label='Despesas', color='#e74c3c')
        ax.plot(labels, saldos, marker='^', linewidth=2, label='Saldo', color='#3498db', linestyle='--')

        # Adicionar área sob as curvas
        ax.fill_between(labels, receitas, alpha=0.2, color='#2ecc71')
        ax.fill_between(labels, despesas, alpha=0.2, color='#e74c3c')

        # Configurações do gráfico
        ax.set_ylabel('Valor (R$)', fontweight='bold')
        ax.set_xlabel('Mês', fontweight='bold')
        ax.set_title('📈 Evolução Financeira Mensal', fontsize=14, fontweight='bold', pad=20)
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        self.embed_chart(fig)

    def embed_chart(self, fig):
        """Embute o gráfico matplotlib no tkinter"""
        canvas = FigureCanvasTkAgg(fig, self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)