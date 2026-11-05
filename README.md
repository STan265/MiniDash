# MiniDash – Scheduled Orders API

## 1. Project Overview

MiniDash is a restaurant ordering REST API built using Python, FastAPI, and SQLite.

This project implements a restaurant ordering system with support for immediate orders and scheduled deliveries.

Customers can:
- View available restaurants and their menus.
- Place immediate orders.
- Schedule orders for future delivery.
- Retrieve order details and update order statuses.
- Cancel scheduled orders before their release time.

Scheduled orders are automatically released for processing 30 minutes before their requested delivery time.

## 2. Technologies Used

- Python
- FastAPI
- SQLite
- Pydantic
- Pytest
- HTTPX
- Uvicorn

## 3. Project Structure

```text
MiniDash/
├── docs/
│   ├── requirements.md
│   ├── design.md
│   └── tasks.md
├── src/
│   ├── routes/
│   │   ├── restaurants.py
│   │   └── orders.py
│   ├── services/
│   │   └── orders.py
│   ├── repositories/
│   │   └── orders.py
│   ├── database.py
│   ├── models.py
│   └── main.py
├── tests/
│   ├── test_restaurants.py
│   └── test_orders.py
├── .gitignore
├── requirements.txt
└── README.md
```

## 4. Installation

### Prerequisites

- Python installed
- Git installed

### Create a Virtual Environment

From the project directory, run:

```powershell
python -m venv .venv
```

### Activate the Virtual Environment

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks script execution, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then activate the environment again.

### Install Dependencies

```powershell
pip install -r requirements.txt
```

## 5. Running the Application

Start the FastAPI application using Uvicorn:

```powershell
python -m uvicorn src.main:app --reload
```

The API will be available at:

`http://127.0.0.1:8000`

Interactive API documentation is available at:

`http://127.0.0.1:8000/docs`

The SQLite database is initialized automatically when the application starts.

## 6. API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/restaurants` | Retrieve all restaurants |
| GET | `/restaurants/{id}/menu` | Retrieve a restaurant's menu |
| POST | `/orders` | Create an immediate or scheduled order |
| GET | `/orders/{id}` | Retrieve order details |
| PATCH | `/orders/{id}/status` | Update an order's status |

## 7. Scheduled Order Functionality

Scheduled orders support the following rules:

- Delivery must be at least 45 minutes in the future.
- Delivery cannot be more than 7 days in the future.
- Scheduled delivery timestamps must include timezone information.
- The restaurant must be open at the requested delivery time.
- Valid scheduled orders are initially assigned the `SCHEDULED` status.
- Orders are automatically changed to `PLACED` 30 minutes before delivery.
- Customers can cancel scheduled orders more than 30 minutes before delivery.

A background worker checks for scheduled orders every 30 seconds. The release operation updates only orders that are still in the `SCHEDULED` status, preventing duplicate releases.

Scheduled timestamps are stored in UTC. Restaurant operating-hours validation currently assumes the submitted time's clock time corresponds to the restaurant's operating-hours time.

## 8. Order Statuses

The application supports these order statuses:

- `SCHEDULED`
- `PLACED`
- `PREPARING`
- `READY`
- `DELIVERED`
- `CANCELLED`

## 9. Running Automated Tests

Run the complete test suite from the project directory:

```powershell
python -m pytest -v
```

The tests cover:

- Restaurant and menu retrieval.
- Immediate order creation.
- Order retrieval and status updates.
- Scheduled delivery validation.
- Minimum and maximum scheduling boundaries.
- Restaurant operating hours.
- Automatic scheduled-order release.
- Scheduled-order cancellation.

Time-dependent service logic uses an injected clock so scheduling behavior can be tested without waiting for real time to pass.

## 10. Database

MiniDash uses SQLite to store:

- Restaurants
- Menu items
- Orders
- Order items

The database is initialized automatically when the application starts. The local database file is named `minidash.db`.

## 11. Project Documentation

Additional project documentation is available in the `docs/` directory:

- `requirements.md` – User stories, acceptance criteria, assumptions, and out-of-scope features.
- `design.md` – Architecture, API interfaces, database changes, and architecture decision record.
- `tasks.md` – Implementation tasks and corresponding tests.