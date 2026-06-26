"""
generate_data.py — Creates a realistic synthetic e-commerce dataset.
Run once: python generate_data.py
"""
import sqlite3
import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

random.seed(42)
np.random.seed(42)

# ── Config ──────────────────────────────────────────────────────────────────
N_CUSTOMERS  = 1_200
N_PRODUCTS   = 80
N_ORDERS     = 8_000
START_DATE   = datetime(2023, 1, 1)
END_DATE     = datetime(2024, 12, 31)

CATEGORIES = {
    "Electronics":   (120, 900),
    "Clothing":      (20,  150),
    "Home & Garden": (15,  300),
    "Sports":        (25,  400),
    "Books":         (8,   60),
}

REGIONS  = ["North", "South", "East", "West", "Central"]
CHANNELS = ["Organic", "Paid Ads", "Email", "Social Media", "Referral"]

# ── Customers ────────────────────────────────────────────────────────────────
customers = pd.DataFrame({
    "customer_id":   range(1, N_CUSTOMERS + 1),
    "age":           np.random.randint(18, 70, N_CUSTOMERS),
    "region":        np.random.choice(REGIONS, N_CUSTOMERS),
    "channel":       np.random.choice(CHANNELS, N_CUSTOMERS,
                         p=[0.30, 0.25, 0.20, 0.15, 0.10]),
    "signup_date":   [START_DATE + timedelta(days=random.randint(0, 365))
                      for _ in range(N_CUSTOMERS)],
    "age_group":     None,
})
customers["age_group"] = pd.cut(
    customers["age"], bins=[0, 25, 35, 50, 100],
    labels=["18-25", "26-35", "36-50", "50+"]
)

# ── Products ─────────────────────────────────────────────────────────────────
products = []
pid = 1
for cat, (lo, hi) in CATEGORIES.items():
    for i in range(N_PRODUCTS // len(CATEGORIES)):
        products.append({
            "product_id":   pid,
            "product_name": f"{cat} Item {i+1}",
            "category":     cat,
            "price":        round(random.uniform(lo, hi), 2),
            "cost":         None,
        })
        pid += 1
products_df = pd.DataFrame(products)
products_df["cost"] = (products_df["price"] * np.random.uniform(0.35, 0.65,
                         len(products_df))).round(2)

# ── Orders ────────────────────────────────────────────────────────────────────
total_days = (END_DATE - START_DATE).days

def seasonal_weight(d):
    """Higher orders in Q4 + summer."""
    m = d.month
    if m in [11, 12]: return 2.5
    if m in [6, 7, 8]: return 1.4
    return 1.0

all_dates = [START_DATE + timedelta(days=i) for i in range(total_days)]
weights   = [seasonal_weight(d) for d in all_dates]
w_sum     = sum(weights)
probs     = [w / w_sum for w in weights]

order_dates     = np.random.choice(all_dates, size=N_ORDERS, p=probs)
order_customers = np.random.choice(customers["customer_id"], size=N_ORDERS)
order_products  = np.random.choice(products_df["product_id"], size=N_ORDERS)
order_qty       = np.random.choice([1, 2, 3, 4, 5], size=N_ORDERS,
                                   p=[0.50, 0.25, 0.13, 0.08, 0.04])

orders = pd.DataFrame({
    "order_id":    range(1, N_ORDERS + 1),
    "customer_id": order_customers,
    "product_id":  order_products,
    "order_date":  order_dates,
    "quantity":    order_qty,
    "status":      np.random.choice(
                       ["Completed", "Completed", "Completed",
                        "Returned", "Cancelled"],
                       size=N_ORDERS),
})

orders = orders.merge(products_df[["product_id", "price", "cost"]], on="product_id")
orders["revenue"] = (orders["price"] * orders["quantity"]).round(2)
orders["profit"]  = ((orders["price"] - orders["cost"]) * orders["quantity"]).round(2)
orders["year_month"] = pd.to_datetime(orders["order_date"]).dt.to_period("M").astype(str)

# ── Write to SQLite ───────────────────────────────────────────────────────────
conn = sqlite3.connect("data/ecommerce.db")
customers.to_sql("customers",  conn, if_exists="replace", index=False)
products_df.to_sql("products", conn, if_exists="replace", index=False)
orders.to_sql("orders",        conn, if_exists="replace", index=False)
conn.close()
print("✅  Database created: data/ecommerce.db")
print(f"   Customers : {len(customers):,}")
print(f"   Products  : {len(products_df):,}")
print(f"   Orders    : {len(orders):,}")
print(f"   Revenue   : ${orders[orders.status=='Completed']['revenue'].sum():,.0f}")
