This module provides granular control over which service products impact the calculation of the Sales Order's scheduled delivery date.

The module introduces a field and modifies the core logic for calculating a line's impact on delivery time (`_is_delivery` method on `sale.order.line`).

1.  New Field: A boolean field named "Affect Delivery Date" is added to the product template ("Sales" tab, "Extra Info" section).
2.  Service Exclusion (Default): All products of type `service` are now set to NOT affect the order's delivery date calculation by default, regardless of the new flag's state.
3.  Opt-In Mechanism: Only if the product is of type `service` AND the "Affect Delivery Date" flag is explicitly checked, will that line be included in the planning and scheduling that drives the final expected date.
4.  Physical Goods: Storable and Consumable products always affect the delivery date (their logic remains unchanged from Odoo standard).
