# Django Social Networking API

This is a social networking API built with Django and Django REST Framework.

## Features

- User signup and login
- Search users by email and name
- Send, accept, and reject friend requests
- List friends
- List pending friend requests

## Requirements

- Python 
- Django 
- Django REST Framework
- Docker (optional, for containerization)

## Installation

### 1. Clone the repository


git clone https://github.com/yourusername/django-social-networking-api.git
cd django-social-networking-api```

```python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver



