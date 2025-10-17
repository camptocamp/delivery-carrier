# Copyright 2020 Camptocamp
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    delivery_type = fields.Selection(
        selection_add=[("pricelist", "Based on Product Pricelist")],
        ondelete={"pricelist": "set default"},
    )
    invoice_policy = fields.Selection(
        selection_add=[("pricelist", "Delivery Product Price")],
        ondelete={"pricelist": "set default"},
        help="Estimated Cost: the customer will be invoiced the estimated"
        " cost of the shipping.\n"
        "Real Cost: the customer will be invoiced the real cost of the"
        " shipping, the cost of the shipping will be updated on the"
        " SO after the delivery.\n"
        "Delivery Product Price: the customer will be invoiced the price of the "
        "related delivery product based on the pricelist of the sales order. "
        "The provider's cost is ignored.",
    )

    def __getattribute__(self, item):
        # OVERRIDE: in case ``invoice_policy`` is set as "pricelist", we want to use
        # method ``pricelist_rate_shipment`` to retrieve the proper prices. However,
        # Odoo uses ``getattr(self, '%s_rate_shipment' % self.delivery_type)`` in its
        # base method ``rate_shipment()`` to lookup which function to use.
        # The 3 previous solutions were:
        #   1) use ``new()`` to create a temporary record with ``delivery_type`` set to
        #      pricelist => failed because comparisons among stored records and virtual
        #      records failed (eg: carrier's and shipping partner's countries comparison
        #      in ``_match_address()`` failed because virtual record's countries were
        #      assigned ``NewId`` objects instead of real ``IDs``, leading to a failure
        #      even if the countries were actually the same)
        #   2) temporarily change the ``delivery_type`` to "pricelist", compute the
        #      prices, then revert the ``delivery_type`` to its old value: that caused
        #      an ``AccessError`` if the user didn't have ``write`` access on
        #      ``delivery.carrier``, even though the user had the permission of updating
        #      the carrier on a SO w/ the proper wizard
        #   3) just like 2), but with ``sudo()`` to prevent the ``AccessError``: when
        #      updating ``delivery_type``, Odoo triggers a series of recomputations that
        #      will modify other fields, which is an unwanted side effect that cannot
        #      always be reverted when ``delivery_type`` is reverted to its original
        #      value (eg: see method ``_compute_can_generate_return()``)
        # Overriding ``__getattribute__()`` might seem overkill, but it seems to be one
        # of the few remaining feasible options.
        if (
            # ⚠️ The first check may seem redundant, given the other ones;
            # however, without this, Python will crash with a ``RecursionError``,
            # because it'll try to access the fields we need for the check, and before
            # being able to read their value, it'll enter again the ``__getattribute__``
            # override, so it'll try to access the fields we need for the check again,
            # and so on, entering an infinite loophole
            item.endswith("_rate_shipment")
            and self.invoice_policy == "pricelist"
            and (delivery_type := self.delivery_type) != "pricelist"
            and item == f"{delivery_type}_rate_shipment"
        ):
            item = "pricelist_rate_shipment"
        return super().__getattribute__(item)

    def send_shipping(self, pickings):
        result = super().send_shipping(pickings)
        if self.invoice_policy == "pricelist":
            # force computation from pricelist when the invoicing policy says
            # so
            rates = self.pricelist_send_shipping(pickings)
            for index, rate in enumerate(rates):
                result[index]["exact_price"] = rate["exact_price"]
        return result

    def _pricelist_get_price(self, order):
        product_price = order.pricelist_id._get_product_price(
            self.product_id,
            1.0,
            uom=self.product_id.uom_id,
            date=order.date_order,
        )
        price = order.currency_id._convert(
            product_price,
            order.company_id.currency_id,
            order.company_id,
            order.date_order or fields.Date.today(),
        )
        return price

    def pricelist_rate_shipment(self, order):
        carrier = self._match_address(order.partner_shipping_id)
        if not carrier:
            return {
                "success": False,
                "price": 0.0,
                "error_message": self.env._(
                    "Error: this delivery method is not available for this address."
                ),
                "warning_message": False,
            }
        price = self._pricelist_get_price(order)
        return {
            "success": True,
            "price": price,
            "error_message": False,
            "warning_message": False,
        }

    def pricelist_send_shipping(self, pickings):
        res = []
        for picking in pickings:
            carrier = picking.carrier_id
            sale = picking.sale_id
            price = carrier._pricelist_get_price(sale) if sale else 0.0
            res = res + [{"exact_price": price, "tracking_number": False}]
        return res

    def pricelist_get_tracking_link(self, picking):
        return False

    def pricelist_cancel_shipment(self, pickings):
        raise NotImplementedError()

    @api.model
    def _get_view(self, view_id=None, view_type="form", **options):
        arch, view = super()._get_view(
            view_id=view_id, view_type=view_type, options=options
        )
        if view.name == "delivery.carrier.form":
            arch = self._fields_view_get_adapt_attrs(arch)
        return arch, view

    @property
    def attrs_list(self):
        return ["invisible", "required", "readonly"]

    def _add_pricelist_domain(
        self,
        doc,
        xpath_expr,
        attrs_key,
        domain_operator="or",
        field_operator="==",
    ):
        """Add the delivery type domain for 'pricelist' in attrs"""

        if attrs_key not in self.attrs_list:
            return

        nodes = doc.xpath(xpath_expr)
        for field in nodes:
            domain = field.attrib.get(attrs_key, "")
            if not domain:
                continue

            delivery_type_domain = f"delivery_type {field_operator} 'pricelist'"
            domain = f"{domain} {domain_operator} {delivery_type_domain}"
            field.set(attrs_key, domain)

    def _fields_view_get_adapt_attrs(self, view_arch):
        """Adapt the attrs of elements in the view with 'pricelist' delivery type"""
        # hide all these fields and buttons for delivery providers which have already
        # an attrs with a domain we can't extend...
        self._add_pricelist_domain(
            view_arch, "//button[@name='toggle_prod_environment']", "invisible"
        )
        self._add_pricelist_domain(
            view_arch, "//button[@name='toggle_debug']", "invisible"
        )
        self._add_pricelist_domain(
            view_arch, "//field[@name='integration_level']", "invisible"
        )
        self._add_pricelist_domain(
            view_arch, "//field[@name='invoice_policy']", "invisible"
        )

        return view_arch
