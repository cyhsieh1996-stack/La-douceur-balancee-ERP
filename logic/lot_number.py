# logic/lot_number.py
import datetime

def generate_lot_number(item_id: str, date: datetime.date = None) -> str:
    """
    Lot 格式：
    YY + WW + D + item_id(4)
    例：254303FNMT
    """
    if date is None:
        date = datetime.date.today()

    yy = str(date.year % 100).zfill(2)
    ww = str(date.isocalendar().week).zfill(2)
    d = str(date.isocalendar().weekday)  # 1–7

    item_code = item_id.upper()[-4:]

    return f"{yy}{ww}{d}{item_code}"
