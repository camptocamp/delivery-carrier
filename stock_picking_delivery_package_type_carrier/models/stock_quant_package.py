from odoo import _, models
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

    def write(self, vals):
        package_type_id = vals.get("package_type_id")
        if package_type_id:
            package_type = self.env["stock.package.type"].browse(package_type_id)
            self._check_package_type_carrier_compatibility(package_type)
        return super().write(vals)
