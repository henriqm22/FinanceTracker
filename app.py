from flask import Flask, render_template, jsonify, request
import sqlite3
import json
from datetime import datetime
from collections import defaultdict

app = Flask(__name__)

# Configurações
DATABASE = 'database.db'


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    conn.execute('''
                 CREATE TABLE IF NOT EXISTS transactions
                 (
                     id
                     INTEGER
                     PRIMARY
                     KEY
                     AUTOINCREMENT,
                     tipo
                     TEXT
                     NOT
                     NULL,
                     categoria
                     TEXT
                     NOT
                     NULL,
                     valor
                     REAL
                     NOT
                     NULL,
                     descricao
                     TEXT,
                     date
                     TIMESTAMP
                     DEFAULT
                     CURRENT_TIMESTAMP
                 )
                 ''')
    conn.commit()
    conn.close()


# Rotas de páginas
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/transactions')
def transactions():
    return render_template('transactions.html')


@app.route('/charts')
def charts():
    return render_template('charts.html')


# API Routes
@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    conn = get_db_connection()
    transactions = conn.execute('SELECT * FROM transactions ORDER BY date DESC').fetchall()
    conn.close()

    transactions_list = []
    for trans in transactions:
        transactions_list.append({
            'id': trans['id'],
            'tipo': trans['tipo'],
            'categoria': trans['categoria'],
            'valor': trans['valor'],
            'descricao': trans['descricao'],
            'data': trans['date']
        })

    return jsonify(transactions_list)


@app.route('/api/transactions', methods=['POST'])
def add_transaction():
    try:
        data = request.get_json()

        conn = get_db_connection()
        cursor = conn.execute(
            'INSERT INTO transactions (tipo, categoria, valor, descricao) VALUES (?, ?, ?, ?)',
            (data['tipo'], data['categoria'], data['valor'], data.get('descricao', ''))
        )
        conn.commit()
        transaction_id = cursor.lastrowid
        conn.close()

        return jsonify({
            'status': 'success',
            'message': 'Transação adicionada!',
            'id': transaction_id
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/transactions/<int:transaction_id>', methods=['PUT'])
def update_transaction(transaction_id):
    data = request.get_json()

    conn = get_db_connection()
    conn.execute(
        'UPDATE transactions SET tipo = ?, categoria = ?, valor = ?, descricao = ? WHERE id = ?',
        (data['tipo'], data['categoria'], data['valor'], data.get('descricao', ''), transaction_id)
    )
    conn.commit()
    conn.close()

    return jsonify({'status': 'success', 'message': 'Transação atualizada!'})


@app.route('/api/transactions/<int:transaction_id>', methods=['DELETE'])
def delete_transaction(transaction_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM transactions WHERE id = ?', (transaction_id,))
    conn.commit()
    conn.close()

    return jsonify({'status': 'success', 'message': 'Transação excluída!'})


@app.route('/api/charts/data')
def get_charts_data():
    conn = get_db_connection()
    transactions = conn.execute('SELECT * FROM transactions').fetchall()
    conn.close()

    # Dados para gráfico de pizza (Receitas vs Despesas)
    pie_data = []
    receitas_total = sum(t['valor'] for t in transactions if t['tipo'] == 'Receita')
    despesas_total = sum(t['valor'] for t in transactions if t['tipo'] == 'Despesa')

    if receitas_total > 0:
        pie_data.append({'type': 'Receita', 'total': receitas_total})
    if despesas_total > 0:
        pie_data.append({'type': 'Despesa', 'total': despesas_total})

    # Dados para gráfico de barras (Despesas por categoria)
    bar_data = []
    despesas_por_categoria = defaultdict(float)

    for trans in transactions:
        if trans['tipo'] == 'Despesa':
            despesas_por_categoria[trans['categoria']] += trans['valor']

    for categoria, total in despesas_por_categoria.items():
        bar_data.append({'category': categoria, 'total': total})

    # Dados para gráfico de linhas (Evolução mensal)
    line_data = []
    transacoes_por_mes = defaultdict(lambda: {'revenue': 0, 'expense': 0})

    for trans in transactions:
        try:
            if trans['date']:
                data_obj = datetime.strptime(trans['date'], '%Y-%m-%d %H:%M:%S')
                mes_ano = data_obj.strftime('%Y-%m')

                if trans['tipo'] == 'Receita':
                    transacoes_por_mes[mes_ano]['revenue'] += trans['valor']
                else:
                    transacoes_por_mes[mes_ano]['expense'] += trans['valor']
        except (ValueError, TypeError):
            continue

    for mes, totais in sorted(transacoes_por_mes.items()):
        line_data.append({
            'month': mes,
            'revenue': totais['revenue'],
            'expense': totais['expense']
        })

    return jsonify({
        'pie': pie_data,
        'bar': bar_data,
        'line': line_data
    })


@app.route('/api/export/<format_type>')
def export_data(format_type):
    conn = get_db_connection()
    transactions = conn.execute('SELECT * FROM transactions ORDER BY date DESC').fetchall()
    conn.close()

    transactions_list = []
    for trans in transactions:
        transactions_list.append({
            'id': trans['id'],
            'tipo': trans['tipo'],
            'categoria': trans['categoria'],
            'valor': trans['valor'],
            'descricao': trans['descricao'],
            'data': trans['date']
        })

    if format_type == 'json':
        return jsonify(transactions_list)
    elif format_type == 'csv':
        csv_content = "ID,Data,Tipo,Categoria,Valor,Descrição\n"
        for trans in transactions_list:
            csv_content += f"{trans['id']},{trans['data']},{trans['tipo']},{trans['categoria']},{trans['valor']},{trans['descricao'] or ''}\n"

        from flask import Response
        return Response(
            csv_content,
            mimetype="text/csv",
            headers={"Content-disposition": "attachment; filename=transacoes.csv"}
        )

    return jsonify({'error': 'Formato não suportado'})


# Rota de teste
@app.route('/api/test')
def test_api():
    return jsonify({"status": "API working", "message": "Flask está respondendo!"})


if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)