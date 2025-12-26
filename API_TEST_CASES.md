# RetailConnect Kenya API - Test Cases

This document provides comprehensive test cases for all API endpoints in the RetailConnect Kenya system.

## Table of Contents

1. [Test Environment Setup](#test-environment-setup)
2. [Health Check Tests](#health-check-tests)
3. [Authentication Tests](#authentication-tests)
4. [User Management Tests](#user-management-tests)
5. [Product Management Tests](#product-management-tests)
6. [Order Management Tests](#order-management-tests)
7. [Payment Tests](#payment-tests)
8. [Delivery Tests](#delivery-tests)
9. [Notification Tests](#notification-tests)
10. [Analytics Tests](#analytics-tests)
11. [End-to-End Test Scenarios](#end-to-end-test-scenarios)

---

## Test Environment Setup

### Prerequisites
- API server running at `http://localhost:8000`
- Database with test data (or empty for fresh testing)
- Postman or similar API testing tool

### Test Users
Create the following test users for comprehensive testing:

| Username | User Type | Password | Purpose |
|----------|-----------|----------|---------|
| `test_retailer` | retailer | `TestPass123!` | Testing retailer flows |
| `test_wholesaler` | wholesaler | `TestPass123!` | Testing wholesaler flows |
| `test_retailer2` | retailer | `TestPass123!` | Testing multi-user scenarios |

---

## Health Check Tests

### TC-HC-001: Server Health Check
| Field | Value |
|-------|-------|
| **Endpoint** | `GET /healthz` |
| **Auth Required** | No |
| **Description** | Verify the API server is running and responsive |

**Request:**
```http
GET /healthz
```

**Expected Response:**
```json
{
    "status": "ok"
}
```

| Test Step | Expected Result | Status |
|-----------|-----------------|--------|
| Send GET request to `/healthz` | Status code: 200 | ⬜ |
| Verify response body | Contains `{"status": "ok"}` | ⬜ |

---

## Authentication Tests

### TC-AUTH-001: User Registration - Retailer
| Field | Value |
|-------|-------|
| **Endpoint** | `POST /api/v1/users/register/` |
| **Auth Required** | No |
| **Description** | Register a new retailer account |

**Request:**
```json
{
    "username": "test_retailer",
    "phone_number": "+254712345678",
    "password": "TestPass123!",
    "password_confirm": "TestPass123!",
    "user_type": "retailer",
    "business_name": "Test Retail Shop",
    "city": "Nairobi"
}
```

**Expected Response (201 Created):**
```json
{
    "id": 1,
    "username": "test_retailer",
    "phone_number": "+254712345678",
    "user_type": "retailer",
    "business_name": "Test Retail Shop",
    "city": "Nairobi"
}
```

| Test Step | Expected Result | Status |
|-----------|-----------------|--------|
| Send valid registration data | Status code: 201 | ⬜ |
| Verify user is created in database | User exists with correct data | ⬜ |
| Verify retailer profile is created | RetailerProfile exists | ⬜ |

---

### TC-AUTH-002: User Registration - Wholesaler
| Field | Value |
|-------|-------|
| **Endpoint** | `POST /api/v1/users/register/` |
| **Auth Required** | No |
| **Description** | Register a new wholesaler account |

**Request:**
```json
{
    "username": "test_wholesaler",
    "phone_number": "+254722345678",
    "password": "TestPass123!",
    "password_confirm": "TestPass123!",
    "user_type": "wholesaler",
    "business_name": "Test Wholesale Company",
    "city": "Mombasa"
}
```

| Test Step | Expected Result | Status |
|-----------|-----------------|--------|
| Send valid registration data | Status code: 201 | ⬜ |
| Verify wholesaler profile is created | WholesalerProfile exists | ⬜ |

---

### TC-AUTH-003: Registration - Password Mismatch
| Field | Value |
|-------|-------|
| **Endpoint** | `POST /api/v1/users/register/` |
| **Auth Required** | No |
| **Description** | Verify password mismatch validation |

**Request:**
```json
{
    "username": "test_user",
    "phone_number": "+254733345678",
    "password": "TestPass123!",
    "password_confirm": "DifferentPass123!",
    "user_type": "retailer",
    "business_name": "Test Shop",
    "city": "Nairobi"
}
```

| Test Step | Expected Result | Status |
|-----------|-----------------|--------|
| Send mismatched passwords | Status code: 400 | ⬜ |
| Verify error message | "Passwords don't match" | ⬜ |

---

### TC-AUTH-004: Registration - Duplicate Username
| Field | Value |
|-------|-------|
| **Endpoint** | `POST /api/v1/users/register/` |
| **Auth Required** | No |
| **Description** | Verify duplicate username rejection |

**Request:**
```json
{
    "username": "test_retailer",
    "phone_number": "+254744345678",
    "password": "TestPass123!",
    "password_confirm": "TestPass123!",
    "user_type": "retailer",
    "business_name": "Another Shop",
    "city": "Nairobi"
}
```

| Test Step | Expected Result | Status |
|-----------|-----------------|--------|
| Send duplicate username | Status code: 400 | ⬜ |
| Verify error message | Username already exists error | ⬜ |

---

### TC-AUTH-005: Login - Valid Credentials
| Field | Value |
|-------|-------|
| **Endpoint** | `POST /api/v1/users/login/` |
| **Auth Required** | No |
| **Description** | Login with valid credentials |

**Request:**
```json
{
    "username": "test_retailer",
    "password": "TestPass123!"
}
```

**Expected Response (200 OK):**
```json
{
    "refresh": "<refresh_token>",
    "access": "<access_token>",
    "user": {
        "id": 1,
        "username": "test_retailer",
        "user_type": "retailer",
        ...
    }
}
```

| Test Step | Expected Result | Status |
|-----------|-----------------|--------|
| Send valid credentials | Status code: 200 | ⬜ |
| Verify access token received | Token is valid JWT | ⬜ |
| Verify refresh token received | Token is valid JWT | ⬜ |
| Verify user data returned | Correct user information | ⬜ |

---

### TC-AUTH-006: Login - Invalid Password
| Field | Value |
|-------|-------|
| **Endpoint** | `POST /api/v1/users/login/` |
| **Auth Required** | No |
| **Description** | Login with wrong password |

**Request:**
```json
{
    "username": "test_retailer",
    "password": "WrongPassword123!"
}
```

| Test Step | Expected Result | Status |
|-----------|-----------------|--------|
| Send wrong password | Status code: 401 | ⬜ |
| Verify error message | "Invalid username or password" | ⬜ |

---

### TC-AUTH-007: Login - Non-existent User
| Field | Value |
|-------|-------|
| **Endpoint** | `POST /api/v1/users/login/` |
| **Auth Required** | No |
| **Description** | Login with non-existent username |

**Request:**
```json
{
    "username": "nonexistent_user",
    "password": "TestPass123!"
}
```

| Test Step | Expected Result | Status |
|-----------|-----------------|--------|
| Send non-existent username | Status code: 401 | ⬜ |
| Verify error message | "User is not registered" | ⬜ |

---

### TC-AUTH-008: Token Refresh
| Field | Value |
|-------|-------|
| **Endpoint** | `POST /api/v1/users/token/refresh/` |
| **Auth Required** | No |
| **Description** | Refresh access token using refresh token |

**Request:**
```json
{
    "refresh": "<valid_refresh_token>"
}
```

**Expected Response (200 OK):**
```json
{
    "access": "<new_access_token>"
}
```

| Test Step | Expected Result | Status |
|-----------|-----------------|--------|
| Send valid refresh token | Status code: 200 | ⬜ |
| Verify new access token received | Valid JWT token | ⬜ |
| Use new token for authenticated request | Request succeeds | ⬜ |

---

### TC-AUTH-009: Token Refresh - Invalid Token
| Field | Value |
|-------|-------|
| **Endpoint** | `POST /api/v1/users/token/refresh/` |
| **Auth Required** | No |
| **Description** | Refresh with invalid token |

**Request:**
```json
{
    "refresh": "invalid_token_here"
}
```

| Test Step | Expected Result | Status |
|-----------|-----------------|--------|
| Send invalid refresh token | Status code: 401 | ⬜ |
| Verify error message | Token is invalid or expired | ⬜ |

---

## User Management Tests

### TC-USER-001: Get Profile - Authenticated
| Field | Value |
|-------|-------|
| **Endpoint** | `GET /api/v1/users/profile/` |
| **Auth Required** | Yes |
| **Description** | Get current user's profile |

**Headers:**
```
Authorization: Bearer <access_token>
```

**Expected Response (200 OK):**
```json
{
    "id": 1,
    "username": "test_retailer",
    "email": null,
    "user_type": "retailer",
    "phone_number": "+254712345678",
    "business_name": "Test Retail Shop",
    "location": null,
    "city": "Nairobi",
    "is_verified": false,
    "profile_image": null,
    "created_at": "2025-12-25T10:00:00Z"
}
```

| Test Step | Expected Result | Status |
|-----------|-----------------|--------|
| Send request with valid token | Status code: 200 | ⬜ |
| Verify correct user data returned | Matches logged in user | ⬜ |

---

### TC-USER-002: Get Profile - Unauthenticated
| Field | Value |
|-------|-------|
| **Endpoint** | `GET /api/v1/users/profile/` |
| **Auth Required** | Yes |
| **Description** | Access profile without authentication |

| Test Step | Expected Result | Status |
|-----------|-----------------|--------|
| Send request without token | Status code: 401 | ⬜ |
| Verify error message | Authentication credentials required | ⬜ |

---

### TC-USER-003: Update Profile
| Field | Value |
|-------|-------|
| **Endpoint** | `PUT /api/v1/users/profile/update/` |
| **Auth Required** | Yes |
| **Description** | Update user profile information |

**Request:**
```json
{
    "username": "updated_retailer",
    "email": "retailer@example.com",
    "phone_number": "+254712345678",
    "business_name": "Updated Retail Shop",
    "location": "Westlands, Nairobi",
    "city": "Nairobi",
    "profile_image": "https://example.com/image.jpg"
}
```

| Test Step | Expected Result | Status |
|-----------|-----------------|--------|
| Send valid update data | Status code: 200 | ⬜ |
| Verify data is updated | All fields updated correctly | ⬜ |
| Verify partial update works | Only sent fields updated | ⬜ |

---

### TC-USER-004: Update Profile - Duplicate Username
| Field | Value |
|-------|-------|
| **Endpoint** | `PUT /api/v1/users/profile/update/` |
| **Auth Required** | Yes |
| **Description** | Update with already taken username |

**Request:**
```json
{
    "username": "test_wholesaler"
}
```

| Test Step | Expected Result | Status |
|-----------|-----------------|--------|
| Send duplicate username | Status code: 400 | ⬜ |
| Verify error message | "This username is already taken" | ⬜ |

---

### TC-USER-005: List Wholesalers
| Field | Value |
|-------|-------|
| **Endpoint** | `GET /api/v1/users/wholesalers/` |
| **Auth Required** | Yes |
| **Description** | Get list of all wholesalers |
| **Query Parameters** | `city` (optional), `verified` (optional) |

| Test Step | Expected Result | Status |
|-----------|-----------------|--------|
| Send authenticated request | Status code: 200 | ⬜ |
| Verify response is array | Array of wholesaler objects | ⬜ |
| Verify only wholesalers returned | No retailers in list | ⬜ |
| Filter by city `?city=Nairobi` | Only Nairobi wholesalers | ⬜ |
| Filter by verified `?verified=true` | Only verified wholesalers | ⬜ |

---

### TC-USER-006: Get Wholesaler Detail
| Field | Value |
|-------|-------|
| **Endpoint** | `GET /api/v1/users/wholesalers/:id/` |
| **Auth Required** | Yes |
| **Description** | Get specific wholesaler details |

| Test Step | Expected Result | Status |
|-----------|-----------------|--------|
| Send request with valid ID | Status code: 200 | ⬜ |
| Verify wholesaler data returned | Complete profile information | ⬜ |
| Send request with invalid ID | Status code: 404 | ⬜ |

---

## Product Management Tests

### TC-PROD-001: List Categories
| Field | Value |
|-------|-------|
| **Endpoint** | `GET /api/v1/products/categories/` |
| **Auth Required** | No |
| **Description** | Get product categories (root categories with nested subcategories by default) |
| **Query Parameters** | `all` (optional) - set to `true` to get all categories flat |

**Expected Response (200 OK):**
```json
[
    {
        "id": 1,
        "name": "Grains & Cereals",
        "slug": "grains-cereals",
        "description": "Rice, wheat, maize...",
        "image": null,
        "parent": null,
        "subcategories": [
            {
                "id": 2,
                "name": "Rice",
                "slug": "rice",
                "description": "All types of rice",
                "image": null,
                "parent": 1,
                "subcategories": []
            }
        ]
    }
]
```

| Test Step | Expected Result | Status |
|-----------|-----------------|--------|
| Send request | Status code: 200 | ⬜ |
| Verify root categories returned | Array with root category objects (parent=null) | ⬜ |
| Verify subcategories nested | Subcategories in parent's subcategories array | ⬜ |
| Send request with `?all=true` | All categories returned flat | ⬜ |

---

### TC-PROD-002: List All Products
| Field | Value |
|-------|-------|
| **Endpoint** | `GET /api/v1/products/` |
| **Auth Required** | No |
| **Description** | Get all available products |

| Test Step | Expected Result | Status |
|-----------|-----------------|--------|
| Send request | Status code: 200 | ⬜ |
| Verify products returned | Array of product objects | ⬜ |
| Verify pagination works | Paginated response | ⬜ |

---

### TC-PROD-003: Filter Products by Category
| Field | Value |
|-------|-------|
| **Endpoint** | `GET /api/v1/products/?category=1` |
| **Auth Required** | No |
| **Description** | Filter products by category |

| Test Step | Expected Result | Status |
|-----------|-----------------|--------|
| Send request with category filter | Status code: 200 | ⬜ |
| Verify only matching products returned | All products have category_id=1 | ⬜ |

---

### TC-PROD-004: Search Products
| Field | Value |
|-------|-------|
| **Endpoint** | `GET /api/v1/products/?search=rice` |
| **Auth Required** | No |
| **Description** | Search products by name |

| Test Step | Expected Result | Status |
|-----------|-----------------|--------|
| Send request with search query | Status code: 200 | ⬜ |
| Verify matching products returned | Products contain "rice" in name | ⬜ |

---

### TC-PROD-005: Filter Products by Price Range
| Field | Value |
|-------|-------|
| **Endpoint** | `GET /api/v1/products/?min_price=100&max_price=500` |
| **Auth Required** | No |
| **Description** | Filter products by price range |

| Test Step | Expected Result | Status |
|-----------|-----------------|--------|
| Send request with price filters | Status code: 200 | ⬜ |
| Verify price range respected | All products within range | ⬜ |

---

### TC-PROD-006: Get Product Detail
| Field | Value |
|-------|-------|
| **Endpoint** | `GET /api/v1/products/:id/` |
| **Auth Required** | No |
| **Description** | Get specific product details |

| Test Step | Expected Result | Status |
|-----------|-----------------|--------|
| Send request with valid ID | Status code: 200 | ⬜ |
| Verify complete product data | All fields present | ⬜ |
| Verify images included | Images array present | ⬜ |
| Send request with invalid ID | Status code: 404 | ⬜ |

---

### TC-PROD-007: Create Product (Wholesaler)
| Field | Value |
|-------|-------|
| **Endpoint** | `POST /api/v1/products/my-products/` |
| **Auth Required** | Yes (Wholesaler) |
| **Description** | Create a new product |

**Request:**
```json
{
    "category": 1,
    "name": "Premium Basmati Rice",
    "slug": "premium-basmati-rice",
    "description": "High quality basmati rice imported from India",
    "sku": "RICE-BSM-001",
    "unit_price": "250.00",
    "bulk_price": "220.00",
    "bulk_quantity": 10,
    "unit_of_measure": "kg",
    "minimum_order_quantity": 5,
    "stock_quantity": 100,
    "low_stock_threshold": 10
}
```

| Test Step | Expected Result | Status |
|-----------|-----------------|--------|
| Send as wholesaler | Status code: 201 | ⬜ |
| Verify product created | Product exists in database | ⬜ |
| Verify wholesaler assigned | Product.wholesaler = current user | ⬜ |
| Send as retailer | Status code: 403 | ⬜ |

---

### TC-PROD-008: Create Product - Missing Required Fields
| Field | Value |
|-------|-------|
| **Endpoint** | `POST /api/v1/products/my-products/` |
| **Auth Required** | Yes (Wholesaler) |
| **Description** | Create product with missing fields |

**Request:**
```json
{
    "name": "Test Product"
}
```

| Test Step | Expected Result | Status |
|-----------|-----------------|--------|
| Send incomplete data | Status code: 400 | ⬜ |
| Verify validation errors | Lists missing required fields | ⬜ |

---

### TC-PROD-009: List My Products (Wholesaler)
| Field | Value |
|-------|-------|
| **Endpoint** | `GET /api/v1/products/my-products/` |
| **Auth Required** | Yes (Wholesaler) |
| **Description** | Get wholesaler's own products |

| Test Step | Expected Result | Status |
|-----------|-----------------|--------|
| Send as wholesaler | Status code: 200 | ⬜ |
| Verify only own products | All products belong to user | ⬜ |

---

### TC-PROD-010: Update Product (Wholesaler)
| Field | Value |
|-------|-------|
| **Endpoint** | `PUT /api/v1/products/my-products/:id/` |
| **Auth Required** | Yes (Wholesaler) |
| **Description** | Update existing product |

**Request:**
```json
{
    "category": 1,
    "name": "Premium Basmati Rice - Updated",
    "slug": "premium-basmati-rice",
    "description": "Updated description",
    "sku": "RICE-BSM-001",
    "unit_price": "260.00",
    "bulk_price": "230.00",
    "bulk_quantity": 10,
    "unit_of_measure": "kg",
    "minimum_order_quantity": 5,
    "stock_quantity": 150,
    "low_stock_threshold": 15
}
```

| Test Step | Expected Result | Status |
|-----------|-----------------|--------|
| Update own product | Status code: 200 | ⬜ |
| Verify changes saved | Data updated correctly | ⬜ |
| Update other's product | Status code: 404 or 403 | ⬜ |

---

### TC-PROD-011: Partial Update Product (Wholesaler)
| Field | Value |
|-------|-------|
| **Endpoint** | `PATCH /api/v1/products/my-products/:id/` |
| **Auth Required** | Yes (Wholesaler) |
| **Description** | Partially update product |

**Request:**
```json
{
    "unit_price": "270.00",
    "stock_quantity": 200
}
```

| Test Step | Expected Result | Status |
|-----------|-----------------|--------|
| Send partial update | Status code: 200 | ⬜ |
| Verify only sent fields changed | Other fields unchanged | ⬜ |

---

### TC-PROD-012: Delete Product (Wholesaler)
| Field | Value |
|-------|-------|
| **Endpoint** | `DELETE /api/v1/products/my-products/:id/` |
| **Auth Required** | Yes (Wholesaler) |
| **Description** | Delete a product |

| Test Step | Expected Result | Status |
|-----------|-----------------|--------|
| Delete own product | Status code: 204 | ⬜ |
| Verify product removed | Product not found | ⬜ |
| Delete other's product | Status code: 404 or 403 | ⬜ |

---

### TC-PROD-013: Upload Product Image
| Field | Value |
|-------|-------|
| **Endpoint** | `POST /api/v1/products/my-products/:product_id/images/` |
| **Auth Required** | Yes (Wholesaler) |
| **Description** | Upload image for product |

**Request (multipart/form-data):**
```
image: <file>
is_primary: true
```

| Test Step | Expected Result | Status |
|-----------|-----------------|--------|
| Upload valid image | Status code: 201 | ⬜ |
| Verify image saved | Image URL returned | ⬜ |
| Verify primary flag set | is_primary = true | ⬜ |
| Upload to other's product | Status code: 403 | ⬜ |

---

## Order Management Tests

### TC-CART-001: Get Empty Cart
| Field | Value |
|-------|-------|
| **Endpoint** | `GET /api/v1/orders/cart/` |
| **Auth Required** | Yes |
| **Description** | Get cart when empty |

| Test Step | Expected Result | Status |
|-----------|-----------------|--------|
| Get cart for new user | Status code: 200 | ⬜ |
| Verify empty items array | items: [] | ⬜ |
| Verify total is 0 | total: "0.00" | ⬜ |

---

### TC-CART-002: Add Item to Cart
| Field | Value |
|-------|-------|
| **Endpoint** | `POST /api/v1/orders/cart/items/` |
| **Auth Required** | Yes (Retailer) |
| **Description** | Add product to cart |

**Request:**
```json
{
    "product_id": 1,
    "quantity": 5
}
```

| Test Step | Expected Result | Status |
|-----------|-----------------|--------|
| Add valid product | Status code: 201 | ⬜ |
| Verify item in cart | Cart contains product | ⬜ |
| Verify quantity correct | quantity = 5 | ⬜ |
| Verify total calculated | Correct total price | ⬜ |

---

### TC-CART-003: Add Item - Below Minimum Order Quantity
| Field | Value |
|-------|-------|
| **Endpoint** | `POST /api/v1/orders/cart/items/` |
| **Auth Required** | Yes (Retailer) |
| **Description** | Add product with quantity below minimum |

**Request:**
```json
{
    "product_id": 1,
    "quantity": 1
}
```

| Test Step | Expected Result | Status |
|-----------|-----------------|--------|
| Add with low quantity | Status code: 400 | ⬜ |
| Verify error message | Below minimum order quantity | ⬜ |

---

### TC-CART-004: Add Item - Invalid Product
| Field | Value |
|-------|-------|
| **Endpoint** | `POST /api/v1/orders/cart/items/` |
| **Auth Required** | Yes (Retailer) |
| **Description** | Add non-existent product |

**Request:**
```json
{
    "product_id": 99999,
    "quantity": 5
}
```

| Test Step | Expected Result | Status |
|-----------|-----------------|--------|
| Add invalid product | Status code: 400 or 404 | ⬜ |
| Verify error message | Product not found | ⬜ |

---

### TC-CART-005: Update Cart Item Quantity
| Field | Value |
|-------|-------|
| **Endpoint** | `PUT /api/v1/orders/cart/items/:id/` |
| **Auth Required** | Yes |
| **Description** | Update quantity of cart item |

**Request:**
```json
{
    "quantity": 10
}
```

| Test Step | Expected Result | Status |
|-----------|-----------------|--------|
| Update to valid quantity | Status code: 200 | ⬜ |
| Verify quantity changed | quantity = 10 | ⬜ |
| Verify total recalculated | New total price | ⬜ |

---

### TC-CART-006: Remove Cart Item
| Field | Value |
|-------|-------|
| **Endpoint** | `DELETE /api/v1/orders/cart/items/:id/` |
| **Auth Required** | Yes |
| **Description** | Remove item from cart |

| Test Step | Expected Result | Status |
|-----------|-----------------|--------|
| Delete cart item | Status code: 204 | ⬜ |
| Verify item removed | Item not in cart | ⬜ |
| Delete invalid item | Status code: 404 | ⬜ |

---

### TC-CART-007: Clear Cart
| Field | Value |
|-------|-------|
| **Endpoint** | `DELETE /api/v1/orders/cart/clear/` |
| **Auth Required** | Yes |
| **Description** | Remove all items from cart |

| Test Step | Expected Result | Status |
|-----------|-----------------|--------|
| Clear cart with items | Status code: 204 | ⬜ |
| Verify cart is empty | items: [] | ⬜ |

---

### TC-ORDER-001: Checkout - Success
| Field | Value |
|-------|-------|
| **Endpoint** | `POST /api/v1/orders/checkout/` |
| **Auth Required** | Yes (Retailer) |
| **Description** | Create order from cart |

**Prerequisites:**
- Cart has items from at least one wholesaler

**Request:**
```json
{
    "delivery_address": "123 Kimathi Street, CBD",
    "delivery_city": "Nairobi",
    "delivery_notes": "Please call before delivery"
}
```

| Test Step | Expected Result | Status |
|-----------|-----------------|--------|
| Checkout with valid cart | Status code: 201 | ⬜ |
| Verify order created | Order exists with items | ⬜ |
| Verify cart cleared | Cart is empty | ⬜ |
| Verify order number generated | Unique order number | ⬜ |
| Verify totals calculated | Subtotal, delivery_fee, total | ⬜ |

---

### TC-ORDER-002: Checkout - Empty Cart
| Field | Value |
|-------|-------|
| **Endpoint** | `POST /api/v1/orders/checkout/` |
| **Auth Required** | Yes (Retailer) |
| **Description** | Checkout with empty cart |

| Test Step | Expected Result | Status |
|-----------|-----------------|--------|
| Checkout empty cart | Status code: 400 | ⬜ |
| Verify error message | Cart is empty | ⬜ |

---

### TC-ORDER-003: List Retailer Orders
| Field | Value |
|-------|-------|
| **Endpoint** | `GET /api/v1/orders/my-orders/` |
| **Auth Required** | Yes (Retailer) |
| **Description** | Get orders placed by retailer |

| Test Step | Expected Result | Status |
|-----------|-----------------|--------|
| Get orders as retailer | Status code: 200 | ⬜ |
| Verify only own orders | All orders belong to user | ⬜ |
| Verify order details | Complete order information | ⬜ |

---

### TC-ORDER-004: List Wholesaler Orders
| Field | Value |
|-------|-------|
| **Endpoint** | `GET /api/v1/orders/received-orders/` |
| **Auth Required** | Yes (Wholesaler) |
| **Description** | Get orders received by wholesaler |

| Test Step | Expected Result | Status |
|-----------|-----------------|--------|
| Get orders as wholesaler | Status code: 200 | ⬜ |
| Verify orders for wholesaler | All orders contain wholesaler's products | ⬜ |

---

### TC-ORDER-005: Get Order Detail
| Field | Value |
|-------|-------|
| **Endpoint** | `GET /api/v1/orders/:id/` |
| **Auth Required** | Yes |
| **Description** | Get specific order details |

| Test Step | Expected Result | Status |
|-----------|-----------------|--------|
| Get own order | Status code: 200 | ⬜ |
| Verify order items | Items array populated | ⬜ |
| Get other's order | Status code: 404 or 403 | ⬜ |

---

### TC-ORDER-006: Update Order Status (Wholesaler)
| Field | Value |
|-------|-------|
| **Endpoint** | `PATCH /api/v1/orders/:id/status/` |
| **Auth Required** | Yes (Wholesaler) |
| **Description** | Update order status |

**Request:**
```json
{
    "status": "confirmed"
}
```

**Valid Status Values:**
- `pending` → `confirmed` → `processing` → `shipped` → `delivered`
- `cancelled` (from any status)

| Test Step | Expected Result | Status |
|-----------|-----------------|--------|
| Update to valid status | Status code: 200 | ⬜ |
| Verify status changed | Order.status updated | ⬜ |
| Update as retailer | Status code: 403 | ⬜ |
| Invalid status transition | Status code: 400 | ⬜ |

---

## Payment Tests

### TC-PAY-001: Initiate M-Pesa Payment
| Field | Value |
|-------|-------|
| **Endpoint** | `POST /api/v1/payments/mpesa/initiate/` |
| **Auth Required** | Yes |
| **Description** | Initiate STK Push payment |

**Request:**
```json
{
    "order_id": 1,
    "phone_number": "254712345678"
}
```

| Test Step | Expected Result | Status |
|-----------|-----------------|--------|
| Initiate with valid data | Status code: 200 | ⬜ |
| Verify STK push sent | Success response from M-Pesa | ⬜ |
| Verify payment record created | Payment exists with pending status | ⬜ |

---

### TC-PAY-002: Initiate Payment - Invalid Phone
| Field | Value |
|-------|-------|
| **Endpoint** | `POST /api/v1/payments/mpesa/initiate/` |
| **Auth Required** | Yes |
| **Description** | Initiate with invalid phone number |

**Request:**
```json
{
    "order_id": 1,
    "phone_number": "123456"
}
```

| Test Step | Expected Result | Status |
|-----------|-----------------|--------|
| Initiate with invalid phone | Status code: 400 | ⬜ |
| Verify error message | Invalid phone number format | ⬜ |

---

### TC-PAY-003: Initiate Payment - Invalid Order
| Field | Value |
|-------|-------|
| **Endpoint** | `POST /api/v1/payments/mpesa/initiate/` |
| **Auth Required** | Yes |
| **Description** | Initiate payment for non-existent order |

**Request:**
```json
{
    "order_id": 99999,
    "phone_number": "254712345678"
}
```

| Test Step | Expected Result | Status |
|-----------|-----------------|--------|
| Initiate for invalid order | Status code: 404 | ⬜ |
| Verify error message | Order not found | ⬜ |

---

### TC-PAY-004: M-Pesa Callback - Success
| Field | Value |
|-------|-------|
| **Endpoint** | `POST /api/v1/payments/mpesa/callback/` |
| **Auth Required** | No |
| **Description** | Handle successful M-Pesa callback |

**Request:**
```json
{
    "Body": {
        "stkCallback": {
            "MerchantRequestID": "xxxxx",
            "CheckoutRequestID": "xxxxx",
            "ResultCode": 0,
            "ResultDesc": "The service request is processed successfully.",
            "CallbackMetadata": {
                "Item": [
                    {"Name": "Amount", "Value": 1000},
                    {"Name": "MpesaReceiptNumber", "Value": "XXX123XXX"},
                    {"Name": "TransactionDate", "Value": 20251225120000},
                    {"Name": "PhoneNumber", "Value": 254712345678}
                ]
            }
        }
    }
}
```

| Test Step | Expected Result | Status |
|-----------|-----------------|--------|
| Send success callback | Status code: 200 | ⬜ |
| Verify payment updated | Status = completed | ⬜ |
| Verify receipt number saved | mpesa_receipt_number set | ⬜ |
| Verify order marked paid | Order.is_paid = true | ⬜ |

---

### TC-PAY-005: M-Pesa Callback - Failed
| Field | Value |
|-------|-------|
| **Endpoint** | `POST /api/v1/payments/mpesa/callback/` |
| **Auth Required** | No |
| **Description** | Handle failed M-Pesa callback |

**Request:**
```json
{
    "Body": {
        "stkCallback": {
            "MerchantRequestID": "xxxxx",
            "CheckoutRequestID": "xxxxx",
            "ResultCode": 1032,
            "ResultDesc": "Request cancelled by user"
        }
    }
}
```

| Test Step | Expected Result | Status |
|-----------|-----------------|--------|
| Send failed callback | Status code: 200 | ⬜ |
| Verify payment updated | Status = failed | ⬜ |
| Verify order not paid | Order.is_paid = false | ⬜ |

---

### TC-PAY-006: List Payments
| Field | Value |
|-------|-------|
| **Endpoint** | `GET /api/v1/payments/` |
| **Auth Required** | Yes |
| **Description** | Get user's payments |

| Test Step | Expected Result | Status |
|-----------|-----------------|--------|
| Get payments | Status code: 200 | ⬜ |
| Verify only own payments | Payments for user's orders | ⬜ |

---

### TC-PAY-007: Get Payment Detail
| Field | Value |
|-------|-------|
| **Endpoint** | `GET /api/v1/payments/:id/` |
| **Auth Required** | Yes |
| **Description** | Get specific payment details |

| Test Step | Expected Result | Status |
|-----------|-----------------|--------|
| Get own payment | Status code: 200 | ⬜ |
| Verify complete data | All payment fields | ⬜ |
| Get other's payment | Status code: 404 or 403 | ⬜ |

---

## Delivery Tests

### TC-DEL-001: Create Delivery
| Field | Value |
|-------|-------|
| **Endpoint** | `POST /api/v1/delivery/` |
| **Auth Required** | Yes |
| **Description** | Create delivery record for order |

**Request:**
```json
{
    "order": 1,
    "driver_name": "John Doe",
    "driver_phone": "+254712345678",
    "vehicle_number": "KAA 123A",
    "status": "pending",
    "estimated_delivery_time": "2025-12-26T10:00:00Z",
    "notes": "Handle with care"
}
```

| Test Step | Expected Result | Status |
|-----------|-----------------|--------|
| Create with valid data | Status code: 201 | ⬜ |
| Verify delivery created | Delivery record exists | ⬜ |
| Verify order linked | Order association correct | ⬜ |

---

### TC-DEL-002: List Deliveries
| Field | Value |
|-------|-------|
| **Endpoint** | `GET /api/v1/delivery/` |
| **Auth Required** | Yes |
| **Description** | Get all deliveries |

| Test Step | Expected Result | Status |
|-----------|-----------------|--------|
| Get deliveries | Status code: 200 | ⬜ |
| Verify delivery list | Array of deliveries | ⬜ |

---

### TC-DEL-003: Get Delivery Detail
| Field | Value |
|-------|-------|
| **Endpoint** | `GET /api/v1/delivery/:id/` |
| **Auth Required** | Yes |
| **Description** | Get specific delivery details |

| Test Step | Expected Result | Status |
|-----------|-----------------|--------|
| Get delivery by ID | Status code: 200 | ⬜ |
| Verify all fields | Complete delivery data | ⬜ |
| Get invalid ID | Status code: 404 | ⬜ |

---

### TC-DEL-004: Update Delivery
| Field | Value |
|-------|-------|
| **Endpoint** | `PUT /api/v1/delivery/:id/` |
| **Auth Required** | Yes |
| **Description** | Full update of delivery |

**Request:**
```json
{
    "order": 1,
    "driver_name": "Jane Doe",
    "driver_phone": "+254722345678",
    "vehicle_number": "KAB 456B",
    "status": "in_transit",
    "estimated_delivery_time": "2025-12-26T11:00:00Z",
    "notes": "Updated notes"
}
```

| Test Step | Expected Result | Status |
|-----------|-----------------|--------|
| Full update | Status code: 200 | ⬜ |
| Verify all fields updated | Data matches request | ⬜ |

---

### TC-DEL-005: Partial Update Delivery
| Field | Value |
|-------|-------|
| **Endpoint** | `PATCH /api/v1/delivery/:id/` |
| **Auth Required** | Yes |
| **Description** | Partial update of delivery |

**Request:**
```json
{
    "status": "delivered",
    "actual_delivery_time": "2025-12-26T09:30:00Z"
}
```

| Test Step | Expected Result | Status |
|-----------|-----------------|--------|
| Partial update | Status code: 200 | ⬜ |
| Verify only sent fields changed | Other fields unchanged | ⬜ |

---

### TC-DEL-006: Delete Delivery
| Field | Value |
|-------|-------|
| **Endpoint** | `DELETE /api/v1/delivery/:id/` |
| **Auth Required** | Yes |
| **Description** | Delete delivery record |

| Test Step | Expected Result | Status |
|-----------|-----------------|--------|
| Delete delivery | Status code: 204 | ⬜ |
| Verify record removed | Delivery not found | ⬜ |

---

## Notification Tests

### TC-NOTIF-001: List Notifications
| Field | Value |
|-------|-------|
| **Endpoint** | `GET /api/v1/notifications/` |
| **Auth Required** | Yes |
| **Description** | Get user's notifications |

| Test Step | Expected Result | Status |
|-----------|-----------------|--------|
| Get notifications | Status code: 200 | ⬜ |
| Verify only own notifications | Notifications for current user | ⬜ |

---

### TC-NOTIF-002: Get Notification Detail
| Field | Value |
|-------|-------|
| **Endpoint** | `GET /api/v1/notifications/:id/` |
| **Auth Required** | Yes |
| **Description** | Get specific notification |

| Test Step | Expected Result | Status |
|-----------|-----------------|--------|
| Get notification by ID | Status code: 200 | ⬜ |
| Verify notification data | Complete notification info | ⬜ |
| Get other's notification | Status code: 404 or 403 | ⬜ |

---

## Analytics Tests

### TC-ANAL-001: Get Analytics Overview
| Field | Value |
|-------|-------|
| **Endpoint** | `GET /api/v1/analytics/overview/` |
| **Auth Required** | Yes |
| **Description** | Get analytics dashboard data |

| Test Step | Expected Result | Status |
|-----------|-----------------|--------|
| Get overview | Status code: 200 | ⬜ |
| Verify analytics data | Sales, orders statistics | ⬜ |

---

## End-to-End Test Scenarios

### E2E-001: Complete Purchase Flow (Retailer)

**Scenario:** A retailer discovers products, adds to cart, and completes purchase.

| Step | Action | Expected Result | Status |
|------|--------|-----------------|--------|
| 1 | Register as retailer | Account created | ⬜ |
| 2 | Login | Tokens received | ⬜ |
| 3 | Browse products | Product list returned | ⬜ |
| 4 | View product detail | Product details shown | ⬜ |
| 5 | Add to cart | Item added to cart | ⬜ |
| 6 | View cart | Cart with items shown | ⬜ |
| 7 | Checkout | Order created | ⬜ |
| 8 | Initiate payment | STK push sent | ⬜ |
| 9 | Complete payment | Payment confirmed | ⬜ |
| 10 | View order | Order with paid status | ⬜ |

---

### E2E-002: Complete Order Fulfillment Flow (Wholesaler)

**Scenario:** A wholesaler manages products and fulfills orders.

| Step | Action | Expected Result | Status |
|------|--------|-----------------|--------|
| 1 | Register as wholesaler | Account created | ⬜ |
| 2 | Login | Tokens received | ⬜ |
| 3 | Create product | Product created | ⬜ |
| 4 | Upload product image | Image uploaded | ⬜ |
| 5 | View received orders | Order list shown | ⬜ |
| 6 | Update order to confirmed | Status updated | ⬜ |
| 7 | Update order to processing | Status updated | ⬜ |
| 8 | Create delivery record | Delivery created | ⬜ |
| 9 | Update order to shipped | Status updated | ⬜ |
| 10 | Update delivery to delivered | Delivery completed | ⬜ |
| 11 | Update order to delivered | Order completed | ⬜ |

---

### E2E-003: Multi-Wholesaler Cart Flow

**Scenario:** Retailer orders from multiple wholesalers in single checkout.

| Step | Action | Expected Result | Status |
|------|--------|-----------------|--------|
| 1 | Login as retailer | Tokens received | ⬜ |
| 2 | Add product from Wholesaler A | Item in cart | ⬜ |
| 3 | Add product from Wholesaler B | Both items in cart | ⬜ |
| 4 | Checkout | Multiple orders created | ⬜ |
| 5 | Verify separate orders | One per wholesaler | ⬜ |
| 6 | Each wholesaler sees own order | Filtered correctly | ⬜ |

---

## Test Execution Checklist

### Pre-requisites
- [ ] API server running
- [ ] Database migrations applied
- [ ] Test categories created
- [ ] M-Pesa sandbox configured (for payment tests)

### Test Summary

| Module | Total Tests | Passed | Failed | Blocked |
|--------|-------------|--------|--------|---------|
| Health Check | 1 | ⬜ | ⬜ | ⬜ |
| Authentication | 9 | ⬜ | ⬜ | ⬜ |
| Users | 6 | ⬜ | ⬜ | ⬜ |
| Products | 13 | ⬜ | ⬜ | ⬜ |
| Orders (Cart) | 7 | ⬜ | ⬜ | ⬜ |
| Orders | 6 | ⬜ | ⬜ | ⬜ |
| Payments | 7 | ⬜ | ⬜ | ⬜ |
| Delivery | 6 | ⬜ | ⬜ | ⬜ |
| Notifications | 2 | ⬜ | ⬜ | ⬜ |
| Analytics | 1 | ⬜ | ⬜ | ⬜ |
| E2E Scenarios | 3 | ⬜ | ⬜ | ⬜ |
| **TOTAL** | **61** | ⬜ | ⬜ | ⬜ |

---

## Notes

- All authenticated endpoints require `Authorization: Bearer <access_token>` header
- Replace `:id` in URLs with actual resource IDs
- Phone numbers must be in format `254XXXXXXXXX` for M-Pesa
- Timestamps should be in ISO 8601 format
- Test with both valid and invalid data to ensure proper error handling
