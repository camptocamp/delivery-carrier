# Copyright 2026 Camptocamp SA (https://www.camptocamp.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import ValidationError

from odoo.addons.base.tests.common import BaseCommon
from odoo.addons.stock_picking_delivery_package_type_domain.tests.common import (
    CommonChooseDeliveryPackage,
)


class TestStockQuantPackageWrite(CommonChooseDeliveryPackage, BaseCommon):
    @classmethod
    def _create_package_for_picking_carrier(cls):
        sale = cls._create_sale()
        sale.action_confirm()
        picking = sale.picking_ids

        move_line = cls.env["stock.move.line"].create(
            {
                "product_id": cls.product.id,
                "product_uom_id": cls.product.uom_id.id,
                "picking_id": picking.id,
                "quantity": 1,
                "location_id": cls.env.ref("stock.stock_location_stock").id,
                "location_dest_id": cls.env.ref("stock.stock_location_customers").id,
            }
        )

        package = cls.env["stock.quant.package"].create({})
        move_line.result_package_id = package
        return package, picking

    def test_write_allows_package_type_without_dedicated_carrier(self):
        package, picking = self._create_package_for_picking_carrier()
        package_type = self.env["stock.package.type"].create(
            {
                "name": "No Dedicated Carrier",
                "package_carrier_type": picking.carrier_id.delivery_type,
            }
        )

        package.write({"package_type_id": package_type.id})

        self.assertEqual(package.package_type_id, package_type)

    def test_write_rejects_package_type_for_another_dedicated_carrier(self):
        package, picking = self._create_package_for_picking_carrier()
        other_carrier = self.env["delivery.carrier"].create(
            {
                "name": "Another Carrier",
                "delivery_type": picking.carrier_id.delivery_type,
                "product_id": self.product_delivery.id,
            }
        )
        package_type = self.env["stock.package.type"].create(
            {
                "name": "Other Dedicated Carrier",
                "package_carrier_type": picking.carrier_id.delivery_type,
                "package_carrier_id": other_carrier.id,
            }
        )

        with self.assertRaises(ValidationError):
            package.write({"package_type_id": package_type.id})
