from datetime import datetime, timedelta

from celery import shared_task

from borrowing.models import Borrowing
from borrowing.telegram_utils import send_telegram_message


@shared_task
def check_overdue_borrowings():
    now = datetime.now()
    tomorrow = now + timedelta(days=1)

    all_borrowings = Borrowing.objects.filter(actual_return_date__isnull=True)

    if all_borrowings.exists():
        for borrowing in all_borrowings:
            status = (
                "Overdue" if borrowing.expected_return_date <= now else "Not overdue"
            )
            message = (
                f"Borrowing status:\n"
                f"User: {borrowing.user.email}\n"
                f"Book: {borrowing.book.title}\n"
                f"Expected return date: {borrowing.expected_return_date}\n"
                f"Status: {status}\n"
            )
            try:
                send_telegram_message(message)
            except Exception as e:
                pass
    else:
        try:
            send_telegram_message("No active borrowings today!")
        except Exception as e:
            pass
