# Copyright 2025 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _set_a_default_package(self):
        """Pickings using this module must have a package

        If not this method put it one silently
        """
        # N.B.: This method was previously defined in the
        # ``delivery_postlogistics`` module,
        # but not needed there anymore, so we moved it here.
        for picking in self:
            move_lines = picking.move_line_ids.filtered(
                lambda s: not (s.package_id or s.result_package_id)
            )
            if move_lines:
                carrier = picking.carrier_id
                default_packaging = carrier.postlogistics_default_package_type_id
                package = self.env["stock.quant.package"].create(
                    {
                        "package_type_id": default_packaging
                        and default_packaging.id
                        or False
                    }
                )
                move_lines.write({"result_package_id": package.id})
