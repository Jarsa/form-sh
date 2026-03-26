# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import models

_logger = logging.getLogger(__name__)


def _is_mx(record):
    """Devuelve True si el registro pertenece a una empresa mexicana."""
    return record.company_id.country_id == record.env.ref("base.mx")


class AccountFullReconcile(models.Model):
    _inherit = "account.full.reconcile"

    def unlink(self):
        """Al borrar una conciliación total, desvincula el asiento de
        diferencia cambiaria (FX) para evitar que quede huérfano en empresas MX.
        """
        mxn_moves = (
            self.mapped("reconciled_line_ids")
            .filtered(_is_mx)
            .mapped("full_reconcile_id")
        )
        if mxn_moves:
            _logger.debug(
                "Desvinculando exchange_move_id de %d conciliación(es) MX antes de eliminar.",
                len(mxn_moves),
            )
            mxn_moves.write({"exchange_move_id": False})
        return super().unlink()


class AccountPartialReconcile(models.Model):
    _inherit = "account.partial.reconcile"

    def unlink(self):
        """Al borrar una conciliación parcial en empresas MX, elimina en orden
        correcto toda la cadena de asientos derivados:
          - Asientos de diferencia cambiaria (FX)
          - Asientos de IVA en efectivo (CABA)
          - Asientos FX generados por los propios CABA
        para evitar asientos huérfanos que contaminen la contabilidad.
        """
        mxn_moves = self.filtered(_is_mx)

        # Procesar conciliaciones de empresas NO-MX con el flujo estándar
        res = super(AccountPartialReconcile, self - mxn_moves).unlink()

        if not mxn_moves:
            return res

        _logger.debug(
            "Iniciando limpieza de asientos derivados para %d conciliación(es) parcial(es) MX.",
            len(mxn_moves),
        )

        move_obj = self.env["account.move"]
        partial_to_unlink = mxn_moves

        # 1. Conciliaciones totales vinculadas a las parciales MX
        afr_ids = mxn_moves.mapped("full_reconcile_id")

        # 2. Asientos FX generados al momento de la conciliación
        fx_move_ids = afr_ids.mapped("exchange_move_id")
        fx_apr_ids = (
            fx_move_ids.mapped("line_ids.matched_debit_ids")
            | fx_move_ids.mapped("line_ids.matched_credit_ids")
        )

        # 3. Asientos CABA generados por los asientos FX
        caba_fx_move_ids = move_obj.search([("tax_cash_basis_rec_id", "in", fx_apr_ids.ids)])
        caba_fx_apr_ids = (
            caba_fx_move_ids.mapped("line_ids.matched_debit_ids")
            | caba_fx_move_ids.mapped("line_ids.matched_credit_ids")
        )
        caba_fx_afr_ids = caba_fx_move_ids.mapped("line_ids.full_reconcile_id")

        # 4. Asientos FX generados por los CABA de FX
        fx_caba_fx_move_ids = caba_fx_afr_ids.mapped("exchange_move_id")
        fx_caba_fx_apr_ids = (
            fx_caba_fx_move_ids.mapped("line_ids.matched_debit_ids")
            | fx_caba_fx_move_ids.mapped("line_ids.matched_credit_ids")
        )

        # 5. Asientos CABA generados directamente por las conciliaciones parciales
        caba_move_ids = move_obj.search([("tax_cash_basis_rec_id", "in", partial_to_unlink.ids)])
        caba_afr_ids = caba_move_ids.mapped("line_ids.full_reconcile_id")
        caba_apr_ids = (
            caba_move_ids.mapped("line_ids.matched_debit_ids")
            | caba_move_ids.mapped("line_ids.matched_credit_ids")
        )

        # 6. Asientos FX generados por los CABA directos
        fx_caba_move_ids = caba_afr_ids.mapped("exchange_move_id")
        fx_caba_apr_ids = (
            fx_caba_move_ids.mapped("line_ids.matched_debit_ids")
            | fx_caba_move_ids.mapped("line_ids.matched_credit_ids")
        )

        # --- Eliminación en orden correcto (de hijos a padres) ---

        # Primero las conciliaciones totales (AFR) para liberar las referencias
        full_to_unlink = afr_ids | caba_fx_afr_ids | caba_afr_ids
        if full_to_unlink:
            _logger.debug("Eliminando %d conciliación(es) total(es) derivadas.", len(full_to_unlink))
            full_to_unlink.unlink()

        # Luego las conciliaciones parciales (APR) derivadas
        partial_to_unlink = (
            partial_to_unlink
            | fx_apr_ids
            | caba_fx_apr_ids
            | fx_caba_fx_apr_ids
            | caba_apr_ids
            | fx_caba_apr_ids
        )
        if partial_to_unlink:
            _logger.debug("Eliminando %d conciliación(es) parcial(es) derivadas.", len(partial_to_unlink))
            super(models.Model, partial_to_unlink).unlink()

        # Finalmente cancelar y borrar todos los asientos contables auxiliares
        move_ids = (
            fx_move_ids
            | caba_fx_move_ids
            | fx_caba_fx_move_ids
            | caba_move_ids
            | fx_caba_move_ids
        )
        if move_ids:
            _logger.debug(
                "Cancelando y eliminando %d asiento(s) contable(s) auxiliar(es) (FX/CABA).",
                len(move_ids),
            )
            move_ids.button_cancel()
            move_ids.with_context(force_delete=True).unlink()

        _logger.debug("Limpieza de asientos derivados MX completada.")
        return res
