# E-Commerce Django Project

A full-featured e-commerce platform built with Django.

## 🚀 Quick Setup

1. Download the ZIP or clone the repo:
```bash
git clone https://github.com/HazemAymanNobody/E-Commerce-Django-Graduation-Project.git
cd E-Commerce-Django-Graduation-Project
```

2. Create and activate virtual environment:
```bash
# Windows
python -m venv env
.\env\Scripts\activate

# Linux/Mac
python -m venv env
source env/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Create superuser (optional):
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

7. Access the application:
- Main site: http://127.0.0.1:8000/
- Admin panel: http://127.0.0.1:8000/admin/

✅ The database (db.sqlite3) is already included.

## Features

- User Authentication
- Product Management
- Shopping Cart
- Payment Integration (Stripe & PayPal)
- Order Management
- Vendor Dashboard
- Admin Dashboard
- Product Reviews
- Wishlist
- Search & Filter
- Responsive Design

## Configuration (Optional)

For payment processing and email functionality, create a `.env` file in the root directory:

```
# Payment Gateway Keys
STRIPE_SECRET_KEY=your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key
PAYPAL_RECEIVER_EMAIL=your-paypal-email@example.com
PAYPAL_CLIENT_ID=your-paypal-client-id
PAYPAL_SECRET_KEY=your-paypal-secret-key

# Django Settings
DEBUG=True
SECRET_KEY=your-django-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1

# Email Settings (Optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-specific-password
```

## Troubleshooting

If you encounter any issues:
1. Make sure your virtual environment is activated
2. Verify that all requirements are installed correctly
3. Check if the database migrations were applied successfully

## License

This project is licensed under the MIT License.
