from odoo import _, api, models
from odoo.exceptions import ValidationError


class StockQuantPackage(models.Model):
    _inherit = "stock.quant.package"

    def _check_package_type_carrier_compatibility(self, package_type):
        dedicated_carrier = package_type.package_carrier_id
        if not dedicated_carrier:
            return

        for package in self:
            pkg_id = package.id
            domain = [
                "|",
                ("result_package_id", "=", pkg_id),
                ("package_id", "=", pkg_id),
            ]
            package_carriers = (
                self.env["stock.move.line"]
                .search(domain)
                .mapped("picking_id.carrier_id")
            )
            if not package_carriers:
                continue
            if dedicated_carrier not in package_carriers:
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
