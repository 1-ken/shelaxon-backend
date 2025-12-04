# Django Tutorial Using RetailConnect (for React/Next.js devs)

This hands-on tutorial teaches Django fundamentals by exploring and extending the RetailConnect API. It assumes you know JavaScript, React, and Next.js, but are new to Django.

## 1) Big Picture: Django vs Next.js
- **Django**: Python web framework focused on server-side (models, ORM, routing, views, templates, admin).
- **DRF (Django REST Framework)**: Adds API tooling (serializers, viewsets, auth, browsing API).
- **This project**: A REST backend; you’ll consume it from a React/Next.js frontend.

Key parallels:
- Next.js routes → Django `urls.py`
- Next.js middleware → Django `middleware`
- Next.js API handlers → DRF Views/ViewSets
- Prisma/ORM → Django ORM

## 2) Project Structure
```
manage.py                 # Django CLI entry
retailconnect/            # Project (settings, urls, wsgi/asgi)
apps/                     # Feature apps (users, products, orders, payments, ...)
  users/                  # Example app with auth endpoints
  products/               # Products listing & management
utils/mpesa.py            # Integration helper
```

- `retailconnect/settings/*`: Modular settings (`base`, `dev`, `prod`, `test`).
- `retailconnect/urls.py`: Central router (we use `api/v1/*`).
- `apps/<name>/`: Each app has `models.py`, `serializers.py`, `views.py`, `urls.py`.

## 3) Running Locally
```powershell
# Activate venv
C:/Users/kenni/Desktop/retailconnect_kenya/rr/retailconnect_kenya/.venv/Scripts/Activate.ps1

# Install deps
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit DB credentials in .env if needed

# Migrate DB
python manage.py migrate

# Start server
python manage.py runserver
# Visit http://127.0.0.1:8000/api/docs
```

## 4) Django Core Concepts (fast track)
- **Model** (`apps/products/models.py`): Python class → database table via ORM.
- **Serializer** (`apps/products/serializers.py`): Maps model ↔ JSON; handles validation.
- **View** (`apps/products/views.py`): Request handler; in DRF, commonly a `ViewSet`.
- **URL Router** (`apps/products/urls.py`): Binds URLs to views.
- **Settings** (`retailconnect/settings/base.py`): Global config: apps, DB, REST, auth.

Think: Model → Serializer → View → URL.

## 5) Your First Endpoint (Add a simple Ping)
Add a health endpoint (already present) and a custom ping in products.

1) In `apps/products/views.py`:
```python
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

@api_view(["GET"]) 
@permission_classes([AllowAny])
def ping(_request):
    return Response({"message": "pong"})
```

2) In `apps/products/urls.py`:
```python
from .views import ping
urlpatterns = [
    # ...existing routes...
    path('ping/', ping, name='products-ping'),
]
```

3) Try: `GET /api/v1/products/ping/` → `{ "message": "pong" }`

## 6) CRUD with Django ORM
Goal: list products.

- Model (simplified):
```python
# apps/products/models.py
from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)

class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
```

- Serializer:
```python
# apps/products/serializers.py
from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "price", "category"]
```

- ViewSet:
```python
# apps/products/views.py
from rest_framework import viewsets, permissions
from .models import Product
from .serializers import ProductSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
```

- URLs (already wired):
```python
# apps/products/urls.py
from django.urls import path
from .views import ProductViewSet
urlpatterns = [
  path('', ProductViewSet.as_view({'get': 'list', 'post': 'create'})),
]
```

Try requests with `Authorization: Bearer <token>`.

## 7) Authentication (JWT)
- Use `POST /api/users/login/` with username+password → receive `{ access, refresh }`.
- Send `Authorization: Bearer <access>` to call protected endpoints.
- Refresh via `POST /api/users/token/refresh/`.

Where it’s configured:
- `retailconnect/settings/base.py` → `REST_FRAMEWORK` and `SIMPLE_JWT`.
- `retailconnect/urls.py` → `api/v1/users/*` routes.

## 8) Connecting Next.js Frontend
Quick example using `fetch` in Next.js server actions or client components.

- Login:
```ts
const login = async (username: string, password: string) => {
  const res = await fetch('http://127.0.0.1:8000/api/v1/users/login/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });
  return res.json(); // { access, refresh }
};
```

- List products:
```ts
const listProducts = async (token: string) => {
  const res = await fetch('http://127.0.0.1:8000/api/v1/products/', {
    headers: { Authorization: `Bearer ${token}` },
  });
  return res.json();
};
```

- Upload product image:
```ts
const uploadImage = async (token: string, productId: number, file: File) => {
  const form = new FormData();
  form.append('image', file);
  const res = await fetch(`http://127.0.0.1:8000/api/v1/products/my-products/${productId}/images/`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}` },
    body: form,
  });
  return res.json();
};
```

## 9) Admin Panel (Superpower)
Create a superuser and explore:
```powershell
python manage.py createsuperuser
# Visit http://127.0.0.1:8000/admin/
```
Register models in `apps/<app>/admin.py` to manage them via admin.

## 10) Testing & Environments
- Use `retailconnect/settings/test.py` to speed up tests.
- Write API tests with `pytest` or `unittest`.
- Switch environments by setting `DJANGO_SETTINGS_MODULE`.

## 11) Deployment Basics
- Prefer Docker; run migrations on deploy.
- Serve with Gunicorn/Uvicorn workers.
- Configure environment variables and DB/Redis credentials.

## 12) What to Try Next
- Add new app `apps/reviews` with CRUD endpoints.
- Implement pagination and search on product list.
- Add role-based permissions (retailer vs wholesaler).
- Build a Next.js UI that logs in, lists products, and places orders.

## Cheat Sheet (Django commands)
```powershell
# Create app
python manage.py startapp apps.reviews

# Make migrations
python manage.py makemigrations
python manage.py migrate

# Run server
python manage.py runserver
```

You now have the mental model to build Django APIs and connect them to your React/Next.js apps. Keep views thin, move logic to services, and lean on DRF serializers + viewsets for speed and consistency.
