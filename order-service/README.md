# Order service

## Endpoints

### Create order
`POST /create/<uuid:user_id>`

Creates a new order for the user with the given UUID `user_id`. 
This returns the generated order_id in the following way:
```json
{
  "status": 201,
  "order_id": "49a8870a-4400-4fec-a47c-521ee365e761"
}
```

### Remove order
`DELETE /remove/<uuid:order_id>`

Deletes the order with the given UUID `order_id`.
Returns the following if successful:
```json
{
  "status": 200,
  "message": "success"
}
```

### Find order
`GET /find/<uuid:order_id>`

Finds the order with the given UUID `order_id` and returns the associated `user_id`, the items in the order, and the payment status.

For now, it returns only the `user_id` and the items, as no connection with the payment service is implemented yet.

Example response:
```json
{
  "status": 200,
  "order": {
    "order_id": "49a8870a-4400-4fec-a47c-521ee365e761",
    "user_id": "55888c00-b375-4f08-a8dc-9e28b57b4b18",
    "items": [
      {
        "item_id": "5e29052a-b86a-47ff-9a66-de3634a614ce",
        "amount": 2
      }
    ] 
  }
}
```

### Add item to order
`POST /addItem/<uuid:order_id>/<uuid:item_id>`

Adds the item with the given UUID `item_id` to the order with the given UUID `order_id`. 

Currently does not check whether the item actually exists in the stock service.

If the order is not found, it returns a `404 NOT FOUND` status.

Response if successful:
```json
    {
      "status": 200,
      "message": "success"
    }
```

### Removes item to order
`DELETE /addItem/<uuid:order_id>/<uuid:item_id>`

Remove the item with the given UUID `item_id` from the order with the given UUID `order_id`.

Does not check if the order actually contained the item. 
In the postgres implementation this has no effect, but in the cassandra implementation the "amount" counter can go negative because of this.

Response if successful:
```json
    {
      "status": 200,
      "message": "success"
    }
```

### Checkout order
`POST /checkout/<uuid:order_id>>`

Not implemented yet. Should contact the stock and payment services in a single transaction that completes the order.



To do:
- Connect to other services
- Implement checkout endpoint
- Evaluate cassandra consistency for order items
- Check if items exists before adding to order by contacting stock service
