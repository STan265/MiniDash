# MiniDash – Scheduled Orders Requirements

## 1. Project Overview

MiniDash is a restaurant ordering REST API built with Python, FastAPI, and SQLite.

This project extends the baseline ordering system with scheduled delivery functionality. Customers can place orders for future delivery, and the system automatically releases scheduled orders for processing 30 minutes before their requested delivery time.

## 2. User Stories

### US-01: Schedule a Delivery
As a customer, I want to schedule an order for a future date and time so that I can receive my food when I need it.

### US-02: Validate Scheduled Delivery Time
As a customer, I want the system to validate my requested delivery time so that I cannot schedule orders outside the permitted time window.

### US-03: Check Restaurant Availability
As a customer, I want the system to verify that the restaurant is open at my requested delivery time so that my order can be fulfilled.

### US-04: Automatically Release Scheduled Orders
As a restaurant, I want scheduled orders to be released 30 minutes before delivery so that preparation can begin at the appropriate time.

### US-05: Cancel Scheduled Orders
As a customer, I want to cancel my scheduled order before it is released so that I can change my plans.

## 3. Acceptance Criteria (EARS Format)

1. **Optional scheduling:** When a customer submits an order without a scheduled delivery time, the system shall process it through the normal immediate-order workflow.

2. **Minimum scheduling window:** When a customer requests a delivery time less than 45 minutes in the future, the system shall reject the request with `SCHEDULE_TOO_SOON`.

3. **Maximum scheduling window:** When a customer requests a delivery time more than 7 days in the future, the system shall reject the request with `SCHEDULE_TOO_FAR`.

4. **Restaurant operating hours:** When a customer requests a delivery time outside the restaurant's operating hours, the system shall reject the request with `RESTAURANT_CLOSED`.

5. **Scheduled order creation:** When a customer submits a valid scheduled order, the system shall save the requested delivery time and set the order status to `SCHEDULED`.

6. **Automatic release:** When a scheduled order reaches 30 minutes before its delivery time, the system shall change its status from `SCHEDULED` to `PLACED` exactly once.

7. **Cancellation:** When a customer cancels an order whose status is `SCHEDULED`, the system shall change its status to `CANCELLED` and prevent automatic release.

8. **Cancellation after release:** When a customer attempts to cancel an order after its status has changed to `PLACED`, the system shall reject the scheduled-order cancellation request.

9. **Injected clock:** When the application evaluates scheduling windows or releases orders, the system shall use an injected clock rather than directly accessing the operating system clock in business logic.

10. **Invalid date/time:** When a customer submits an invalid scheduled delivery date or time, the system shall reject the request with a clear validation error.

## 4. Out of Scope

The following features are not included:

- Customer authentication and account management
- Payment processing and refunds
- Driver assignment and delivery tracking
- GPS and real-time location tracking
- SMS and email notifications
- Recurring scheduled orders
- Multiple delivery addresses per customer
- Changes to menu items after an order is submitted

## 5. Assumptions and Constraints

- The application will use Python, FastAPI, and SQLite.
- Scheduled delivery times must be at least 45 minutes and no more than 7 days in the future.
- Exactly 45 minutes and exactly 7 days are valid boundaries.
- Orders will be released 30 minutes before the requested delivery time.
- Scheduled orders can only be cancelled before release.
- All scheduling logic will use an injectable clock to support deterministic testing.
- The restaurant's operating hours will determine whether a requested delivery time is permitted.

## 6. Definition of Done

The feature will be considered complete when:

- All acceptance criteria are implemented.
- Automated tests cover valid and invalid scheduling scenarios.
- Tests verify the 45-minute and 7-day boundaries.
- Tests verify automatic release and cancellation behavior.
- Tests use a controllable injected clock.
- The existing immediate-order workflow continues to function.
- The README documents how to run the application and tests.
- All changes are committed to Git.
