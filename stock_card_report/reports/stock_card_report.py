import pytz
from odoo import api, fields, models


class StockCardView(models.TransientModel):
    _name = "stock.card.view"
    _description = "Stock Card View"
    _order = "date"

    date = fields.Datetime()
    product_id = fields.Many2one(comodel_name="product.product")
    product_qty = fields.Float()
    product_uom_qty = fields.Float()
    product_uom = fields.Many2one(comodel_name="uom.uom")
    reference = fields.Char()
    location_id = fields.Many2one(comodel_name="stock.location")
    location_dest_id = fields.Many2one(comodel_name="stock.location")
    is_initial = fields.Boolean()
    product_in = fields.Float()
    product_out = fields.Float()
    picking_id = fields.Many2one(comodel_name="stock.picking")

    def name_get(self):
        result = []
        for rec in self:
            name = rec.reference
            if rec.picking_id.origin:
                name = "{} ({})".format(name, rec.picking_id.origin)
            result.append((rec.id, name))
        return result


class StockCardReport(models.TransientModel):
    _name = "report.stock.card.report"
    _description = "Stock Card Report"

    # Filters fields, used for data computation
    date_from = fields.Date()
    date_to = fields.Date()
    product_ids = fields.Many2many(comodel_name="product.product")
    location_id = fields.Many2one(comodel_name="stock.location")

    # Data fields, used to browse report data
    results = fields.Many2many(
        comodel_name="stock.card.view",
        compute="_compute_results",
        help="Use compute fields, so there is nothing stored in the database",
    )

    def _compute_results(self):
        self.ensure_one()
        date_from = self.date_from or "0001-01-01"
        self.date_to = self.date_to or fields.Date.context_today(self)
        locations = self.env["stock.location"].search(
            [("id", "child_of", [self.location_id.id])]
        )
        self._cr.execute(
            """
            SELECT move.date, move.product_id, move.product_qty,
                move.product_uom_qty, move.product_uom, move.reference,
                move.location_id, move.location_dest_id,
                CASE WHEN move.location_dest_id IN %s THEN move.product_qty END AS product_in,
                CASE WHEN move.location_id IN %s THEN move.product_qty END AS product_out,
                CASE WHEN move.date < %s THEN True ELSE False END AS is_initial,
                move.picking_id
            FROM stock_move move
            WHERE (move.location_id IN %s OR move.location_dest_id IN %s)
                AND move.state = 'done' AND move.product_id IN %s
                AND CAST(move.date AS DATE) <= %s
            ORDER BY move.date, move.reference
        """,
            (
                tuple(locations.ids),
                tuple(locations.ids),
                date_from,
                tuple(locations.ids),
                tuple(locations.ids),
                tuple(self.product_ids.ids),
                self.date_to,
            ),
        )
        stock_card_results = self._cr.dictfetchall()
        user_timezone = pytz.timezone(self.env.user.tz)
        new_results = []
        for line in stock_card_results:
            line["date"] = line["date"].astimezone(user_timezone).replace(tzinfo=None)
            new_results.append(self.env["stock.card.view"].new(line).id)
        self.results = new_results

    def _get_initial(self, product_line):
        """Compute the initial balance before the date range."""
        product_input_qty = sum(product_line.mapped("product_in"))
        product_output_qty = sum(product_line.mapped("product_out"))
        return product_input_qty - product_output_qty

    def print_report(self, report_type="qweb"):
        """Trigger the report (PDF or XLSX) generation."""
        self.ensure_one()
        action = (
            report_type == "xlsx"
            and self.env.ref("stock_card_report.action_stock_card_report_xlsx")
            or self.env.ref("stock_card_report.action_stock_card_report_pdf")
        )
        return action.report_action(self, config=False)

    def _get_html(self):
        result = {}
        report = self.browse(self._context.get("active_id"))
        if report:
            context = {"o": report}
            result["html"] = self.env["ir.qweb"]._render(
                "stock_card_report.report_stock_card_report_html", context
            )
        return result

    @api.model
    def get_html(self, given_context=None):
        """Generate the HTML version of the report."""
        return self.with_context(**(given_context or {}))._get_html()
