# Copyright 2025 Camptocamp
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    affect_delivery_date = fields.Boolean(
        help="By default, this product won’t impact the sales order delivery date"
        " computation unless this is flagged.",
    )
