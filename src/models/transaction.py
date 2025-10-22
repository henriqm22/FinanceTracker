# models/transaction.py
from datetime import datetime


class Transaction:
    def __init__(self, type, category, value, date=None, description=''):
        self.type = type  # 'Receita' ou 'Despesa'
        self.category = category
        self.value = float(value)
        # Agora inclui data E hora
        if date:
            self.date = date
        else:
            self.date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.description = description

    def __str__(self):
        return f"<Transação tipo={self.type}, valor={self.value}, categoria={self.category}>"

    def to_dict(self):
        return {
            'type': self.type,
            'category': self.category,
            'value': self.value,
            'date': self.date,
            'description': self.description
        }