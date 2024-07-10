from datetime import datetime, timedelta

from celery import shared_task

from borrowing.models import Borrowing
from borrowing.telegram_utils import send_telegram_message


@shared_task
def check_overdue_borrowings():
    now = datetime.now()
    tomorrow = now + timedelta(days=1)
    overdue_borrowings = Borrowing.objects.filter(
        expected_return_date__lte=tomorrow, actual_return_date__isnull=True
    )

    if overdue_borrowings.exists():
        for borrowing in overdue_borrowings:
            message = (
                f"Overdue borrowing:\n"
                f"User: {borrowing.user.email}\n"
                f"Book: {borrowing.book.title}\n"
                f"Expected return date: {borrowing.expected_return_date}\n"
            )
            send_telegram_message(message)
    else:
        send_telegram_message("No borrowings overdue today!")
