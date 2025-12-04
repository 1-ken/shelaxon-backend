# Authentication & Database Guide for RetailConnect Kenya

This guide explains how login works and how data is stored in this app using simple English.

---

## 🔐 Part 1: How Login Works (Authentication)

### What is JWT?

JWT means "JSON Web Token". Think of it like a **special ticket** you get after you login.

- When you **login with your phone number and password**, the server checks if they are correct
- If correct, you get **2 tickets**:
  - **Access Token** - This ticket lasts for 1 hour. You show this ticket every time you want to do something
  - **Refresh Token** - This ticket lasts for 7 days. When your access token expires, you use this to get a new access token without logging in again

### How to Login (Step by Step)

**Step 1: Register a New User**

Send this to the server:
```
POST /api/v1/users/register/
{
  "username": "myshop",
  "password": "mypassword123",
  "phone_number": "+254712345678",
  "business_name": "My Corner Shop",
  "location": "Nairobi CBD",
  "city": "Nairobi",
  "user_type": "retailer"  // Can be "retailer" or "wholesaler"
}
```

**Step 2: Login**

Send this to get your tokens:
```
POST /api/v1/users/login/
{
  "username": "myshop",
  "password": "mypassword123"
}
```

You get back:
```
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",  // Your 1-hour ticket
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."  // Your 7-day ticket
}
```

**Step 3: Use Access Token**

Every time you want to get products, place orders, etc., include your access token like this:
```
GET /api/v1/products/

Headers:
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

**Step 4: Refresh When Access Token Expires**

After 1 hour, your access token stops working. Get a new one:
```
POST /api/v1/users/token/refresh/
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."  // Your 7-day ticket
}
```

You get a new access token:
```
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."  // Fresh 1-hour ticket
}
```

### User Types in the System

There are 3 types of users:

1. **Retailer** - Small shop owners who BUY products
2. **Wholesaler** - Big suppliers who SELL products in bulk
3. **Admin** - System managers

---

## 💾 Part 2: Database Structure (How Data is Stored)

### 📋 Overview of All Tables

Think of the database like a filing cabinet with different drawers (tables). Each drawer stores related information.

Here are all the drawers we have:

1. **users** - Stores all user accounts
2. **retailer_profiles** - Extra info about retailers
3. **wholesaler_profiles** - Extra info about wholesalers
4. **categories** - Product categories (e.g., "Food", "Drinks")
5. **products** - All products for sale
6. **product_images** - Pictures of products
7. **carts** - Shopping carts for each retailer
8. **cart_items** - Products inside each cart
9. **orders** - Orders placed by retailers
10. **order_items** - Products inside each order
11. **payments** - Payment transactions (M-Pesa, etc.)
12. **deliveries** - Delivery tracking information

---

### 1️⃣ Users Table

This is the main table for all people using the system.

**What's Stored:**

| Field Name | What It Means | Example |
|-----------|--------------|---------|
| id | Unique number for each user | 1 |
| username | Login name | "myshop" |
| password | Secret password (encrypted) | "••••••••" |
| phone_number | Phone number | "+254712345678" |
| business_name | Name of their shop/business | "My Corner Shop" |
| user_type | Type of user | "retailer" or "wholesaler" |
| location | Address | "Nairobi CBD" |
| city | City | "Nairobi" |
| is_verified | Is account verified? | True/False |
| profile_image | Photo | "profiles/myshop.jpg" |
| created_at | When account was created | "2025-11-30 10:30:00" |

**Key Points:**
- Every user MUST have a unique phone number
- Password is encrypted (scrambled) for security
- New users are "retailer" by default
- Users are NOT verified by default (is_verified = False)

---

### 2️⃣ Retailer Profiles Table

Extra information about retailers (shop owners).

**What's Stored:**

| Field Name | What It Means | Example |
|-----------|--------------|---------|
| user | Link to the user account | User #1 |
| business_type | Type of shop | "kiosk", "shop", "supermarket" |
| credit_limit | How much they can buy on credit | 50000.00 |
| preferred_wholesalers | List of favorite wholesalers | [User #5, User #8] |

**Key Points:**
- ONE retailer profile per user
- Default business type is "shop"
- Credit limit starts at 0
- Can mark multiple wholesalers as favorites

---

### 3️⃣ Wholesaler Profiles Table

Extra information about wholesalers (suppliers).

**What's Stored:**

| Field Name | What It Means | Example |
|-----------|--------------|---------|
| user | Link to the user account | User #5 |
| subscription_plan | Plan they're on | "free", "basic", "premium" |
| subscription_expiry | When plan expires | "2025-12-31" |
| categories | What they sell | ["Food", "Drinks"] |
| minimum_order_amount | Minimum order value | 5000.00 |
| delivery_available | Do they deliver? | True/False |
| rating | Average rating | 4.5 |
| total_reviews | Number of reviews | 120 |

**Key Points:**
- ONE wholesaler profile per user
- Default plan is "free"
- Can sell products in multiple categories
- Rating is out of 5 (5.00 is max)

---

### 4️⃣ Categories Table

Product categories (like "Food", "Electronics", etc.)

**What's Stored:**

| Field Name | What It Means | Example |
|-----------|--------------|---------|
| name | Category name | "Food & Beverages" |
| slug | URL-friendly name | "food-beverages" |
| description | What's in this category | "All food items" |
| image | Category picture | "categories/food.jpg" |
| parent | Parent category (if subcategory) | Category #1 |
| is_active | Is category visible? | True/False |

**Key Points:**
- Categories can have subcategories (e.g., "Food" → "Snacks" → "Crisps")
- Slug must be unique
- If parent is empty, it's a main category

**Example Structure:**
```
Food & Beverages (parent = None)
  ├── Snacks (parent = Food & Beverages)
  │     ├── Crisps (parent = Snacks)
  │     └── Biscuits (parent = Snacks)
  └── Drinks (parent = Food & Beverages)
