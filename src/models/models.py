from dataclasses import dataclass
from datetime import datetime
from typing import Literal

TransactionType = Literal['income', 'expense']


@dataclass
class Transaction:
    id: int
    description: str
    amount: float
    category: str
    type: TransactionType
    date: str
    created_at: str

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'description': self.description,
            'amount': self.amount,
            'category': self.category,
            'type': self.type,
            'date': self.date,
            'created_at': self.created_at
        }


@dataclass
class FinancialSummary:
    total_income: float
    total_expenses: float
    balance: float
    transactions_count: int