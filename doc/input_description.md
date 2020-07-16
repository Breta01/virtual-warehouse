# Input Description
Input should be in form of tabular data (ideally CSV or excel).

## Data Structure
Data consists of 5 tables

### XYZ Coordinates
Describes the positions of locations in the warehouse.  
Columns:

- Location name
- X coord.
- Y coord.
- Z coord.

### Location Master
Describes properties of individual location. Optional columns are for areas storing items.  
Columns:
- Location name (same as in XYZ table)
- Location type
- Location class
- Location subclass
- Length
- Width
- Height
- Dimension units
- *Maximum weight (optional)*
- *Weight units (optional)*
- *Zone (optional)*

### Item Master
Describes individual items which may occure in warehouse. For each item there can be multiple levels of packaging.  
Columns:
- Item ID
- Description
- Goods type
- Zone - zone from location master where item can be stored
- Conversion quantity (base unit)
- Quantity unit of measure (base unit)
- Length (base unit)
- Width (base unit)
- Height (base unit)
- Dimension unit of measure (base unit)
- Weight (base unit)
- Weight unit of measure (2. lvl unit)
- Conversion quantity (2. lvl unit)
- Quantity unit of measure (2. lvl unit)
- Length (2. lvl unit)
- Width (2. lvl unit)
- Height (2. lvl unit)
- Dimension unit of measure (2. lvl unit)
- Weight (2. lvl unit)
- Weight unit of measure (2. lvl unit)
- ... (more levels)

### Inventory Balance
Description of current warehouse inventory (matching location master with item master).  
Columns:
- Inventory as at (date of snapshot)
- Location
- Location type
- Item ID
- Expiry date
- Available quantity
- Onhand quantity
- In transit quantity
- Allocated quantity
- Suspense quantity

### Order list
List of all orderds up until now.  
Columns:
- Order ID
- Direction (outbound, inbound)
- *Ship to country (optional)*
- *Requested delivery date (optional)*
- *Scheduled ship date (optional)*
- *Actual ship date (optional)*
- ERP order line num
- Item ID
- Requested quantity
- Total quantity
- Quantity unit
