from flask import Flask, render_template, jsonify, request, Response, send_file
import sqlite3
import json
from datetime import datetime
from collections import defaultdict
import io
import csv

app = Flask(__name__)

# Configuração do banco
DATABASE = 'database.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT NOT NULL,
            categoria TEXT NOT NULL,
            valor REAL NOT NULL,
            descricao TEXT,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()


# =================== ROTAS DE PÁGINA ===================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/transactions')
def transactions_page():
    return render_template('transactions.html')

@app.route('/charts')
def charts_page():
    return render_template('charts.html')


# =================== API DE TRANSACOES ===================

@app.get('/api/transacoes')
def get_transacoes():
    conn = get_db_connection()
    rows = conn.execute('SELECT * FROM transactions ORDER BY date DESC').fetchall()
    conn.close()

    data = [{
        'id': row['id'],
        'tipo': row['tipo'],
        'categoria': row['categoria'],
        'valor': row['valor'],
        'descricao': row['descricao'],
        'data': row['date']
    } for row in rows]

    return jsonify(data), 200


@app.post('/api/transacoes')
def add_transacao():
    data = request.get_json(silent=True) or {}

    campos = ['tipo', 'categoria', 'valor', 'descricao']
    if not all(c in data and str(data[c]).strip() for c in campos):
        return jsonify({'error': 'Campos obrigatórios: tipo, categoria, valor, descricao'}), 400

    try:
        valor = float(data['valor'])
        if valor <= 0:
            raise ValueError()
    except Exception:
        return jsonify({'error': 'Valor inválido'}), 400

    conn = get_db_connection()
    cursor = conn.execute(
        'INSERT INTO transactions (tipo, categoria, valor, descricao) VALUES (?, ?, ?, ?)',
        (data['tipo'].strip(), data['categoria'].strip(), valor, data['descricao'].strip())
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()

    return jsonify({
        'id': new_id,
        'tipo': data['tipo'],
        'categoria': data['categoria'],
        'valor': valor,
        'descricao': data['descricao'],
        'data': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }), 201


@app.delete('/api/transacoes/<int:transacao_id>')
def delete_transacao(transacao_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM transactions WHERE id = ?', (transacao_id,))
    conn.commit()
    conn.close()
    return jsonify({'ok': True}), 200


# =================== EXPORTAÇÕES ===================

@app.get('/api/transacoes/export/json')
def export_json():
    conn = get_db_connection()
    rows = conn.execute('SELECT * FROM transactions ORDER BY date DESC').fetchall()
    conn.close()

    data = [{
        'id': row['id'],
        'data': row['date'],
        'tipo': row['tipo'],
        'categoria': row['categoria'],
        'valor': row['valor'],
        'descricao': row['descricao']
    } for row in rows]

    buf = io.BytesIO(json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8'))
    return send_file(buf, mimetype='application/json', as_attachment=True, download_name='transacoes.json')


@app.get('/api/transacoes/export/csv')
def export_csv():
    conn = get_db_connection()
    rows = conn.execute('SELECT * FROM transactions ORDER BY date DESC').fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output, lineterminator='\n')
    writer.writerow(['ID', 'Data', 'Tipo', 'Categoria', 'Valor', 'Descrição'])
    for row in rows:
        writer.writerow([row['id'], row['date'], row['tipo'], row['categoria'], row['valor'], row['descricao']])

    buf = io.BytesIO(output.getvalue().encode('utf-8'))
    return send_file(buf, mimetype='text/csv', as_attachment=True, download_name='transacoes.csv')


# =================== GRÁFICOS ===================

@app.route('/api/charts/data')
def get_charts_data():
    conn = get_db_connection()
    transactions = conn.execute('SELECT * FROM transactions').fetchall()
    conn.close()

    # Gráfico de pizza
    receitas_total = sum(t['valor'] for t in transactions if t['tipo'] == 'Receita')
    despesas_total = sum(t['valor'] for t in transactions if t['tipo'] == 'Despesa')

    pie_data = []
    if receitas_total > 0:
        pie_data.append({'type': 'Receita', 'total': receitas_total})
    if despesas_total > 0:
        pie_data.append({'type': 'Despesa', 'total': despesas_total})

    # Gráfico de barras
    despesas_por_categoria = defaultdict(float)
    for t in transactions:
        if t['tipo'] == 'Despesa':
            despesas_por_categoria[t['categoria']] += t['valor']

    bar_data = [{'category': c, 'total': v} for c, v in despesas_por_categoria.items()]

    # Gráfico de linhas
    transacoes_por_mes = defaultdict(lambda: {'revenue': 0, 'expense': 0})
    for t in transactions:
        try:
            if t['date']:
                dt = datetime.strptime(t['date'], '%Y-%m-%d %H:%M:%S')
                mes_ano = dt.strftime('%Y-%m')
                if t['tipo'] == 'Receita':
                    transacoes_por_mes[mes_ano]['revenue'] += t['valor']
                else:
                    transacoes_por_mes[mes_ano]['expense'] += t['valor']
        except (ValueError, TypeError):
            continue

    line_data = [{'month': m, 'revenue': v['revenue'], 'expense': v['expense']}
                 for m, v in sorted(transacoes_por_mes.items())]

    return jsonify({'pie': pie_data, 'bar': bar_data, 'line': line_data})


# =================== TESTE ===================
@app.route('/api/test')
def test_api():
    return jsonify({'status': 'API funcionando', 'message': 'Flask está respondendo!'})

# =================== MAIN ===================
if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
