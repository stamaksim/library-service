# Library Service Project

## Project Description

The Library Service Project is designed to modernize the management system of a local library. The current system is
outdated, relying on manual processes for tracking books, borrowings, users, and payments. This project aims to
implement an online management system to optimize library operations, improve user experience, and introduce automated
notifications and online payments.

## Resources

### Book

- **Title**: string
- **Author**: string
- **Cover**: Enum: HARD | SOFT
- **Inventory**: positive integer (number of available copies)
- **Daily fee**: decimal (in $USD)

### User (Customer)

- **Email**: string
- **First name**: string
- **Last name**: string
- **Password**: string
- **Is staff**: boolean

### Borrowing

- **Borrow date**: date
- **Expected return date**: date
- **Actual return date**: date
- **Book id**: integer
- **User id**: integer

### Payment

- **Status**: Enum: PENDING | PAID
- **Type**: Enum: PAYMENT | FINE
- **Borrowing id**: integer
- **Session url**: URL (Stripe payment session URL)
- **Session id**: string (Stripe payment session ID)
- **Money to pay**: decimal (total borrowing price in $USD)

## Components

### Books Service

Manage book inventory (CRUD operations).

#### API Endpoints

- **POST**: `books/` - Add a new book
- **GET**: `books/` - Get a list of books
- **GET**: `books/<id>/` - Get book details
- **PUT/PATCH**: `books/<id>/` - Update book (including inventory)
- **DELETE**: `books/<id>/` - Delete book

### Users Service

Manage user authentication and registration.

#### API Endpoints

- **POST**: `users/` - Register a new user
- **POST**: `users/token/` - Get JWT tokens
- **POST**: `users/token/refresh/` - Refresh JWT token
- **GET**: `users/me/` - Get profile info
- **PUT/PATCH**: `users/me/` - Update profile info

### Borrowings Service

Manage user borrowings of books.

#### API Endpoints

- **POST**: `borrowings/` - Add new borrowing (decrease inventory by 1)
- **GET**: `borrowings/?user_id=...&is_active=...` - Get borrowings by user ID and active status
- **GET**: `borrowings/<id>/` - Get specific borrowing
- **POST**: `borrowings/<id>/return/` - Set actual return date (increase inventory by 1)

### Notifications Service (Telegram)

Send notifications about new borrowings, overdue borrowings, and successful payments.

### Payments Service (Stripe)

Handle payments for book borrowings.

#### API Endpoints

- **GET**: `success/` - Check successful Stripe payment
- **GET**: `cancel/` - Return payment paused message

## Project Setup

### Prerequisites

- Python 3.11
- Django 5.0.6
- PostgreSQL (or any preferred database)
- Stripe account (for payment integration)
- Telegram account (for notification integration)

### Installation

1. **Clone the repository:**
    ```bash
    git clone https://github.com/stamaksim/library-service
    cd library-service
    ```

2. **Create a virtual environment and activate it:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4. **Set up the database:**
    ```bash
    python manage.py migrate
    ```

5. **Create a superuser:**
    ```bash
    python manage.py createsuperuser
    ```

6. **Run the development server:**
    ```bash
    python manage.py runserver
    ```

## Contributing

1. **Fork the repository.**
2. **Create a feature branch:**
    ```bash
    git checkout -b feature/fooBar
    ```
3. **Commit your changes:**
    ```bash
    git commit -am 'Add some fooBar'
    ```
4. **Push to the branch:**
    ```bash
    git push origin feature/fooBar
    ```
5. **Create a new Pull Request.**

## Contact

Maks - [maksymstakhovskyi@yahoo.com](mailto:maksymstakhovskyi@yahoo.com)

Project Link: [https://github.com/stamaksim/library-service](https://github.com/stamaksim/library-service)
