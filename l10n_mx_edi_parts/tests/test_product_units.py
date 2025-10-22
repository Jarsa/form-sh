# Copyright 2019 Vauxoo
# License AGPL-3 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from lxml.objectify import fromstring

from odoo.tests import tagged

from odoo.addons.l10n_mx_edi_40.tests.common import TestMxEdiCommon


@tagged("post_install", "-at_install")
class TestProductUnits(TestMxEdiCommon):
    def test_product_units(self):
        self.certificate._check_credentials()
        self.product.tracking = "serial"
        self.product2 = self.product.create(
            {
                "name": "product_mx 2",
                "weight": 2,
                "uom_po_id": self.env.ref("uom.product_uom_kgm").id,
                "uom_id": self.env.ref("uom.product_uom_kgm").id,
                "lst_price": 1000.0,
                "property_account_income_id": self.company_data["default_account_revenue"].id,
                "property_account_expense_id": self.company_data["default_account_expense"].id,
                "unspsc_code_id": self.env.ref("product_unspsc.unspsc_code_01010101").id,
                "tracking": "serial",
            }
        )
        purchase = self.create_purchase()
        purchase.button_confirm()
        picking = purchase.picking_ids
        line = picking.move_ids_without_package.move_line_ids
        self.set_serial_number(line[0], 1.0, lot_name="123456")
        self.set_serial_number(line[1], 1.0, lot_name="654321")
        picking.sudo().button_validate()
        sale_order = self.create_sale_order()
        sale_order.action_confirm()
        lot = line[0].lot_id
        lot2 = line[1].lot_id
        picking = sale_order.picking_ids
        picking.move_ids_without_package.quantity_done = 1.0
        line = picking.move_ids_without_package.move_line_ids
        self.set_serial_number(line[0], 1.0, lot_id=lot.id)
        self.set_serial_number(line[1], 1.0, lot_id=lot2.id)
        picking.button_validate()
        picking.move_lines.move_line_ids.date = datetime.today() - timedelta(days=1)
        self.env["sale.advance.payment.inv"].with_context(active_ids=[sale_order.id]).create(
            {"advance_payment_method": "delivered"}
        ).create_invoices()
        invoice = sale_order.invoice_ids
        invoice.action_post()
        generated_files = self._process_documents_web_services(invoice, {"cfdi_3_3"})
        self.assertTrue(generated_files)
        self.assertEqual(invoice.edi_state, "sent", invoice.message_ids.mapped("body"))
        xml = fromstring(generated_files[0])
        self.assertEqual(len(xml.Conceptos.Concepto.Parte), 1, "Extra parts in the CFDI.")
        self.assertEqual(len(xml.Conceptos.Concepto[1].Parte), 1, "Extra parts in the CFDI.")
        self.assertEqual(
            xml.Conceptos.Concepto.Parte.attrib["NoIdentificacion"], "123456", "The product lot/serial was not added"
        )
        self.assertEqual(
            xml.Conceptos.Concepto[1].Parte.attrib["NoIdentificacion"],
            "654321",
            "The product lot/serial was not added",
        )

    def set_serial_number(self, move_line, qty, lot_id=None, lot_name=None):
        move_line.sudo().write(
            {
                "qty_done": qty,
                "lot_id": lot_id,
                "lot_name": lot_name,
            }
        )
        return move_line

    def create_purchase(self):
        purchase = (
            self.env["purchase.order"]
            .sudo()
            .create(
                {
                    "partner_id": self.partner_a.id,
                    "order_line": [
                        (
                            0,
                            0,
                            {
                                "name": self.product.name,
                                "product_id": self.product.id,
                                "product_qty": 1.0,
                                "price_unit": 100.0,
                                "date_planned": datetime.today(),
                                "product_uom": self.product.uom_id.id,
                            },
                        ),
                        (
                            0,
                            0,
                            {
                                "name": self.product.name,
                                "product_id": self.product2.id,
                                "product_qty": 1.0,
                                "price_unit": 100.0,
                                "date_planned": datetime.today(),
                                "product_uom": self.product.uom_id.id,
                            },
                        ),
                    ],
                }
            )
        )
        return purchase

    def create_sale_order(self):
        sale = (
            self.env["sale.order"]
            .sudo()
            .create(
                {
                    "partner_id": self.ref("base.res_partner_2"),
                    "order_line": [
                        (
                            0,
                            0,
                            {
                                "product_id": self.product.id,
                                "product_uom_qty": 1.0,
                                "price_unit": 100.0,
                            },
                        ),
                        (
                            0,
                            0,
                            {
                                "product_id": self.product2.id,
                                "product_uom_qty": 1.0,
                                "price_unit": 100.0,
                            },
                        ),
                    ],
                }
            )
        )
        return sale
