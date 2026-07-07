# -*- coding: utf-8 -*-
from odoo import api, models


class Picking(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def _l10n_mx_edi_prepare_picking_cfdi_template(self):
        # OVERRIDES the whole chain: use the clean CartaPorte 3.1 template.
        return 'l10n_mx_edi_stock_cartaporte31_fix.cfdi_cartaporte_31'

    def _l10n_mx_edi_add_picking_cfdi_values(self, cfdi_values):
        # EXTENDS the chain. Everything (origen/destino/domicilio/idccp/peso/
        # regimenes_aduanero/tipo_documento/...) is already built upstream.
        # Here we only guarantee the keys the CartaPorte31 template reads are
        # always present, so QWeb never raises on a missing key.
        super()._l10n_mx_edi_add_picking_cfdi_values(cfdi_values)

        # Colonia: the upstream _add_domicilio only fills a subset; make sure the
        # colony code is available for both endpoints (required attribute in 3.1).
        warehouse_partner = self.picking_type_id.warehouse_id.partner_id
        origin_partner = self.partner_id if self.picking_type_code == 'incoming' else warehouse_partner
        destination_partner = self.partner_id if self.picking_type_code == 'outgoing' else warehouse_partner
        if cfdi_values.get('origen', {}).get('domicilio') is not None:
            cfdi_values['origen']['domicilio'].setdefault('colonia', origin_partner.l10n_mx_edi_colony_code)
        if cfdi_values.get('destino', {}).get('domicilio') is not None:
            cfdi_values['destino']['domicilio'].setdefault('colonia', destination_partner.l10n_mx_edi_colony_code)

        # entrada_salida_merc / via_entrada_salida: only set upstream for COMEX.
        # Default them so the template can reference them unconditionally.
        cfdi_values.setdefault('entrada_salida_merc', None)

        # regimenes_aduanero: extended_31 already provides this list for COMEX.
        # Guarantee it exists (empty list -> no RegimenesAduaneros node emitted).
        cfdi_values.setdefault('regimenes_aduanero', [])

        # COMEX doc keys referenced by DocumentacionAduanera.
        cfdi_values.setdefault('tipo_documento', None)
        cfdi_values.setdefault('num_pedimento', None)
        cfdi_values.setdefault('ident_doc_aduanero', None)
        cfdi_values.setdefault('rfc_impo', None)

        return cfdi_values
