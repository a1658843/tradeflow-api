# TradeFlow API

A backend system for managing trade operations including customers, suppliers, products, orders, and shipments.

Built with FastAPI, this project simulates a real-world trade workflow with authentication, business logic validation, analytics, and containerized deployment.

---

## Tech Stack

- Python
- FastAPI
- SQLAlchemy
- SQLite
- JWT Authentication
- Pytest
- Docker

---

## Features

### Core Modules
- User authentication (JWT login)
- Customer management
- Supplier management
- Product catalog
- Order processing
- Shipment tracking

### Business Logic
- Automatic order total calculation
- Date validation (delivery must be after shipment)
- Unique constraints (SKU, email, tracking number)
- Shipment status updates linked to orders

### Analytics
- Orders by status
- Top products by quantity
- Shipment status summary

### Security
- Protected routes using JWT
- Role-based user structure (admin, operations)

### Testing
- API tests using pytest
- Authentication and protected route validation
- Business rule validation

---

## Running Locally (without Docker)

Start the server:

```bash
uvicorn app.main:app --reload
```

Open in browser:

http://127.0.0.1:8000/docs

---

## Running with Docker

### Build image

```bash
docker build -t tradeflow-api .
```

### Run container
```bash
docker run -d -p 8000:8000 tradeflow-api
```

Open in browser:

http://localhost:8000/docs

---

## Example Workflow

1. Register or log in to obtain a JWT token  
2. Create customers, suppliers, and products  
3. Create an order with quantity and pricing  
4. Automatically calculate total order value  
5. Create a shipment linked to the order  
6. Update shipment status (pending → shipped → delivered)  
7. View analytics for orders and shipments  