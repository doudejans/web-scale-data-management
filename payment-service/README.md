# Payment Service

This service contains the logic for they payment service. 
This includes three routes as defined in the assignment:

### Complete Payment
```POST /payment/pay/{user_id}/{order_id}```

Subtracts the amount of the order from the user’s credit (returns failure if credit is not enough)

### Cancel Payment
```POST /payment/cancel/{user_id}/{order_id}```

Cancels payment made by a specific user for a specific user.
- Does this mean cancel the payment as in cancel the order and set payment status to "Cancelled"?
- Or does it mean that we return the credits to the user after a payment has been made?

### Payment Status
```GET /payment/status/{order_id}```

Returns the status of the payment (paid or not).

---

For now I've defined the payment status as a string in the database: `PAID` or `CANCELLED`.