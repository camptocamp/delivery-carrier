# Copyright 2025 Camptocamp
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import Form
from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger


class TestExcludeService(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product1 = cls.env["product.product"].create(
            {
                "name": "Product 1",
                "type": "consu",
                "is_storable": True,
                "lst_price": 1.0,
            }
        )
        cls.service1 = cls.env["product.product"].create(
            {"name": "Shipping", "type": "service"}
        )
        cls.service_affect_delivery_date = cls.env["product.product"].create(
            {"name": "Affect Delivery", "type": "service", "affect_delivery_date": True}
        )
        cls.partner = cls.env["res.partner"].create({"name": "Partner"})

        cls.sale = cls._create_sale()
        cls.sale.action_confirm()

    @classmethod
    def _create_sale(cls):
        sale_form = Form(cls.env["sale.order"])
        sale_form.partner_id = cls.partner
        with mute_logger("odoo.tests.common.onchange"):
            with sale_form.order_line.new() as line:
                line.product_id = cls.product1
                line.product_uom_qty = 10.0
            with sale_form.order_line.new() as line:
                line.product_id = cls.service1
                line.product_uom_qty = 1.0
            with sale_form.order_line.new() as line:
                line.product_id = cls.service_affect_delivery_date
                line.product_uom_qty = 1.0
        return sale_form.save()

    def test_so_line_is_delivery(self):
        """Test if SO lines are (not) considered as delivery lines correctly.

        'is_delivery' should be 'True' for SO lines:
        - with a service product with affect_delivery_date = False.
        'is_delivery' should be 'False' for SO lines:
        - with a storable product,
        - with a service product with affect_delivery_date = True.
        """
        # FORCE RECALCULATION
        self.sale.order_line._invalidate_cache()
        self.sale.order_line.read(["is_delivery"])
        self.assertRecordValues(
            self.sale.order_line,
            [
                {
                    "product_id": self.product1.id,
                    "name": "Product 1",
                    "is_delivery": False,
                },
                {
                    "product_id": self.service1.id,
                    "name": "Shipping",
                    "is_delivery": True,
                },
                {
                    "product_id": self.service_affect_delivery_date.id,
                    "name": "Affect Delivery",
                    "is_delivery": False,
                },
            ],
        )
