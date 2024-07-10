from datetime import datetime

import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY
from .models import Payment


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


def create_stripe_session(borrowing, user):
    total_price = calculate_total_price(borrowing)
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": "Library Payment",
                    },
                    "unit_amount": int(total_price * 100),  # amount in cents
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url="http://localhost:8000/api/payments/success/",
        cancel_url="http://localhost:8000/api/payments/cancel/",
    )

    payment = Payment.objects.create(
        status=Payment.Status.PENDING,
        type=Payment.Type.PAYMENT,
        borrowing=borrowing,
        session_id=session.id,
        money_to_pay=total_price,
        user=user,
    )

    return payment