```

---

### 5️⃣ Products Table

All products sold by wholesalers.

**What's Stored:**

| Field Name | What It Means | Example |
|-----------|--------------|---------|
| wholesaler | Who is selling this | User #5 |
| category | What category | Category #3 |
| name | Product name | "Coca Cola 500ml" |
| slug | URL-friendly name | "coca-cola-500ml" |
| sku | Unique product code | "CC-500ML-001" |
| unit_price | Price for 1 item | 50.00 |
| bulk_price | Price when buying many | 45.00 |
| bulk_quantity | How many for bulk price | 24 (1 crate) |
| unit_of_measure | How it's measured | "piece", "kg", "carton" |
| stock_quantity | How many available | 500 |
| stock_status | Stock level | "in_stock", "low_stock", "out_of_stock" |
| minimum_order_quantity | Minimum you can buy | 6 |
| is_active | Is product visible? | True/False |

**Key Points:**
- Stock status updates automatically:
  - stock = 0 → "out_of_stock"
  - stock ≤ low_stock_threshold → "low_stock"
  - stock > low_stock_threshold → "in_stock"
- Bulk price applies when quantity ≥ bulk_quantity
- Example: Buy 24+ bottles at 45.00 each instead of 50.00

---

### 6️⃣ Product Images Table

Pictures for each product (a product can have many pictures).

**What's Stored:**

| Field Name | What It Means | Example |
|-----------|--------------|---------|
| product | Which product | Product #10 |
| image | Image file | "products/coke1.jpg" |
| is_primary | Is this the main image? | True/False |

**Key Points:**
- One product can have many images
- Only one image should be marked as primary (main photo)

---

### 7️⃣ Carts Table

Each retailer has ONE shopping cart.

**What's Stored:**

| Field Name | What It Means | Example |
|-----------|--------------|---------|
| retailer | Who owns this cart | User #1 |
| created_at | When cart was created | "2025-11-30 10:00:00" |
| updated_at | Last time cart changed | "2025-11-30 14:30:00" |

**Key Points:**
- One cart per retailer
- Cart stays active until converted to an order

---

### 8️⃣ Cart Items Table

Products inside each cart.

**What's Stored:**

| Field Name | What It Means | Example |
|-----------|--------------|---------|
| cart | Which cart | Cart #1 |
| product | Which product | Product #10 |
| quantity | How many | 24 |

**Key Points:**
- Price is calculated automatically based on quantity:
  - If quantity ≥ bulk_quantity, use bulk_price
  - Otherwise, use unit_price
- Can't add same product twice (quantity updates instead)

---

### 9️⃣ Orders Table

Orders placed by retailers.

**What's Stored:**

| Field Name | What It Means | Example |
|-----------|--------------|---------|
| order_number | Unique order ID | "RC-A1B2C3D4" |
| retailer | Who placed order | User #1 |
| wholesaler | Who receives order | User #5 |
| status | Order stage | "pending", "confirmed", "delivered" |
| subtotal | Total before delivery | 10000.00 |
| delivery_fee | Delivery cost | 500.00 |
| total_amount | Final total | 10500.00 |
| delivery_address | Where to deliver | "123 Main Street" |
| delivery_city | City | "Nairobi" |
| is_paid | Has payment been made? | True/False |
| paid_at | When payment was made | "2025-11-30 15:00:00" |

**Order Status Flow:**
```
pending → confirmed → processing → shipped → delivered
   ↓                                             
