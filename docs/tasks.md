# MiniDash – Scheduled Orders Implementation Tasks

## Task 1: Set Up the Baseline Application

**Description:**
- Create the FastAPI application.
- Configure the SQLite database connection.
- Organize routes, services, and repositories.
- Add initial restaurant and menu data.

**Test:**
- Verify the application starts successfully.
- Verify GET /restaurants returns restaurant data.

## Task 2: Implement Restaurant and Menu Endpoints

**Description:**
- Implement GET /restaurants.
- Implement GET /restaurants/{id}/menu.
- Retrieve data through the repository layer.

**Test:**
- Verify the restaurant list is returned.
- Verify restaurant menu items are returned.
- Verify an invalid restaurant ID returns an appropriate error.

## Task 3: Implement Immediate Order Creation

**Description:**
- Implement POST /orders.
- Validate restaurant and menu item information.
- Calculate order totals.
- Save orders and order items in SQLite.

**Test:**
- Verify a valid order is created.
- Verify the order total is calculated correctly.
- Verify invalid menu items are rejected.

## Task 4: Implement Order Retrieval and Status Updates

**Description:**
- Implement GET /orders/{id}.
- Implement PATCH /orders/{id}/status.
- Support the required order status transitions.

**Test:**
- Verify an existing order can be retrieved.
- Verify an invalid order ID returns an error.
- Verify valid and invalid status updates are handled correctly.

## Task 5: Implement Scheduled Order Validation

**Description:**
- Add the optional scheduled_for field.
- Implement an injectable clock.
- Validate the 45-minute minimum scheduling window.
- Validate the 7-day maximum scheduling window.
- Check restaurant operating hours.
- Store valid scheduled orders with status SCHEDULED.

**Test:**
- Verify immediate orders still work.
- Verify exactly 45 minutes is accepted.
- Verify exactly 7 days is accepted.
- Verify times outside the permitted window are rejected.
- Verify orders requested outside restaurant operating hours are rejected.

## Task 6: Implement Automatic Scheduled Order Release

**Description:**
- Implement the scheduled-order release service.
- Identify scheduled orders due for release.
- Change eligible orders from SCHEDULED to PLACED when they reach 30 minutes before delivery.
- Ensure repeated checks do not release the same order twice.

**Test:**
- Verify an order is not released before the 30-minute window.
- Verify an order is released at the 30-minute boundary.
- Verify an order is released only once.
- Verify cancelled orders are not released.

## Task 7: Implement Scheduled Order Cancellation

**Description:**
- Allow customers to cancel scheduled orders more than 30 minutes before delivery.
- Change the order status to CANCELLED.
- Reject cancellation at or after the 30-minute release boundary.

**Test:**
- Verify a scheduled order can be cancelled.
- Verify a cancelled order cannot be released.
- Verify cancellation is rejected at exactly 30 minutes before delivery and after an order has been released to PLACED.

## Task 8: Final Integration, Documentation, and Verification

**Description:**
- Integrate all application components.
- Update README.md with setup and execution instructions.
- Verify all API endpoints.
- Review error handling and database behavior.
- Run the complete automated test suite.
- Verify the background worker checks for releasable orders every 30 seconds.
- Verify the worker shuts down cleanly when the application stops.

**Test:**
- Run pytest.
- Verify all tests pass.
- Start the application with Uvicorn.
- Manually verify the API through /docs.
- Confirm the immediate-order workflow still works alongside scheduled orders.