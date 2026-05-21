from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class StockQuantPackage(models.Model):
    _inherit = "stock.quant.package"

    result_move_line_ids = fields.One2many(
        comodel_name="stock.move.line",
        inverse_name="result_package_id",
        help="Technical field. Result move lines for this package.",
    )

    @api.constrains("package_type_id")
    def _check_package_type_id_carrier_compatibility(self):
        for package in self:
            package_type = package.package_type_id
            if not package_type:
                continue
            dedicated_carriers = package_type.package_carrier_ids
            if not dedicated_carriers:
                continue
            package_carriers = package.result_move_line_ids.filtered(
                lambda ml: ml.state in ("partially_available", "assigned")
            ).picking_id.carrier_id
            if not package_carriers:
                continue
            if not all(carrier in dedicated_carriers for carrier in package_carriers):
                carrier_names = ", ".join(carrier.name for carrier in package_carriers)
                msg = _(
                    "Package type '%(package_type)s' is not valid for carriers"
                    " '%(carrier)s'."
                ) % {
                    "package_type": package_type.name,
                    "carrier": carrier_names,
                }
                raise ValidationError(msg)