cancelled
```

**Key Points:**
- Order number is auto-generated (starts with "RC-")
- One order is for ONE wholesaler only
- If buying from 2 wholesalers, you make 2 orders

---

### 🔟 Order Items Table

Products inside each order.

**What's Stored:**

| Field Name | What It Means | Example |
|-----------|--------------|---------|
| order | Which order | Order #1 |
| product | Which product | Product #10 |
| product_name | Product name (saved) | "Coca Cola 500ml" |
| quantity | How many | 24 |
| unit_price | Price per item (saved) | 45.00 |
| total_price | Total for this item | 1080.00 |

**Key Points:**
- We save product_name and unit_price at time of order
- Even if product is deleted later, we still have the order history
- Total price = quantity × unit_price

---

### 1️⃣1️⃣ Payments Table

Payment transactions (mainly M-Pesa).

**What's Stored:**

| Field Name | What It Means | Example |
|-----------|--------------|---------|
| transaction_id | Unique payment ID | "PAY-A1B2C3D4E5F6" |
| order | Which order | Order #1 |
| amount | How much | 10500.00 |
| payment_method | How they paid | "mpesa", "card", "bank" |
| status | Payment stage | "pending", "completed", "failed" |
| phone_number | M-Pesa phone number | "+254712345678" |
| mpesa_receipt_number | M-Pesa confirmation code | "QGH123ABC" |
| completed_at | When payment succeeded | "2025-11-30 15:05:00" |

**Payment Status Flow:**
```
pending → processing → completed
   ↓            ↓
failed      failed
```

**Key Points:**
- Transaction ID is auto-generated (starts with "PAY-")
- For M-Pesa, we save receipt number for proof
- One order can have multiple payments (e.g., partial payments)

---

### 1️⃣2️⃣ Deliveries Table

Tracking deliveries for each order.

**What's Stored:**

| Field Name | What It Means | Example |
|-----------|--------------|---------|
| order | Which order | Order #1 |
| driver_name | Delivery person name | "John Doe" |
| driver_phone | Driver phone | "+254712345678" |
| vehicle_number | Vehicle plate | "KCA 123A" |
| status | Delivery stage | "pending", "in_transit", "delivered" |
| estimated_delivery_time | Expected delivery | "2025-12-01 14:00:00" |
| actual_delivery_time | When actually delivered | "2025-12-01 14:15:00" |

**Delivery Status Flow:**
```
pending → assigned → in_transit → delivered
   ↓                                ↓
