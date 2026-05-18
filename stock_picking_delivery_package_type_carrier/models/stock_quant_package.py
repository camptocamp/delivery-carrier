from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class StockQuantPackage(models.Model):
    _inherit = "stock.quant.package"

    result_move_line_ids = fields.One2many(
        comodel_name="stock.move.line",
        inverse_name="result_package_id",
        help="Technical field. Result move lines for this package.",
    )

    def _check_package_type_carrier_compatibility(self, package_type):
        dedicated_carriers = package_type.package_carrier_ids
        if not dedicated_carriers:
            return

        for package in self:
            package_carriers = package.result_move_line_ids.mapped(
                "picking_id.carrier_id"
            )
            if not package_carriers:
                continue
            if not any(carrier in dedicated_carriers for carrier in package_carriers):
                raise ValidationError(
                    _(
                        "Package type '%(package_type)s' is not valid for carrier"
                        " '%(carrier)s'."
                    )
                    % {
                        "package_type": package_type.name,
                        "carrier": package_carriers[0].name,
                    }
                )

    @api.constrains("package_type_id")
    def _check_package_type_id_carrier_compatibility(self):
        for package in self:
            if package_type := package.package_type_id:
                package._check_package_type_carrier_compatibility(package_type)
