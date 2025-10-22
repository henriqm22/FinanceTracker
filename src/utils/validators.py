# utils/validators.py
from datetime import datetime

def validate_date_br(date_string):
    """Valida formato de data dd/mm/aaaa"""
    try:
        datetime.strptime(date_string, '%d/%m/%Y')
        return True
    except ValueError:
        return False

def validate_datetime_br(datetime_string):
    """Valida formato de data e hora dd/mm/aaaa hh:mm"""
    try:
        datetime.strptime(datetime_string, '%d/%m/%Y %H:%M')
        return True
    except ValueError:
        return False

def convert_date_br_to_db(date_br):
    """Converte dd/mm/aaaa para aaaa-mm-dd (formato banco)"""
    try:
        date_obj = datetime.strptime(date_br, '%d/%m/%Y')
        return date_obj.strftime('%Y-%m-%d %H:%M:%S')
    except ValueError:
        return None

def convert_datetime_br_to_db(datetime_br):
    """Converte dd/mm/aaaa hh:mm para aaaa-mm-dd hh:mm:ss (formato banco)"""
    try:
        datetime_obj = datetime.strptime(datetime_br, '%d/%m/%Y %H:%M')
        return datetime_obj.strftime('%Y-%m-%d %H:%M:%S')
    except ValueError:
        return None

def convert_datetime_db_to_br(datetime_db):
    """Converte aaaa-mm-dd hh:mm:ss (banco) para dd/mm/aaaa hh:mm (exibição)"""
    try:
        datetime_obj = datetime.strptime(datetime_db, '%Y-%m-%d %H:%M:%S')
        return datetime_obj.strftime('%d/%m/%Y %H:%M')
    except ValueError:
        # Tenta converter se for só data
        try:
            date_obj = datetime.strptime(datetime_db, '%Y-%m-%d')
            return date_obj.strftime('%d/%m/%Y 00:00')
        except ValueError:
            return datetime_db

def convert_date_db_to_br(date_db):
    """Converte aaaa-mm-dd (banco) para dd/mm/aaaa (exibição) - para compatibilidade"""
    try:
        date_obj = datetime.strptime(date_db, '%Y-%m-%d')
        return date_obj.strftime('%d/%m/%Y')
    except ValueError:
        return date_db

def validate_amount(amount_str):
    """Valida valor monetário e retorna (é_válido, valor)"""
    try:
        value_str = amount_str.replace(',', '.')
        value = float(value_str)
        return (value > 0, value)
    except ValueError:
        return (False, 0.0)

def validate_category(category: str, available_categories: list) -> bool:
    """Valida se categoria existe na lista"""
    return category in available_categories

def validate_transaction_type(trans_type: str) -> bool:
    """Valida tipo de transação"""
    return trans_type in ['Receita', 'Despesa']