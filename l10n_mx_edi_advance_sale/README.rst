Mexican Localization EDI Advances integtration with Sales
=========================================================

This module allows managing the advances related to sales orders an easier way.
With this module you can:

- Apply the advance related from sale order to the invoice.

- Select advances in invoice if they are related with the sales orders that create the invoice.

- Select advances in invoice if they don't have any relation with a sales order.

Configure
=========

- In sales settings assign the product *'Application of advance'* that
  will be used to indicate that an document is an advance.

  .. image:: l10n_mx_edi_advance_sale/static/src/img/sales_settings.png
    :width: 500pt
    :alt: Sales settings

Usage
=====

- Advance **creation**:

  * **Create** a sales order with the products to sale and confirm it.

  * Press the button **Create invoice** in sales order and select to create a Down payment (it can be fixed amount or percentage), set the amount and click on Create Invoice.

    .. image:: l10n_mx_edi_advance_sale/static/src/img/sales_wizard_advance.png
      :width: 500pt
      :alt: Advance creation wizard

  * Validate the invoice, and register the payment. This will be the advance invoice.

- Advance **application**:

  * Go to the sales order that will be invoiced and needs to apply related advances.

  * Press the button **Create invoice** and select to create a Regular Invoice, apply the check on Deduct down payments and click on Create Invoice.

  .. image:: l10n_mx_edi_advance_sale/static/src/img/sales_wizard_advance_application.png
      :width: 500pt
      :alt: Advance application

  * The invoice will be automatically relatead to the sales order advaces.

  .. image:: l10n_mx_edi_advance_sale/static/src/img/invoice_advance_applied.png
      :width: 500pt
      :alt: Invoice with advance

  * Now you can validate and it will follow the flow of l10n_mx_edi_advance module.

Important Notes
===============

- An advance will be only selectable in invoices with lines of the sales order that creates them.
- If you create an advance with no relation with a sales order (from Invoicing), it can be selected on any invoice, no matter if it's created from a sales order or not.

For more information, you can read the `Guia de llenado Anexo20 (Apéndice 6)
<https://www.sat.gob.mx/consultas/35025/formato-de-factura-electronica-(anexo-20)>`_ or the `Use case of advances
<http://omawww.sat.gob.mx/informacion_fiscal/factura_electronica/Documents/Complementoscfdi/Caso_uso_Anticipo.pdf>`_.


Bug Tracker
===========

Bugs are tracked on
`GitLab Issues <https://git.vauxoo.com/Vauxoo/mexico/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and
welcomed feedback.

Credits
=======

**Contributors**

* Alan Ramos <alan.ramos@jarsa.com.mx>

Maintainer
==========

.. image:: https://s3.amazonaws.com/s3.vauxoo.com/description_logo.png
   :alt: Vauxoo
   :target: https://vauxoo.com
