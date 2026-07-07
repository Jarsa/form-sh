# -*- coding: utf-8 -*-
from odoo import api, models

# SAT minimum accepted weight for PesoBrutoTotal / PesoEnKg (kg).
MIN_CFDI_WEIGHT = 0.001


class Picking(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def _l10n_mx_edi_prepare_picking_cfdi_template(self):
        # OVERRIDES the whole chain: use the clean CartaPorte 3.1 template.
        return 'l10n_mx_edi_stock_cartaporte31_fix.cfdi_cartaporte_31'

    # -------------------------------------------------------------------------
    # ROBUST WEIGHT
    # -------------------------------------------------------------------------
    def _l10n_mx_edi_cartaporte_move_raw_weight(self, move):
        """ Best-effort weight (kg) for a single move, WITHOUT the 0.001 floor.

        Priority:
          1) move.weight if > 0 (native computed value)
          2) product.weight * quantity converted to the product's base UoM
        Returns 0.0 if neither is available (the picking-level fallback below
        will then distribute the header weight across moves).
        """
        # 1) native move weight
        weight = move.weight or 0.0
        if weight > 0:
            return weight

        # 2) product weight * qty (in product base UoM)
        product = move.product_id
        if product.weight and move.quantity:
            qty_base = move.product_uom._compute_quantity(
                move.quantity, product.uom_id, rounding_method='HALF-UP',
            )
            weight = qty_base * product.weight
            if weight > 0:
                return weight

        return 0.0

    def _l10n_mx_edi_cartaporte_weight_map(self, moves):
        """ Return {move.id: peso_kg} guaranteeing every value >= MIN_CFDI_WEIGHT.

        If some moves have no derivable weight, the picking header weight
        (shipping_weight or weight) is distributed proportionally by quantity
        across the weightless moves, so the total reflects what the user
        already captured on the picking (e.g. 302.40 kg) instead of 0.
        """
        self.ensure_one()
        raw = {m.id: self._l10n_mx_edi_cartaporte_move_raw_weight(m) for m in moves}

        missing = [m for m in moves if raw[m.id] <= 0]
        if missing:
            # Header weight the user already sees on the picking.
            header_weight = self.shipping_weight or self.weight or 0.0
            already = sum(v for v in raw.values() if v > 0)
            remaining = max(header_weight - already, 0.0)

            total_missing_qty = sum(m.quantity for m in missing) or 0.0
            for m in missing:
                if remaining > 0 and total_missing_qty > 0:
                    raw[m.id] = remaining * (m.quantity / total_missing_qty)
                # else: stays 0 -> floored below

        # Apply SAT minimum floor per move.
        return {mid: max(w, MIN_CFDI_WEIGHT) for mid, w in raw.items()}

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

        # Robust per-move weight map {move.id: kg}, never below SAT's 0.001.
        moves = cfdi_values.get('moves', self.move_ids.filtered(lambda ml: ml.quantity > 0))
        weight_map = self._l10n_mx_edi_cartaporte_weight_map(moves)
        cfdi_values['cartaporte_weight_map'] = weight_map
        cfdi_values['cartaporte_peso_bruto_total'] = max(sum(weight_map.values()), MIN_CFDI_WEIGHT)

        return cfdi_values
