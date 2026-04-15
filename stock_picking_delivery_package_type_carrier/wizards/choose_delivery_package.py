# Copyright 2026 Camptocamp SA (https://www.camptocamp.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class ChooseDeliveryPackage(models.TransientModel):
    _inherit = "choose.delivery.package"

    def _compute_package_type_domain(self):
        package_carrier = self.picking_id.carrier_id
        if not package_carrier:
            return super()._compute_package_type_domain()
        # if package has specific carrier defined, use that for the domain
        domain = [("package_carrier_id", "=", package_carrier.id)]
        for wizard in self:
            wizard.package_type_domain = domain
