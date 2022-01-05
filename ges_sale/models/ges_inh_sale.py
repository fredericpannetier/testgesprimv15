# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError
from math import ceil
from odoo.tools.profiler import profile


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.onchange('product_id')
    def _ges_product_onchange(self):
        if self.product_id:
            if self.product_id.ges_packaging_id:
                self.ges_tare = self.product_id.ges_packaging_id.tare
            self.ges_brand_id = self.product_id.ges_brand_id
            self.ges_category_id = self.product_id.ges_category_id
            self.ges_origin_id = self.product_id.ges_origin_id
            self.ges_size_id = self.product_id.ges_size_id

    ges_category_id = fields.Many2one('di.multi.table', string='Category', domain=[('record_type', '=', 'category')], help="The category of the product.")
    ges_origin_id = fields.Many2one('di.multi.table', string='Origin', domain=[
                                    ('record_type', '=', 'origin')], help="The Origin of the product.")
    ges_brand_id = fields.Many2one('di.multi.table', string='Brand', domain=[
                                   ('record_type', '=', 'brand')], help="The Brand of the product.")
    ges_size_id = fields.Many2one('di.multi.table', string='Size', domain=[
                                  ('record_type', '=', 'size')], help="The Size of the product.")

    ges_pack = fields.Float(string="Number of packages",
                            help="""Number of packages""", digits=(12, 2))
    ges_piece = fields.Integer(string="Number of pieces",
                               help="""Number of pieces""")
    ges_nweight = fields.Float(string="Net weight",
                               help="""Net weight""",
                               digits='Product Unit of Measure')
    ges_gweight = fields.Float(
        string="Gross weight", help="""Gross weight""", digits='Product Unit of Measure')
    ges_tare = fields.Float(
        string="Tare", help="""Tare""", digits='Product Unit of Measure')
    ges_pack_inv = fields.Float(string="Number of packages to invoice",
                                digits=(12, 2))
    ges_piece_inv = fields.Integer(string="Number of pieces to invoice")
    ges_nweight_inv = fields.Float(string="Net weight to invoice",
                                   digits='Product Unit of Measure')
    ges_gweight_inv = fields.Float(
        string="Gross weight to invoice", help="""Gross weight to invoice""", digits='Product Unit of Measure')
    ges_tare_inv = fields.Float(
        string="Tare to invoice", help="""Tare to invoice""", digits='Product Unit of Measure')
    ges_commitment_date = fields.Datetime('Delivery Date', related='order_id.commitment_date')

    @api.onchange('product_uom_qty', 'price_unit')
    def _margin_control(self):
        if self.product_id and self.product_uom_qty:
            marg_mini = int(self.env['ir.config_parameter'].sudo(
            ).get_param('ges_base.ges_marg_mini'))
            margin = self.price_subtotal
            - (self.purchase_price * self.product_uom_qty)
            margin_percent = round((self.price_subtotal and margin
                                    / self.price_subtotal) * 100, 2)
            if marg_mini and marg_mini != 0:
                if margin_percent < marg_mini:
                    raise ValidationError(
                        _('Line margin %s %% below minimum margin %s %%' % (margin_percent, marg_mini)))

    @api.onchange('ges_pack')
    def _ges_pack_onchange(self):
        if self.product_id:
            if not self.env.context.get("noonchangepack") and self.ges_pack:
                # sauvegarde du champ pour voir si on passera
                # dans le onchange correspondant
                product_uom_qty = self.product_uom_qty
                # sauvegarde du champ pour voir si on passera
                # dans le onchange correspondant
                ges_piece = self.ges_piece
                # sauvegarde du champ pour voir si on passera
                # dans le onchange correspondant
                ges_nweight = self.ges_nweight
                ges_gweight = self.ges_gweight
                if self.product_id.ges_pob and self.product_id.ges_pob != 0:
                    self.ges_piece = self.ges_pack*self.product_id.ges_pob
                else:
                    self.ges_piece = self.ges_pack
                if self.product_uom.ges_unittype == 'Piece':
                    self.product_uom_qty = self.ges_piece
                    if self.product_id.ges_uweight:
                        self.ges_nweight = (self.product_uom_qty * self.product_id.ges_uweight)
                        self.ges_gweight = self.ges_nweight + (self.ges_tare * self.ges_pack)
                elif self.product_uom.ges_unittype == 'Package':
                    self.product_uom_qty = self.ges_pack
                    if self.product_id.ges_uweight:
                        self.ges_nweight = (self.product_uom_qty * self.product_id.ges_uweight)
                        self.ges_gweight = self.ges_nweight + (self.ges_tare * self.ges_pack)
                elif self.product_uom.ges_unittype == 'Net weight':
                    if self.product_id.ges_uweight and self.ges_piece:
                        self.ges_nweight = (self.ges_piece * self.product_id.ges_uweight)
                        self.ges_gweight = self.ges_nweight + (self.ges_tare * self.ges_pack)
                    self.product_uom_qty = self.ges_nweight
                if self.product_uom_qty != product_uom_qty:
                    # si la valeur a changé, on passe en contexte
                    # de ne pas traiter le onchange
                    self.env.context = self.with_context(noonchangeqty=True).env.context
                if self.ges_piece != ges_piece:
                    # si la valeur a changé, on passe en contexte
                    # de ne pas traiter le onchange
                    self.env.context = self.with_context(noonchangepiece=True).env.context
                if self.ges_nweight != ges_nweight:
                    # si la valeur a changé, on passe en contexte
                    # de ne pas traiter le onchange
                    self.env.context = self.with_context(noonchangeweight=True).env.context
                if self.ges_gweight != ges_gweight:
                    # si la valeur a changé, on passe en contexte de ne pas traiter le onchange
                    self.env.context = self.with_context(noonchangegweight=True).env.context
            # on rétabli le onchange dans le contexte
            self.env.context = self.with_context(noonchangepack=False).env.context

    @api.onchange('ges_piece')
    def _ges_piece_onchange(self):
        if self.product_id:
            if not self.env.context.get("noonchangepiece") and self.ges_piece:
                if self.product_uom.ges_unittype == 'Piece':
                    if self.product_uom_qty != self.ges_piece:
                        # si la valeur a changé, on passe en contexte
                        # de ne pas traiter le onchange
                        self.product_uom_qty = self.ges_piece
                        self.env.context = self.with_context(noonchangeqty=True).env.context
            # on rétabli le onchange dans le contexte
            self.env.context = self.with_context(noonchangepiece=False).env.context

    @api.onchange('ges_nweight')
    def _ges_nweight_onchange(self):
        if self.product_id:
            if not self.env.context.get("noonchangeweight") and self.ges_nweight:
                # self.ges_gweight = self.ges_nweight + (self.ges_tare * self.ges_pack)
                self.env.context = self.with_context(noonchangegweight=True).env.context
                if self.product_uom.ges_unittype == 'Net weight':
                    if self.product_uom_qty != self.ges_nweight:
                        # si la valeur a changé, on passe en contexte de ne pas traiter le onchange
                        self.product_uom_qty = self.ges_nweight
                        if self.ges_pack and self.ges_pack != 0:
                            self.ges_tare = (self.ges_gweight - self.ges_nweight) / self.ges_pack
                        else:
                            self.ges_tare = (self.ges_gweight - self.ges_nweight)
                        self.env.context = self.with_context(noonchangetare=True).env.context
                        self.env.context = self.with_context(noonchangeqty=True).env.context
            # on rétabli le onchange dans le contexte
            self.env.context = self.with_context(noonchangeweight=False).env.context


    @api.onchange('ges_gweight')
    def _ges_gweight_onchange(self):
        if self.product_id:
            if not self.env.context.get("noonchangegweight") and self.ges_gweight:
                self.ges_nweight = self.ges_gweight - (self.ges_tare * self.ges_pack)
                self.env.context = self.with_context(noonchangeweight=True).env.context
                if self.product_uom.ges_unittype == 'Net weight':
                    if self.product_uom_qty != self.ges_nweight:
                        # si la valeur a changé, on passe en contexte de ne pas traiter le onchange
                        self.product_uom_qty = self.ges_nweight
                        self.env.context = self.with_context(noonchangeqty=True).env.context

            # on rétabli le onchange dans le contexte
            self.env.context = self.with_context(noonchangegweight=False).env.context

    @api.onchange('ges_tare')
    def _ges_tare_onchange(self):
        if self.product_id:
            if (not self.env.context.get("noonchangetare")):
                if self.ges_tare:
                    self.ges_nweight = self.ges_gweight - (self.ges_tare * self.ges_pack)
                    self.env.context = self.with_context(noonchangeweight=True).env.context
                    if self.product_uom.ges_unittype == 'Net weight':
                        if self.product_uom_qty != self.ges_nweight:
                            # si la valeur a changé, on passe en contexte de ne pas traiter le onchange
                            self.product_uom_qty = self.ges_nweight
                            self.env.context = self.with_context(noonchangeqty=True).env.context
            self.env.context = self.with_context(noonchangetare=False).env.context

    @api.onchange('product_uom_qty')
    def _product_uom_qty_onchange(self):
        if self.product_id:
            if (not self.env.context.get("noonchangeqty")
               and self.product_uom_qty):
                if self.product_uom.ges_unittype == 'Piece':
                    if self.ges_piece != self.product_uom_qty:
                        # si la valeur a changé, on passe en contexte
                        # de ne pas traiter le onchange
                        self.ges_piece = self.product_uom_qty
                        self.env.context = self.with_context(noonchangepiece=True).env.context
                elif self.product_uom.ges_unittype == 'Package':
                    if self.ges_pack != self.product_uom_qty:
                        # si la valeur a changé, on passe en contexte
                        # de ne pas traiter le onchange
                        self.ges_pack = self.product_uom_qty
                        self.env.context = self.with_context(noonchangepack=True).env.context
                elif self.product_uom.ges_unittype == 'Net weight':
                    if self.ges_nweight != self.product_uom_qty:
                        # si la valeur a changé, on passe en contexte
                        # de ne pas traiter le onchange
                        self.ges_nweight = self.product_uom_qty
                        self.ges_gweight = self.ges_nweight + (self.ges_tare * self.ges_pack)
                        self.env.context = self.with_context(noonchangegweight=True).env.context
                        self.env.context = self.with_context(noonchangeweight=True).env.context
            # on rétabli le onchange dans le contexte
            self.env.context = self.with_context(noonchangeqty=False).env.context


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _prepare_confirmation_values(self):
        #copie standard
        return {
            'state': 'sale',
            # 'date_order': fields.Datetime.now()
        }

    def _default_prepdt_init(self):
        return (datetime.today().date() +
                timedelta(days=int(self.env['ir.config_parameter'].sudo().get_param('ges_base.ges_prepdelay'))))

    def _default_deliverydt_init(self):
        if self.ges_prepdt:
            prepdt = self.ges_prepdt
        else:
            prepdt = datetime.today().date()+timedelta(days=int(self.env['ir.config_parameter'].sudo().get_param('ges_base.ges_prepdelay')))

        delay = int(self.env['ir.config_parameter'].sudo().get_param('ges_base.ges_deliverydelay'))
        if self.partner_id and self.partner_id.ges_deliverydelay and self.partner_id.ges_deliverydelay > 0:
            delay = self.partner_id.ges_deliverydelay
        return (prepdt + timedelta(days=delay))

    @api.onchange('partner_id')
    def _default_copies(self):
        if self.partner_id:
            if self.partner_id.ges_order_copies:
                self.ges_copies = self.partner_id.ges_order_copies
            self.ges_deliverydt = self._default_deliverydt_init()

    ges_copies = fields.Integer(
        string="Number of copies", default=_default_copies)
    ges_prepdt = fields.Date(string="Preparation date",
                             help="""Delivery date wanted by the customer""",
                             copy=False, default=_default_prepdt_init)
    ges_deliverydt = fields.Date(
        string="Delivery date",
        help="""Delivery date wanted by the customer""",
        copy=False, default=_default_deliverydt_init)

    ges_pack = fields.Float(string="Total packages",
                            compute='_compute_ges_pack_weight_piece')
    ges_nweight = fields.Float(string="Total net weight", compute='_compute_ges_pack_weight_piece', digits=('Product Unit of Measure'))
    ges_gweight = fields.Float(string="Total gross weight", compute='_compute_ges_pack_weight_piece', digits=('Product Unit of Measure'))
    ges_piece = fields.Integer(string="Total net weight", compute='_compute_ges_pack_weight_piece')
    

    @api.depends('order_line.ges_pack', 'order_line.ges_nweight', 'order_line.ges_gweight', 'order_line.ges_piece')
    def _compute_ges_pack_weight_piece(self):
        for sol in self:
            wnbcol = sum([sol.ges_pack for sol in sol.order_line if sol.state != 'cancel'])
            wnbpiece = sum([sol.ges_piece for sol in sol.order_line if sol.state != 'cancel'])
            wpoin = sum([sol.ges_nweight for sol in sol.order_line if sol.state != 'cancel'])
            wpoib = sum([sol.ges_gweight for sol in sol.order_line if sol.state != 'cancel'])
            sol.ges_pack = wnbcol
            sol.ges_piece = wnbpiece
            sol.ges_nweight = wpoin
            sol.ges_gweight = wpoib

    @api.onchange('ges_prepdt')
    def modif_prepdt(self):
        if self.ges_prepdt:
            delay = int(self.env['ir.config_parameter'].sudo().get_param('ges_base.ges_deliverydelay'))
            if self.partner_id and self.partner_id.ges_deliverydelay and self.partner_id.ges_deliverydelay > 0:
                delay = self.partner_id.ges_deliverydelay
            self.ges_deliverydt = self.ges_prepdt + timedelta(days=delay)
            self.commitment_date = self.ges_deliverydt
            if (self.commitment_date and self.expected_date
               and self.commitment_date < self.expected_date):
                return {
                    'warning': {
                        'title': _('Requested date is too soon.'),
                        'message': _("""The delivery date is sooner than the
                        expected date."""
                                     """You may be unable to honor the
                                     delivery date.""")
                    }
                }

    @api.onchange('ges_deliverydt')
    def modif_deliverydt(self):
        if self.ges_deliverydt:
            self.commitment_date = self.ges_deliverydt
            if (self.commitment_date and self.expected_date
               and self.commitment_date < self.expected_date):
                return {
                    'warning': {
                        'title': _('Requested date is too soon.'),
                        'message': _("""The delivery date is sooner than the
                                    expected date."""
                                     """You may be unable to honor
                                     the delivery date.""")
                    }

                }
