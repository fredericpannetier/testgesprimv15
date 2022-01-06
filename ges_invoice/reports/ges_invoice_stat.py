# -*- coding: utf-8 -*-

from odoo import tools
from odoo import models, fields, api


class GesInvoiceStat(models.Model):
    _name = "ges.invoice.stat"
    _description = "Invoices Statistics"
    _auto = False
    _rec_name = 'invoice_date'
    _order = 'invoice_date desc'

    move_line_id = fields.Many2one('account.move.line', readonly=True)
    move_id = fields.Many2one('account.move', readonly=True)
    journal_id = fields.Many2one('account.journal', string='Journal', readonly=True)
    lot_id = fields.Many2one('stock.production.lot', string='Lot', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', readonly=True)
    company_currency_id = fields.Many2one('res.currency', string='Company Currency', readonly=True)
    partner_id = fields.Many2one('res.partner', string='Partner', readonly=True)
    commercial_partner_id = fields.Many2one('res.partner', string='Partner Company', help="Commercial Entity")
    country_id = fields.Many2one('res.country', string="Country")
    invoice_user_id = fields.Many2one('res.users', string='Salesperson', readonly=True)
    move_type = fields.Selection([
        ('out_invoice', 'Customer Invoice'),
        ('in_invoice', 'Vendor Bill'),
        ('out_refund', 'Customer Credit Note'),
        ('in_refund', 'Vendor Credit Note'),
        ], readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('posted', 'Open'),
        ('cancel', 'Cancelled')
        ], string='Invoice Status', readonly=True)
    payment_state = fields.Selection(selection=[
        ('not_paid', 'Not Paid'),
        ('in_payment', 'In Payment'),
        ('paid', 'paid')
    ], string='Payment Status', readonly=True)
    fiscal_position_id = fields.Many2one('account.fiscal.position', string='Fiscal Position', readonly=True)
    invoice_date = fields.Date(readonly=True, string="Invoice Date")
    quantity = fields.Float(string='Product Quantity', readonly=True)
    product_id = fields.Many2one('product.product', string='Article', readonly=True)
    product_uom_id = fields.Many2one('uom.uom', string='Unit of Measure', readonly=True)
    product_categ_id = fields.Many2one('product.category', string='Product Category', readonly=True)
    invoice_date_due = fields.Date(string='Due Date', readonly=True)
    account_id = fields.Many2one('account.account', string='Revenue/Expense Account', readonly=True, domain=[('deprecated', '=', False)])
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account', groups="analytic.group_analytic_accounting")
    price_subtotal = fields.Float(string='Untaxed Total', readonly=True)
    price_average = fields.Float(string='Average Price', readonly=True, group_operator="avg")
    purchase_qty = fields.Float(string='Purchase quantity', readonly=True)
    sale_qty = fields.Float(string='Sale quantity', readonly=True)
    purchase_pack = fields.Float(string='Purchase packages', readonly=True)
    sale_pack = fields.Float(string='Sale packages', readonly=True)
    purchase_piece = fields.Float(string='Purchase pieces', readonly=True)
    sale_piece = fields.Float(string='Sale pieces', readonly=True)
    purchase_nweight = fields.Float(string='Purchase net weight', readonly=True)
    sale_nweight = fields.Float(string='Sale net weight', readonly=True)
    # purchase_amount = fields.Float(string='Purchase amount', readonly=True)
    purchase_price = fields.Float(string='Purchase price', readonly=True)
    price_unit = fields.Float(string='Price unit', readonly=True)
    purchase_amount_for_qty_sold = fields.Float(string='Purchase amount', readonly=True)
    sale_amount = fields.Float(string='Sale amount', readonly=True)
    margin = fields.Float(string='Margin', readonly=True)
    margin_on_sales = fields.Float(string='Margin on sales', readonly=True)
    invoice_number = fields.Char(string="Invoice number", readonly=True)

    _depends = {
        'account.move': [
            'name', 'state', 'move_type', 'partner_id', 'invoice_user_id', 'fiscal_position_id',
            'invoice_date', 'invoice_date_due', 'invoice_payment_term_id', 'partner_bank_id',
        ],
        'account.move.line': [
            'quantity', 'price_subtotal', 'amount_residual', 'balance', 'amount_currency',
            'move_id', 'product_id', 'product_uom_id', 'account_id', 'analytic_account_id',
            'journal_id', 'company_id', 'currency_id', 'partner_id',
        ],
        'product.product': ['product_tmpl_id'],
        'product.template': ['categ_id'],
        'uom.uom': ['category_id', 'factor', 'name', 'uom_type'],
        'res.currency.rate': ['currency_id', 'name'],
        'res.partner': ['country_id'],
    }

    @property
    def _table_query(self):
        return '%s %s %s' % (self._select(), self._from(), self._where())

    @api.model
    def _select(self):
        return '''
            SELECT
                line.id,
                line.id as move_line_id,
                line.move_id,
                line.product_id,
                line.account_id,
                line.analytic_account_id,
                line.journal_id,
                line.company_id,
                line.company_currency_id,
                line.partner_id AS commercial_partner_id,
                move.state,
                move.name as invoice_number,
                move.move_type,
                move.partner_id,
                move.invoice_user_id,
                move.fiscal_position_id,
                move.payment_state,
                move.invoice_date,
                move.invoice_date_due,
                uom_template.id                                             AS product_uom_id,
                template.categ_id                                           AS product_categ_id,
                COALESCE(partner.country_id, commercial_partner.country_id) AS country_id,
                (case when sml_purchase.id is not null then sml_purchase.lot_id else sml_sale.lot_id end) as lot_id,
                (case when sml_purchase.id is not null then sml_purchase.qty_done else sml_sale.qty_done end) / NULLIF(COALESCE(uom_line.factor, 1) / COALESCE(uom_template.factor, 1), 0.0) * (CASE WHEN move.move_type IN ('in_invoice','out_refund','in_receipt') THEN -1 ELSE 1 END) AS quantity,
                -(line.balance * (case when sml_purchase.id is not null then sml_purchase.qty_done else sml_sale.qty_done end) / line.quantity) * currency_table.rate                         AS price_subtotal,
                -(line.balance * (case when sml_purchase.id is not null then sml_purchase.qty_done else sml_sale.qty_done end) / line.quantity) / NULLIF(COALESCE(uom_line.factor, 1) / COALESCE(uom_template.factor, 1), 0.0) * currency_table.rate AS price_average,
                
                (case when sml_purchase.id is not null then sml_purchase.qty_done else sml_sale.qty_done end) / NULLIF(COALESCE(uom_line.factor, 1) / COALESCE(uom_template.factor, 1), 0.0) * (CASE WHEN move.move_type IN ('in_invoice','out_refund','in_receipt') THEN 1 ELSE 0 END) AS purchase_qty,
                (case when sml_purchase.id is not null then sml_purchase.qty_done else sml_sale.qty_done end) / NULLIF(COALESCE(uom_line.factor, 1) / COALESCE(uom_template.factor, 1), 0.0) * (CASE WHEN move.move_type IN ('in_invoice','out_refund','in_receipt') THEN 0 ELSE 1 END) AS sale_qty,

                (case when sml_purchase.id is not null then sml_purchase.ges_pack else sml_sale.ges_pack end) * (CASE WHEN move.move_type IN ('in_invoice','out_refund','in_receipt') THEN 1 ELSE 0 END) AS purchase_pack,
                (case when sml_purchase.id is not null then sml_purchase.ges_pack else sml_sale.ges_pack end) * (CASE WHEN move.move_type IN ('in_invoice','out_refund','in_receipt') THEN 0 ELSE 1 END) AS sale_pack,
                (case when sml_purchase.id is not null then sml_purchase.ges_piece else sml_sale.ges_piece end) * (CASE WHEN move.move_type IN ('in_invoice','out_refund','in_receipt') THEN 1 ELSE 0 END) AS purchase_piece,
                (case when sml_purchase.id is not null then sml_purchase.ges_piece else sml_sale.ges_piece end) * (CASE WHEN move.move_type IN ('in_invoice','out_refund','in_receipt') THEN 0 ELSE 1 END) AS sale_piece,
                (case when sml_purchase.id is not null then sml_purchase.ges_nweight else sml_sale.ges_nweight end) * (CASE WHEN move.move_type IN ('in_invoice','out_refund','in_receipt') THEN 1 ELSE 0 END) AS purchase_nweight,
                (case when sml_purchase.id is not null then sml_purchase.ges_nweight else sml_sale.ges_nweight end) * (CASE WHEN move.move_type IN ('in_invoice','out_refund','in_receipt') THEN 0 ELSE 1 END) AS sale_nweight,
                line.price_unit as price_unit,
                line.ges_purchase_price AS purchase_price,
                line.ges_purchase_price * ((case when sml_purchase.id is not null then sml_purchase.qty_done else sml_sale.qty_done end) / NULLIF(COALESCE(uom_line.factor, 1) / COALESCE(uom_template.factor, 1), 0.0) * (CASE WHEN move.move_type IN ('in_invoice','out_refund','in_receipt') THEN 0 ELSE 1 END)) AS purchase_amount_for_qty_sold,
                -(line.balance * (case when sml_purchase.id is not null then sml_purchase.qty_done else sml_sale.qty_done end) / line.quantity) * currency_table.rate * (CASE WHEN move.move_type IN ('in_invoice','out_refund','in_receipt') THEN 0 ELSE 1 END) AS sale_amount,
                -(line.balance * (case when sml_purchase.id is not null then sml_purchase.qty_done else sml_sale.qty_done end) / line.quantity) * currency_table.rate * (CASE WHEN move.move_type IN ('in_invoice','out_refund','in_receipt') THEN 0 ELSE 1 END)+(-(line.balance * (case when sml_purchase.id is not null then sml_purchase.qty_done else sml_sale.qty_done end) / line.quantity) * currency_table.rate * (CASE WHEN move.move_type IN ('in_invoice','out_refund','in_receipt') THEN 1 ELSE 0 END)) AS margin,
                -(line.balance * (case when sml_purchase.id is not null then sml_purchase.qty_done else sml_sale.qty_done end) / line.quantity) * currency_table.rate * (CASE WHEN move.move_type IN ('in_invoice','out_refund','in_receipt') THEN 0 ELSE 1 END)-(line.ges_purchase_price * ((case when sml_purchase.id is not null then sml_purchase.qty_done else sml_sale.qty_done end) / NULLIF(COALESCE(uom_line.factor, 1) / COALESCE(uom_template.factor, 1), 0.0) * (CASE WHEN move.move_type IN ('in_invoice','out_refund','in_receipt') THEN 0 ELSE 1 END))) AS margin_on_sales
        '''

