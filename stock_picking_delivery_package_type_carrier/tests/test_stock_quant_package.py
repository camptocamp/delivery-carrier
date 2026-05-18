# Copyright 2026 Camptocamp SA (https://www.camptocamp.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import Command
from odoo.exceptions import ValidationError

from odoo.addons.base.tests.common import BaseCommon
from odoo.addons.stock_picking_delivery_package_type_domain.tests.common import (
    CommonChooseDeliveryPackage,
)


class TestStockQuantPackageConstraint(CommonChooseDeliveryPackage, BaseCommon):
    def _create_package_for_picking_carrier(self):
        sale = self._create_sale()
        sale.action_confirm()
        picking = sale.picking_ids

        move_line = self.env["stock.move.line"].create(
            {
                "product_id": self.product.id,
                "product_uom_id": self.product.uom_id.id,
                "picking_id": picking.id,
                "quantity": 1,
                "location_id": self.env.ref("stock.stock_location_stock").id,
                "location_dest_id": self.env.ref("stock.stock_location_customers").id,
            }
        )

        package = self.env["stock.quant.package"].create({})
        move_line.result_package_id = package
        return package, picking

    def test_constraint_allows_package_type_without_dedicated_carrier(self):
        package, picking = self._create_package_for_picking_carrier()
        package_type = self.env["stock.package.type"].create(
            {
                "name": "No Dedicated Carrier",
                "package_carrier_type": picking.carrier_id.delivery_type,
            }
        )

        package.write({"package_type_id": package_type.id})
        self.assertEqual(package.package_type_id, package_type)

    def test_constraint_rejects_package_type_for_another_dedicated_carrier(self):
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
                "package_carrier_ids": [Command.set([other_carrier.id])],
            }
        )

        with self.assertRaises(ValidationError):
            package.write({"package_type_id": package_type.id})

    def test_constraint_rejects_package_type_when_not_valid_for_all_carriers(self):
        package, picking = self._create_package_for_picking_carrier()
        carrier_a = picking.carrier_id

        carrier_b = self.env["delivery.carrier"].create(
            {
                "name": "Carrier B",
                "delivery_type": carrier_a.delivery_type,
                "product_id": self.product_delivery.id,
            }
        )

        # create a second picking with carrier B and link the same package
        picking2 = self.env["stock.picking"].create(
            {
                "picking_type_id": picking.picking_type_id.id,
                "location_id": self.env.ref("stock.stock_location_stock").id,
                "location_dest_id": self.env.ref("stock.stock_location_customers").id,
                "carrier_id": carrier_b.id,
            }
        )
        move_line2 = self.env["stock.move.line"].create(
            {
                "product_id": self.product.id,
                "product_uom_id": self.product.uom_id.id,
                "picking_id": picking2.id,
                "quantity": 1,
                "location_id": self.env.ref("stock.stock_location_stock").id,
                "location_dest_id": self.env.ref("stock.stock_location_customers").id,
            }
        )
        move_line2.result_package_id = package

        # package type is dedicated to carrier_a only, not carrier B
        package_type = self.env["stock.package.type"].create(
            {
                "name": "Carrier A Only",
                "package_carrier_type": carrier_a.delivery_type,
                "package_carrier_ids": [Command.set([carrier_a.id])],
            }
        )

        with self.assertRaises(ValidationError):
            package.write({"package_type_id": package_type.id})
