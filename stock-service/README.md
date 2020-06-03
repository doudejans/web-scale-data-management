# Stock Service

This service contains the logic for the stock service. 
This includes four routes as defined in the assignment:
The price of the stock is defined as an integer.

### Availability
```GET /stock/find/{item_id}```

Return an item's stock and price.

### Subtract from stock item
```POST /stock/subtract/{item_id}/{number}```

Subtract a given number of stock items from the item count in the stock.

### Add to stock item
```POST /stock/add/{item_id}/{number}```

Add a given number of stock items to the item count in the stock.

### Create item
```POST /stock/item/create/{price}```

Create an item along with its price and returns its ID.