# -(line.balance * (case when sml_purchase.id is not null then sml_purchase.qty_done else sml_sale.qty_done end) / line.quantity) * currency_table.rate * (CASE WHEN move.move_type IN ('in_invoice','out_refund','in_receipt') THEN 1 ELSE 0 END) AS purchase_amount,
    @api.model
    def _from(self):
        return '''
            FROM account_move_line line
                LEFT JOIN res_partner partner ON partner.id = line.partner_id
                LEFT JOIN product_product product ON product.id = line.product_id
                LEFT JOIN account_account account ON account.id = line.account_id
                LEFT JOIN account_account_type user_type ON user_type.id = account.user_type_id
                LEFT JOIN product_template template ON template.id = product.product_tmpl_id
                LEFT JOIN uom_uom uom_line ON uom_line.id = line.product_uom_id
                LEFT JOIN uom_uom uom_template ON uom_template.id = template.uom_id
                INNER JOIN account_move move ON move.id = line.move_id
                LEFT JOIN res_partner commercial_partner ON commercial_partner.id = move.commercial_partner_id
                LEFT JOIN sale_order_line_invoice_rel ON line.id = sale_order_line_invoice_rel.invoice_line_id
                LEFT JOIN stock_move as sm_sale on sm_sale.sale_line_id = sale_order_line_invoice_rel.order_line_id and sm_sale.state='done'
                LEFT JOIN stock_move_line sml_sale on sml_sale.move_id = sm_sale.id
                LEFT JOIN stock_move as sm_purchase on sm_purchase.purchase_line_id = line.purchase_line_id and sm_purchase.state='done'
                LEFT JOIN stock_move_line sml_purchase on sml_purchase.move_id = sm_purchase.id
                JOIN {currency_table} ON currency_table.company_id = line.company_id
                JOIN (
                    -- Temporary table to decide if the qty should be added or retrieved (Invoice vs Credit Note)
                    SELECT id,(CASE
                         WHEN move.move_type::text = ANY (ARRAY['in_refund'::character varying::text, 'in_receipt'::character varying::text, 'in_invoice'::character varying::text])
                            THEN -1
                            ELSE 1
                        END) AS sign
                    FROM account_move move
                ) AS invoice_type ON invoice_type.id = move.id
        '''.format(
            currency_table=self.env['res.currency']._get_query_currency_table({'multi_company': True, 'date': {'date_to': fields.Date.today()}}),
        )

    @api.model
    def _where(self):
        return '''
            WHERE move.move_type IN ('out_invoice', 'out_refund', 'in_invoice', 'in_refund', 'out_receipt', 'in_receipt')
                AND line.account_id IS NOT NULL
                AND NOT line.exclude_from_invoice_tab
        '''
