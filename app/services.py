from datetime import date
from app.exceptions import WrongDatesException


def correct_date_check(date_from: date, date_to: date):
    if date_from >= date_to or (date_to - date_from).days > 30:
        raise WrongDatesException
