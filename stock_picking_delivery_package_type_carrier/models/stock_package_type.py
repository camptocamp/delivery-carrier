# Copyright 2026 Camptocamp SA (https://www.camptocamp.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class PackageType(models.Model):
    _inherit = "stock.package.type"

    package_carrier_id = fields.Many2one(
        "delivery.carrier",
        string="Dedicated carrier",
    )
