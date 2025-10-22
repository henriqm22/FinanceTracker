# services/database_service.py
import sqlite3
import os
from datetime import datetime
from models.transaction import Transaction


class DatabaseService:
    def __init__(self, db_path=None):
        # Encontrar o caminho absoluto correto
        if db_path is None:
            # Sobe da pasta services para a raiz do projeto
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(project_root, 'data', 'finance.db')

        self.db_path = db_path
        print(f"Database path: {self.db_path}")

        # Garantir que o diretório existe
        db_dir = os.path.dirname(self.db_path)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)
            print(f"Pasta criada: {db_dir}")

        self.init_database()

    def init_database(self):
        """Inicializa o banco de dados com as tabelas necessárias"""
        try:
            print(f"Tentando conectar ao banco: {self.db_path}")

            # Testar se podemos escrever no diretório
            test_file = os.path.join(os.path.dirname(self.db_path), "test_write.tmp")
            try:
                with open(test_file, 'w') as f:
                    f.write("test")
                os.remove(test_file)
                print("Permissão de escrita: OK")
            except Exception as e:
                print(f"Sem permissão de escrita: {e}")
                # Fallback: usar pasta do usuário
                user_dir = os.path.expanduser("~")
                self.db_path = os.path.join(user_dir, "FinanceTracker_data", "finance.db")
                print(f"Usando fallback: {self.db_path}")
                os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Tabela de transações
                cursor.execute('''
                               CREATE TABLE IF NOT EXISTS transactions
                               (
                                   id
                                   INTEGER
                                   PRIMARY
                                   KEY
                                   AUTOINCREMENT,
                                   type
                                   TEXT
                                   NOT
                                   NULL
                                   CHECK (
                                   type
                                   IN
                               (
                                   'Receita',
                                   'Despesa'
                               )),
                                   category TEXT NOT NULL,
                                   value REAL NOT NULL,
                                   date TEXT NOT NULL,
                                   description TEXT,
                                   created_at TEXT NOT NULL
                                   )
                               ''')

                # Tabela de categorias
                cursor.execute('''
                               CREATE TABLE IF NOT EXISTS categories
                               (
                                   id
                                   INTEGER
                                   PRIMARY
                                   KEY
                                   AUTOINCREMENT,
                                   name
                                   TEXT
                                   NOT
                                   NULL
                                   UNIQUE,
                                   type
                                   TEXT
                                   NOT
                                   NULL
                                   CHECK (
                                   type
                                   IN
                               (
                                   'Receita',
                                   'Despesa'
                               ))
                                   )
                               ''')

                # Categorias padrão
                default_categories = [
                    ('Salário', 'Receita'),
                    ('Freelance', 'Receita'),
                    ('Investimentos', 'Receita'),
                    ('Alimentação', 'Despesa'),
                    ('Transporte', 'Despesa'),
                    ('Moradia', 'Despesa'),
                    ('Lazer', 'Despesa'),
                    ('Saúde', 'Despesa'),
                    ('Educação', 'Despesa')
                ]

                cursor.executemany('''
                                   INSERT
                                   OR IGNORE INTO categories (name, type) VALUES (?, ?)
                                   ''', default_categories)

                conn.commit()
                print("✅ Banco de dados inicializado com sucesso!")

        except Exception as e:
            print(f"❌ Erro crítico ao inicializar banco: {e}")
            # Último fallback - banco na memória
            print("🚨 Usando banco em memória como fallback")
            self.db_path = ":memory:"

    def add_transaction(self, transaction: Transaction) -> bool:
        """Adiciona uma nova transação ao banco"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                               INSERT INTO transactions (type, category, value, date, description, created_at)
                               VALUES (?, ?, ?, ?, ?, ?)
                               ''', (
                                   transaction.type,
                                   transaction.category,
                                   transaction.value,
                                   transaction.date,
                                   transaction.description,
                                   datetime.now().isoformat()
                               ))
                conn.commit()
                return True
        except Exception as e:
            print(f"Erro ao adicionar transação: {e}")
            return False

    def update_transaction(self, transaction_id, transaction_type, category, value, date, description):
        """Atualiza uma transação existente"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                               UPDATE transactions
                               SET type        = ?,
                                   category    = ?,
                                   value       = ?,
                                   date        = ?,
                                   description = ?
                               WHERE id = ?
                               ''', (transaction_type, category, value, date, description, transaction_id))
                conn.commit()
                return True
        except Exception as e:
            print(f"Erro ao atualizar transação: {e}")
            return False

    def get_all_transactions(self):
        """Recupera todas as transações"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('''
                               SELECT *
                               FROM transactions
                               ORDER BY id DESC
                               ''')
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Erro ao buscar transações: {e}")
            return []

    def get_all_transactions_sorted(self, sort_column='id', ascending=True):
        """Recupera transações ordenadas por qualquer coluna"""
        try:
            # Mapear colunas para nomes reais no banco
            column_mapping = {
                'id': 'id',
                'date': 'date',
                'type': 'type',
                'category': 'category',
                'value': 'value',
                'description': 'description'
            }

            # Validar coluna
            if sort_column not in column_mapping:
                sort_column = 'id'  # Fallback

            # Determinar direção
            direction = 'ASC' if ascending else 'DESC'

            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                query = f'''
                    SELECT * FROM transactions 
                    ORDER BY {column_mapping[sort_column]} {direction}
                '''

                cursor.execute(query)
                transactions = [dict(row) for row in cursor.fetchall()]

                print(f"DEBUG - Ordenado por: {sort_column} {direction}")
                print(f"DEBUG - IDs: {[t['id'] for t in transactions]}")

                return transactions

        except Exception as e:
            print(f"Erro ao buscar transações ordenadas: {e}")
            return self.get_all_transactions()  # Fallback

    def get_categories_by_type(self, type_filter=None):
        """Recupera categorias, opcionalmente filtradas por tipo"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                if type_filter:
                    cursor.execute("SELECT name FROM categories WHERE type = ?", (type_filter,))
                else:
                    cursor.execute("SELECT name FROM categories")

                return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            print(f"Erro ao buscar categorias: {e}")
            return []

    def get_financial_summary(self):
        """Retorna resumo financeiro"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute('''
                               SELECT SUM(CASE WHEN type = 'Receita' THEN value ELSE 0 END) as total_revenue,
                                      SUM(CASE WHEN type = 'Despesa' THEN value ELSE 0 END) as total_expense,
                                      COUNT(*)                                              as transaction_count
                               FROM transactions
                               ''')

                result = cursor.fetchone()
                total_revenue = result[0] or 0
                total_expense = result[1] or 0
                balance = total_revenue - total_expense

                return {
                    'total_revenue': total_revenue,
                    'total_expense': total_expense,
                    'balance': balance,
                    'transaction_count': result[2]
                }
        except Exception as e:
            print(f"Erro ao calcular resumo: {e}")
            return {
                'total_revenue': 0,
                'total_expense': 0,
                'balance': 0,
                'transaction_count': 0
            }

    def delete_transaction(self, transaction_id: int) -> bool:
        """Exclui uma transação"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
                conn.commit()
                return True
        except Exception as e:
            print(f"Erro ao excluir transação: {e}")
            return False