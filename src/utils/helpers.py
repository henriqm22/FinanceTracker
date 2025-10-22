# src/utils/helpers.py
import os
from datetime import datetime, timedelta


def format_currency(value: float) -> str:
    """Formata valor como moeda brasileira"""
    return f"R$ {value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')


def get_month_range(month_offset=0):
    """Retorna data inicial e final do mês (com offset)"""
    today = datetime.now()
    target_month = today.month + month_offset

    year = today.year + (target_month - 1) // 12
    month = (target_month - 1) % 12 + 1

    first_day = datetime(year, month, 1)

    if month == 12:
        last_day = datetime(year + 1, 1, 1) - timedelta(days=1)
    else:
        last_day = datetime(year, month + 1, 1) - timedelta(days=1)

    return first_day.strftime('%Y-%m-%d'), last_day.strftime('%Y-%m-%d')


def ensure_directory(path: str):
    """Garante que um diretório existe"""
    os.makedirs(path, exist_ok=True)