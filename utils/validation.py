import re


def validate_email(email: str) -> bool:
    """Valide le format d'un email."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone: str) -> bool:
    """Valide le format d'un numéro de téléphone."""
    pattern = r'^(\+212|0)[5-7]\d{8}$'
    return re.match(pattern, phone) is not None
