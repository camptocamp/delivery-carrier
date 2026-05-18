# Copyright 2026 Camptocamp SA (https://www.camptocamp.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import Command

from odoo.addons.base.tests.common import BaseCommon
from odoo.addons.stock_picking_delivery_package_type_domain.tests.common import (
    CommonChooseDeliveryPackage,
)


class TestChooseDeliveryPackageType(CommonChooseDeliveryPackage, BaseCommon):
    def test_domain_gets_correct_package_type(self):
        sale = self._create_sale()
        sale.action_confirm()
        self.assertTrue(sale.picking_ids)
        carrier = sale.picking_ids.carrier_id
        res = sale.picking_ids.action_put_in_pack()
        model = res.get("res_model")
        context = res.get("context")
        self.assertEqual("choose.delivery.package", model)
        self.wizard = self.env[model].with_context(**context).create({})
        self.assertTrue(self.wizard)
        self.assertEqual(
            self.wizard.package_type_domain,
            [
                "|",
                ("package_carrier_ids", "=", False),
                ("package_carrier_ids", "in", [carrier.id]),
            ],
        )

    def test_domain_excludes_package_types_of_other_carriers(self):
        sale = self._create_sale()
        sale.action_confirm()
        self.assertTrue(sale.picking_ids)

        picking = sale.picking_ids
        carrier = picking.carrier_id

        # package type selectable for this picking
        matching_type = self.env["stock.package.type"].create(
            {
                "name": "Type Matching Carrier",
                "package_carrier_type": carrier.delivery_type,
                "package_carrier_ids": [Command.set([carrier.id])],
            }
        )

        # same carrier type with different dedicated carrier must be excluded
        other_carrier = self.env["delivery.carrier"].create(
            {
                "name": "Other Test Carrier",
                "delivery_type": carrier.delivery_type,
                "product_id": self.product_delivery.id,
            }
        )
        excluded_type = self.env["stock.package.type"].create(
            {
                "name": "Type Other Carrier",
                "package_carrier_type": carrier.delivery_type,
                "package_carrier_ids": [Command.set([other_carrier.id])],
            }
        )

        res = picking.action_put_in_pack()
        wizard_model = res.get("res_model")
        wizard_context = res.get("context")
        wizard = self.env[wizard_model].with_context(**wizard_context).create({})

        package_types = self.env["stock.package.type"].search(
            wizard.package_type_domain
        )
        self.assertIn(matching_type, package_types)
        self.assertNotIn(excluded_type, package_types)

    def test_domain_without_carrier_keeps_parent_domain(self):
        sale = self._create_sale()
        sale.action_confirm()
        self.assertTrue(sale.picking_ids)

        picking = sale.picking_ids
        picking.carrier_id = False

        wizard = (
            self.env["choose.delivery.package"]
            .with_context(
                default_picking_id=picking.id,
                current_package_carrier_type="none",
            )
            .create({})
        )

        self.assertEqual(
            [("package_carrier_type", "=", "none")],
            wizard.package_type_domain,
        )
