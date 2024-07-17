from datetime import datetime


def calculate_total_price(borrowing):
    borrow_date = borrowing.borrow_date
    expected_return_date = borrowing.expected_return_date

    if isinstance(borrow_date, datetime):
        borrow_date = borrow_date.date()
    if isinstance(expected_return_date, datetime):
        expected_return_date = expected_return_date.date()

    days_borrowed = (expected_return_date - borrow_date).days
    daily_fee = borrowing.book.daily_fee

    return days_borrowed * daily_fee
