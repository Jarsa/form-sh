from odoo import api, SUPERUSER_ID


def generate_advance_records(cr):
    env = api.Environment(cr, SUPERUSER_ID, {})
    invoice_line = env['account.move.line']
    env['account.move'].search([('l10n_mx_edi_origin', '!=', False)]).l10n_mx_edi_get_related_documents()
    for company in env['res.company'].search([('partner_id.country_id', '=', env.ref('base.mx').id),
                                              ('l10n_mx_edi_product_advance_id', '!=', False)]):
        advance_product = company.l10n_mx_edi_product_advance_id
        advances = invoice_line.search([('product_id', '=', advance_product.id)]).mapped('move_id')
        advances._compute_advance_available()
        for adv in advances.filtered('l10n_mx_edi_amount_available'):
            advance = adv._l10n_mx_edi_create_advance()
            adv.l10n_mx_edi_get_related_documents()
            for rel in adv.l10n_mx_edi_related_document_ids_inverse:
                refund = rel.reversal_move_id
                if not refund:
                    continue
                rel.l10n_mx_edi_advance_ids = [(0, 0, {'advance_id': advance.id,
                                                       'amount': refund.amount_total})]
            adv._compute_advance_available()
            advance._compute_amount_total()


def migrate(cr, version):
    if not version:
        return

    generate_advance_records(cr)
