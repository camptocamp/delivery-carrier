# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.onchange("carrier_id")
    def _onchange_carrier_id_set_picking_policy(self):
        if self.carrier_id:
            self.picking_policy = self.carrier_id.picking_policy

    def set_delivery_line(self, carrier, amount):
        res = super().set_delivery_line(carrier, amount)
        if carrier.picking_policy:
            self.picking_policy = carrier.picking_policy
        return res
