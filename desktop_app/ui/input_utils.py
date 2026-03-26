from datetime import datetime


def clean_text(value):
    return (value or "").strip()


def parse_non_negative_float(raw, field_name):
    text = clean_text(raw)
    if text == "":
        return 0.0, None
    try:
        value = float(text)
    except ValueError:
        return None, f"{field_name}必須是數字"
    if value < 0:
        return None, f"{field_name}不可為負數"
    return value, None


def parse_positive_float(raw, field_name):
    text = clean_text(raw)
    if text == "":
        return None, f"{field_name}不可空白"
    try:
        value = float(text)
    except ValueError:
        return None, f"{field_name}必須是數字"
    if value <= 0:
        return None, f"{field_name}必須大於 0"
    return value, None


def parse_optional_non_negative_int(raw, field_name):
    text = clean_text(raw)
    if text == "":
        return None, None
    try:
        value = int(text)
    except ValueError:
        return None, f"{field_name}必須是整數"
    if value < 0:
        return None, f"{field_name}不可為負數"
    return value, None


def validate_date_yyyy_mm_dd(date_text):
    text = clean_text(date_text)
    try:
        datetime.strptime(text, "%Y-%m-%d")
    except ValueError:
        return False
    return True