failed                          failed
```

**Key Points:**
- ONE delivery per order
- Driver info is optional (can be empty)
- Tracks both estimated and actual delivery times

---

## 🔗 Part 3: How Tables Connect (Relationships)

### User → Retailer Profile (One-to-One)
- Each user can have ONLY ONE retailer profile
- If user is deleted, their profile is also deleted

### User → Wholesaler Profile (One-to-One)
- Each user can have ONLY ONE wholesaler profile
- If user is deleted, their profile is also deleted

### User → Cart (One-to-One)
- Each retailer has ONLY ONE cart
- If user is deleted, their cart is also deleted

### Wholesaler → Products (One-to-Many)
- One wholesaler can have MANY products
- One product belongs to ONE wholesaler
- If wholesaler is deleted, their products are also deleted

### Product → Product Images (One-to-Many)
- One product can have MANY images
- One image belongs to ONE product
- If product is deleted, its images are also deleted

### Cart → Cart Items (One-to-Many)
- One cart can have MANY cart items
- One cart item belongs to ONE cart
- If cart is deleted, all cart items are also deleted

### Order → Order Items (One-to-Many)
- One order can have MANY order items
- One order item belongs to ONE order
- If order is deleted, all order items are also deleted

### Order → Payment (One-to-Many)
- One order can have MANY payments
- One payment belongs to ONE order
- If order is deleted, payment records remain (for accounting)

### Order → Delivery (One-to-One)
- One order has ONLY ONE delivery record
- If order is deleted, delivery record is also deleted

---

## 📊 Part 4: Example Shopping Flow

Let's see how all these tables work together:

### Step 1: Retailer Browses Products
```
Retailer "myshop" (User #1) searches for "Coca Cola"
→ Looks in Products table where name contains "Coca Cola"
→ Finds Product #10 (owned by Wholesaler User #5)
```

### Step 2: Retailer Adds to Cart
```
POST /api/v1/cart/items/
{
  "product": 10,
  "quantity": 24
}

→ Finds Cart #1 (belongs to User #1)
→ Creates CartItem: cart=1, product=10, quantity=24
→ Price calculated: 24 × 45.00 (bulk price) = 1080.00
```

### Step 3: Retailer Checks Out
```
POST /api/v1/orders/checkout/

→ Creates Order #1:
  - retailer = User #1
  - wholesaler = User #5 (from product owner)
  - subtotal = 1080.00
  - delivery_fee = 500.00
  - total_amount = 1580.00
  - status = "pending"

→ Creates OrderItem:
  - order = Order #1
  - product = Product #10
  - product_name = "Coca Cola 500ml" (saved snapshot)
  - quantity = 24
  - unit_price = 45.00 (saved snapshot)
  - total_price = 1080.00

→ Clears Cart #1 items
```

### Step 4: Retailer Pays via M-Pesa
```
POST /api/v1/payments/mpesa/

→ Creates Payment #1:
  - transaction_id = "PAY-A1B2C3D4E5F6"
  - order = Order #1
  - amount = 1580.00
  - payment_method = "mpesa"
  - status = "pending"

→ After M-Pesa confirmation:
  - Updates Payment #1: status = "completed"
  - Updates Order #1: is_paid = True
  - Updates Order #1: status = "confirmed"
```

### Step 5: Wholesaler Prepares Order
```
Wholesaler updates order status:

→ Updates Order #1: status = "processing"
→ Updates Product #10: stock_quantity = 500 - 24 = 476
```

### Step 6: Delivery is Arranged
```
POST /api/v1/deliveries/

→ Creates Delivery #1:
  - order = Order #1
  - driver_name = "John Doe"
  - driver_phone = "+254712345678"
  - status = "assigned"

→ Updates Order #1: status = "shipped"
```

### Step 7: Order is Delivered
```
PUT /api/v1/deliveries/1/

→ Updates Delivery #1:
  - status = "delivered"
  - actual_delivery_time = "2025-12-01 14:15:00"

→ Updates Order #1: status = "delivered"
```

---

## 🎯 Part 5: Important Security Rules

### Who Can Do What?

**Everyone (No Login Required):**
- Browse products
- View categories
- See wholesaler profiles (public info)

**Logged-In Retailers Can:**
- Add products to cart
- Place orders
- View their own orders
- Make payments
- View delivery status

**Logged-In Wholesalers Can:**
- Add/edit/delete their own products
- View orders for their products
- Update order status
- View payment confirmations

**Admins Can:**
- Do everything
- Verify users
- Manage all orders
- View all payments

### How Security Works

1. **Token Required**: Most actions require a valid access token
2. **User Type Check**: System checks if you're a retailer/wholesaler
3. **Ownership Check**: You can only edit your own data
   - Retailers can only see their own orders
   - Wholesalers can only edit their own products

---

## 🔍 Part 6: Common Questions

### Q: How does bulk pricing work?
**A:** If a product has:
- unit_price = 50.00
- bulk_price = 45.00
- bulk_quantity = 24

Then:
- Buy 23 items → Pay 23 × 50.00 = 1,150.00
- Buy 24 items → Pay 24 × 45.00 = 1,080.00 (saved 120.00!)

### Q: Can a user be both retailer AND wholesaler?
**A:** No. Each user account is one type only. If someone wants both, they need 2 separate accounts.

### Q: What happens if a product is deleted after someone ordered it?
**A:** The order is safe! We save the product name and price in the OrderItem table. Even if Product #10 is deleted, Order #1 still shows what was ordered.

### Q: Can one order have products from different wholesalers?
**A:** No. Each order is for ONE wholesaler only. If you want products from 2 wholesalers, make 2 separate orders.

### Q: How long do tokens last?
**A:**
- Access Token: 1 hour
- Refresh Token: 7 days
- After 7 days, you must login again

### Q: What is the order of table creation in database?
**A:**
1. First: users (because everything needs users)
2. Then: categories (needed for products)
3. Then: retailer_profiles, wholesaler_profiles (need users)
4. Then: products (need users and categories)
5. Then: product_images (need products)
6. Then: carts (need users)
7. Then: cart_items (need carts and products)
8. Then: orders (need users)
9. Then: order_items (need orders and products)
10. Then: payments (need orders)
11. Finally: deliveries (need orders)

---

## 📝 Summary

**Authentication:**
- Login with username + password → Get tokens
- Use access token for 1 hour
- Refresh with refresh token for up to 7 days

**Database:**
- 12 main tables storing all information
- Tables are connected (users → products → orders → payments → deliveries)
- Security ensures users only access their own data

**Shopping Flow:**
Browse → Add to Cart → Checkout → Pay → Deliver

That's it! You now understand how authentication and the database work in RetailConnect Kenya. 🎉
