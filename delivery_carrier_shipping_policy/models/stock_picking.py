# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.onchange("carrier_id")
    def _onchange_carrier_id_set_move_type(self):
        if self.carrier_id.picking_policy:
            self.move_type = self.carrier_id.picking_policy
