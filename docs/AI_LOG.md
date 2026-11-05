# AI Usage Log — MiniDash

## Entry #1 — November 5, 2026

**Tool, model, mode:** ChatGPT, GPT-6, conversational coding assistance

**Slice:** Project setup and requirements

**Prompt (verbatim or summarized):**

Help me understand and organize the MiniDash scheduled-order assignment and its implementation requirements.

**What the AI produced:**

A breakdown of the project requirements, application structure, API responsibilities, and implementation steps.

**What I've verified:**

Reviewed the assignment requirements and confirmed that the project structure supports the required restaurant and order functionality.

**What I changed and why:**

Organized the implementation into separate modules for database access, models, routes, services, and repositories to keep responsibilities separated.

**Outcome:**

Established the project structure and implementation plan.

---

## Entry #2 — November 5, 2026

**Tool, model, mode:** ChatGPT, GPT-6, conversational coding assistance

**Slice:** Restaurant API

**Prompt (verbatim or summarized):**

Help implement the restaurant endpoints for retrieving restaurants and their menu items.

**What the AI produced:**

Python FastAPI route implementation for retrieving restaurants and restaurant menus from SQLite.

**What I've verified:**

Ran the restaurant tests, including retrieving restaurants, retrieving menu items, and handling invalid restaurant IDs.

**What I changed and why:**

Adjusted the implementation to use the existing database connection and repository structure.

**Outcome:**

Restaurant API endpoints implemented and tested successfully.

---

## Entry #3 — November 5, 2026

**Tool, model, mode:** ChatGPT, GPT-6, conversational coding assistance

**Slice:** Order creation and status management

**Prompt (verbatim or summarized):**

Help implement order creation, order retrieval, and order status updates.

**What the AI produced:**

Pydantic request models, FastAPI endpoints, service logic, and SQLite repository operations.

**What I've verified:**

Ran automated tests for valid orders, invalid restaurants, menu-item ownership, order retrieval, and status updates.

**What I changed and why:**

Integrated the suggested implementation with the existing project structure and database schema.

**Outcome:**

Order creation, retrieval, and status management implemented.

---

## Entry #4 — November 5, 2026

**Tool, model, mode:** ChatGPT, GPT-6, conversational coding assistance

**Slice:** Scheduled-order validation

**Prompt (verbatim or summarized):**

Implement scheduled-order validation, including the 45-minute minimum, 7-day maximum, timezone requirement, and restaurant operating hours.

**What the AI produced:**

Validation logic using an injected clock and timezone-aware datetime comparisons.

**What I've verified:**

Ran tests for missing timezones, scheduling too soon, scheduling too far ahead, restaurant closing hours, and valid scheduled orders.

**What I changed and why:**

Reworked the test scheduling times after an initially suggested test time conflicted with restaurant operating hours. Updated the test cases to use valid restaurant delivery windows.

**Outcome:**

Scheduled-order validation implemented and verified.

---

## Entry #5 — November 5, 2026

**Tool, model, mode:** ChatGPT, GPT-6, conversational coding assistance

**Slice:** Automatic scheduled-order release

**Prompt (verbatim or summarized):**

Implement automatic release of scheduled orders 30 minutes before their requested delivery time.

**What the AI produced:**

A release function using an injected clock, a database update operation, and a background worker that periodically checks scheduled orders.

**What I've verified:**

Ran tests verifying that orders are released at the 30-minute boundary, are not released too early, and are not released more than once.

**What I changed and why:**

Integrated the release logic into the existing order service and connected the worker to the FastAPI application lifecycle.

**Outcome:**

Automatic scheduled-order release implemented.

---

## Entry #6 — November 5, 2026

**Tool, model, mode:** ChatGPT, GPT-6, conversational coding assistance

**Slice:** Scheduled-order cancellation

**Prompt (verbatim or summarized):**

Implement cancellation for scheduled orders before they are released.

**What the AI produced:**

A cancellation service function and SQLite repository update that changes eligible scheduled orders to CANCELLED.

**What I've verified:**

Ran tests confirming cancellation before the release boundary and rejection at the 30-minute boundary.

**What I changed and why:**

Used a conditional database update to prevent cancellation after an order becomes eligible for release.

**Outcome:**

Scheduled-order cancellation implemented and tested.

---

## Entry #7 — November 5, 2026

**Tool, model, mode:** ChatGPT, GPT-6, conversational coding assistance

**Slice:** Documentation and automated testing

**Prompt (verbatim or summarized):**

Help review the project documentation, stabilize the tests, and verify the complete application.

**What the AI produced:**

Documentation updates, testing instructions, and suggested commands for running pytest.

**What I've verified:**

The initial `pytest -v` command failed to locate the `src` package. Running `python -m pytest -v` successfully discovered and executed all 18 tests.

**What I changed and why:**

Rejected the initial test command for this Windows environment and used `python -m pytest -v` instead because it correctly resolved the project imports.

**Outcome:**

All 18 automated tests passed.

---

## Entry #8 — November 5, 2026

**Tool, model, mode:** ChatGPT, GPT-6, conversational coding assistance

**Slice:** Transition from backend-only application to frontend implementation

**Prompt (verbatim or summarized):**

After completing the backend functionality, I wanted to change the project from a backend-focused API application into a customer-facing website. I asked ChatGPT to help implement a frontend that allows customers to browse restaurants, view menus, add items to a cart, place immediate or scheduled orders, track orders, and cancel scheduled orders.

**What the AI produced:**

Initially, the project was focused on backend functionality using FastAPI and SQLite. ChatGPT suggested adding an optional frontend using HTML, CSS, and JavaScript without introducing additional frameworks or dependencies. It provided the frontend implementation and modifications to FastAPI to serve the website.

**What I've verified:**

Confirmed that the homepage loads, restaurant data is retrieved, CSS and JavaScript files return HTTP 200, an immediate order was successfully placed, a scheduled order was created, and a scheduled order was successfully cancelled.

**What I changed and why:**

Changed the project scope from a backend-only ordering API to a full-stack restaurant ordering application. I decided to implement the frontend rather than keep the application limited to API endpoints because a customer-facing interface makes the system easier to use and demonstrate. I kept the existing backend responsible for order processing, validation, scheduling, and database operations.

**Outcome:**

Successfully extended MiniDash with a working customer-facing frontend while preserving the existing backend functionality and all 18 passing automated tests.

## Entry #9 — November 5, 2026

**Tool, model, mode:** ChatGPT, GPT-6, conversational coding assistance

**Slice:** Multi-page frontend implementation

**Prompt (verbatim or summarized):**

After implementing the initial single-page customer-facing website, I requested a redesign with separate pages for restaurant menus, checkout, order confirmation, and order tracking.

**What the AI produced:**

A multi-page frontend implementation using HTML, CSS, and JavaScript, including separate restaurant menu pages, a checkout page, an order confirmation page, and an order tracking page.

**What I've verified:**

Manually tested the homepage, restaurant menu, adding items to the cart, checkout, order placement, and order tracking. Confirmed that the frontend communicates with the FastAPI backend.

**What I changed and why:**

Replaced the original single-page layout with a multi-page structure to improve navigation and organize the customer ordering experience. Preserved the existing backend API and database functionality.

**Outcome:**

Implemented the multi-page customer-facing frontend and verified the main ordering workflow.