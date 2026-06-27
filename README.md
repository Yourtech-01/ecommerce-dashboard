# E-Commerce Sales Intelligence Dashboard

🚀 **Live Demo:** [https://ecommerce-dashboard-2-u4rt.onrender.com]

⚡ Note: App may take 30 seconds to load on first visit (free tier cold start)

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Dash](https://img.shields.io/badge/Dash-2.17-informational)
![Plotly](https://img.shields.io/badge/Plotly-5.22-blueviolet)
![Render](https://img.shields.io/badge/Deployed-Render-brightgreen)

An interactive analytics dashboard built with **Plotly Dash** that gives business 
stakeholders a full view of sales performance, customer behaviour, and product trends.

## Features
- KPI cards: Revenue, Orders, Profit, AOV
- Monthly revenue vs profit trend (area + line)
- Revenue by category (donut), region (bar), channel (bar)
- Order status breakdown (donut)
- Top 10 products by revenue
- Revenue by customer age group
- Live filtering by Category and Date Range

## Stack
| Layer       | Technology                  |
|-------------|----------------------------|
| Dashboard   | Plotly Dash + Bootstrap     |
| Data        | Pandas + SQLite             |
| Charts      | Plotly Express / Graph Objects |
| Deployment  | Render (free tier)          |

## Run Locally
```bash
pip install -r requirements.txt
python generate_data.py      # creates data/ecommerce.db
python app.py                # → http://localhost:8050
```

## Free Deployment (Render)
1. Push to GitHub
2. New → Web Service on render.com
3. Build command: `pip install -r requirements.txt && python generate_data.py`
4. Start command: `gunicorn app:server`
5. Add `gunicorn` to requirements.txt

## Skills Demonstrated
- SQL + Pandas data transformation
- Interactive dashboard design
- Business KPI definition & storytelling
- Seasonal trend analysis
- Customer segmentation (RFM proxy)
