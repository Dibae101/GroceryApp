# Grocery Application

This is a Django-based grocery application that allows users to manage grocery items, join groups, and maintain a shopping basket.

## Features

- User authentication (signup, login, logout).
- Grocery item management (add, view, delete).
- Group management (create, join, leave groups).
- Basket functionality (add items, view total cost, remove items).
- Search and filter grocery items.
- Pagination for large datasets.
- Email notifications for group activities.

## Setup Instructions

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)

### Installation

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd project-ecom
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Apply migrations:

   ```bash
   python manage.py migrate
   ```

4. Create a superuser:

   ```bash
   python manage.py createsuperuser
   ```

5. Run the development server:

   ```bash
   python manage.py runserver
   ```

6. Access the application at `http://127.0.0.1:8000/`.

### Deployment

1. Set `DEBUG = False` in `settings.py`.
2. Configure `ALLOWED_HOSTS` with your domain.
3. Collect static files:
   ```bash
   python manage.py collectstatic
   ```
4. Use a production-ready web server (e.g., Gunicorn, Nginx).

## Testing

Run the test suite to ensure everything is working:

```bash
python manage.py test
```

## License

This project is licensed under the MIT License.
