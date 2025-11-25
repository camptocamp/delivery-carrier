# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _is_delivery(self):
        if (
            self.product_id
            and self.product_id.type == "service"
            and not self.product_id.affect_delivery_date
        ):
            return True
        return super()._is_delivery()
