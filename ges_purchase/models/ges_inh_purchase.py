# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
# from datetime import datetime, timedelta
# from odoo.exceptions import UserError, ValidationError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.onchange('partner_id')
    def _default_copies(self):
        if self.partner_id and self.partner_id.ges_order_copies:
            self.ges_copies = self.partner_id.ges_order_copies

    ges_copies = fields.Integer(
        string="Number of copies", default=_default_copies)


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    ges_category_id = fields.Many2one('di.multi.table', string='Category', domain=[
                                      ('record_type', '=', 'category')], help="The category of the product.")
    ges_origin_id = fields.Many2one('di.multi.table', string='Origin', domain=[
                                    ('record_type', '=', 'origin')], help="The Origin of the product.")
    ges_brand_id = fields.Many2one('di.multi.table', string='Brand', domain=[
                                   ('record_type', '=', 'brand')], help="The Brand of the product.")
    ges_size_id = fields.Many2one('di.multi.table', string='Size', domain=[
                                  ('record_type', '=', 'size')], help="The Size of the product.")

    ges_pack = fields.Float(string="Number of packages",
                            help="""Number of packages""", digits=(12, 2))
    ges_piece = fields.Integer(
        string="Number of pieces", help="""Number of pieces""")
    ges_nweight = fields.Float(
        string="Net weight", help="""Net weight""", digits='Product Unit of Measure')
    ges_gweight = fields.Float(
        string="Gross weight", help="""Gross weight""", digits='Product Unit of Measure')
    ges_tare = fields.Float(
        string="Tare", help="""Tare""", digits='Product Unit of Measure')
    ges_pack_inv = fields.Float(
        string="Number of packages to invoice", digits=(12, 2))
    ges_piece_inv = fields.Integer(string="Number of pieces to invoice")
    ges_nweight_inv = fields.Float(
        string="Net weight to invoice", digits='Product Unit of Measure')
    ges_gweight_inv = fields.Float(
        string="Gross weight to invoice", help="""Gross weight to invoice""", digits='Product Unit of Measure')
    ges_tare_inv = fields.Float(
        string="Tare to invoice", help="""Tare to invoice""", digits='Product Unit of Measure')

    @api.onchange('product_id')
    def _ges_product_onchange(self):
        if self.product_id:
            if self.product_id.ges_packaging_id:
                self.ges_tare = self.product_id.ges_packaging_id.tare
            self.ges_brand_id = self.product_id.ges_brand_id
            self.ges_category_id = self.product_id.ges_category_id
            self.ges_origin_id = self.product_id.ges_origin_id
            self.ges_size_id = self.product_id.ges_size_id

    @api.onchange('ges_pack')
    def _ges_pack_onchange(self):
        if self.product_id:
            if not self.env.context.get("noonchangepack") and self.ges_pack:
                # sauvegarde du champ pour voir si on passera dans le onchange correspondant
                product_qty = self.product_qty
                # sauvegarde du champ pour voir si on passera dans le onchange correspondant
                ges_piece = self.ges_piece
                # sauvegarde du champ pour voir si on passera dans le onchange correspondant
                ges_nweight = self.ges_nweight
                ges_gweight = self.ges_gweight
                
                if self.product_id.ges_pob and self.product_id.ges_pob != 0:
                    self.ges_piece = self.ges_pack*self.product_id.ges_pob
                else:
                    self.ges_piece = self.ges_pack
                if self.product_uom.ges_unittype == 'Piece':
                    self.product_qty = self.ges_piece
                    if self.product_id.ges_uweight:
                        self.ges_nweight = self.product_qty*self.product_id.ges_uweight
                        self.ges_gweight = self.ges_nweight + (self.ges_tare * self.ges_pack)
                elif self.product_uom.ges_unittype == 'Package':
                    self.product_qty = self.ges_pack
                    if self.product_id.ges_uweight:
                        self.ges_nweight = self.product_qty*self.product_id.ges_uweight
                        self.ges_gweight = self.ges_nweight + (self.ges_tare * self.ges_pack)
                elif self.product_uom.ges_unittype == 'Net weight':
                    if self.product_id.ges_uweight and self.ges_piece:
                        self.ges_nweight = self.ges_piece*self.product_id.ges_uweight
                        self.ges_gweight = self.ges_nweight + (self.ges_tare * self.ges_pack)
                    self.product_qty = self.ges_nweight
                if self.product_qty != product_qty:
                    # si la valeur a changé, on passe en contexte de ne pas traiter le onchange
                    self.env.context = self.with_context(
                        noonchangeqty=True).env.context
                if self.ges_piece != ges_piece:
                    # si la valeur a changé, on passe en contexte de ne pas traiter le onchange
                    self.env.context = self.with_context(
                        noonchangepiece=True).env.context
                if self.ges_nweight != ges_nweight:
                    # si la valeur a changé, on passe en contexte de ne pas traiter le onchange
                    self.env.context = self.with_context(
                        noonchangeweight=True).env.context
                if self.ges_gweight != ges_gweight:
                    # si la valeur a changé, on passe en contexte de ne pas traiter le onchange
                    self.env.context = self.with_context(
                        noonchangegweight=True).env.context
            # on rétabli le onchange dans le contexte
            self.env.context = self.with_context(
                noonchangepack=False).env.context

    @api.onchange('ges_piece')
    def _ges_piece_onchange(self):
        if self.product_id:
            if not self.env.context.get("noonchangepiece") and self.ges_piece:
                if self.product_uom.ges_unittype == 'Piece':
                    if self.product_qty != self.ges_piece:
                        # si la valeur a changé, on passe en contexte de ne pas traiter le onchange
                        self.product_qty = self.ges_piece
                        self.env.context = self.with_context(
                            noonchangeqty=True).env.context
            # on rétabli le onchange dans le contexte
            self.env.context = self.with_context(
                noonchangepiece=False).env.context

    @api.onchange('ges_nweight')
    def _ges_nweight_onchange(self):
        if self.product_id:
            if not self.env.context.get("noonchangeweight") and self.ges_nweight:
                # self.ges_gweight = self.ges_nweight + (self.ges_tare * self.ges_pack)
                self.env.context = self.with_context(noonchangegweight=True).env.context
                if self.product_uom.ges_unittype == 'Net weight':
                    if self.product_qty != self.ges_nweight:
                        # si la valeur a changé, on passe en contexte de ne pas traiter le onchange
                        self.product_qty = self.ges_nweight
                        self.env.context = self.with_context(
                            noonchangeqty=True).env.context
                        if self.ges_pack and self.ges_pack != 0:
                            self.ges_tare = (self.ges_gweight - self.ges_nweight) / self.ges_pack
                        else:
                            self.ges_tare = (self.ges_gweight - self.ges_nweight)
                        self.env.context = self.with_context(noonchangetare=True).env.context
            # on rétabli le onchange dans le contexte
            self.env.context = self.with_context(
                noonchangeweight=False).env.context


    @api.onchange('ges_gweight')
    def _ges_gweight_onchange(self):
        if self.product_id:
            if not self.env.context.get("noonchangegweight") and self.ges_gweight:
                self.ges_nweight = self.ges_gweight - (self.ges_tare * self.ges_pack)
                self.env.context = self.with_context(noonchangeweight=True).env.context
                if self.product_uom.ges_unittype == 'Net weight':
                    if self.product_qty != self.ges_nweight:
                        # si la valeur a changé, on passe en contexte de ne pas traiter le onchange
                        self.product_qty = self.ges_nweight
                        self.env.context = self.with_context(
                            noonchangeqty=True).env.context

            # on rétabli le onchange dans le contexte
            self.env.context = self.with_context(
                noonchangegweight=False).env.context

    @api.onchange('ges_tare')
    def _ges_tare_onchange(self):
        if self.product_id:
            if (not self.env.context.get("noonchangetare")):
                if self.ges_tare:
                    self.ges_nweight = self.ges_gweight - (self.ges_tare * self.ges_pack)
                    self.env.context = self.with_context(noonchangeweight=True).env.context
                    if self.product_uom.ges_unittype == 'Net weight':
                        if self.product_qty != self.ges_nweight:
                            # si la valeur a changé, on passe en contexte de ne pas traiter le onchange
                            self.product_qty = self.ges_nweight
                            self.env.context = self.with_context(
                                noonchangeqty=True).env.context
            self.env.context = self.with_context(noonchangetare=False).env.context

    @api.onchange('product_qty')
    def _product_qty_onchange(self):
        if self.product_id:
            if not self.env.context.get("noonchangeqty") and self.product_qty:
                if self.product_uom.ges_unittype == 'Piece':
                    if self.ges_piece != self.product_qty:
                        # si la valeur a changé, on passe en contexte de ne pas traiter le onchange
                        self.ges_piece = self.product_qty
                        self.env.context = self.with_context(
                            noonchangepiece=True).env.context
                elif self.product_uom.ges_unittype == 'Package':
                    if self.ges_pack != self.product_qty:
                        # si la valeur a changé, on passe en contexte de ne pas traiter le onchange
                        self.ges_pack = self.product_qty
                        self.env.context = self.with_context(
                            noonchangepack=True).env.context
                elif self.product_uom.ges_unittype == 'Net weight':
                    if self.ges_nweight != self.product_qty:
                        # si la valeur a changé, on passe en contexte de ne pas traiter le onchange
                        self.ges_nweight = self.product_qty
                        self.ges_gweight = self.ges_nweight + (self.ges_tare * self.ges_pack)
                        self.env.context = self.with_context(noonchangegweight=True).env.context
                        self.env.context = self.with_context(noonchangeweight=True).env.context
            # on rétabli le onchange dans le contexte
            self.env.context = self.with_context(
                noonchangeqty=False).env.context

    def _prepare_account_move_line(self, move=False):
        invoice_line = super(
            PurchaseOrderLine, self)._prepare_account_move_line(move)
        for line in self:
            ges_pack = 0.0
            ges_piece = 0
            ges_tare = 0
            ges_nweight = 0.0
            ges_gweight = 0.0
            if line.qty_received_method == 'stock_moves':
                for move in line.move_ids.filtered(lambda m: m.product_id == line.product_id):
                    if move.state == 'done':
                        if move.location_dest_id.usage == "supplier":
                            if move.to_refund:
                                ges_pack -= move.ges_pack
                                ges_piece -= move.ges_piece
                                ges_nweight -= move.ges_nweight
                                ges_gweight = ges_nweight + (ges_pack * (move.ges_tare and move.ges_tare or 0.0))
                        elif move.origin_returned_move_id and move.origin_returned_move_id._is_dropshipped() and not move._is_dropshipped_returned():
                            pass
                        elif (
                            move.location_dest_id.usage == "internal"
                            and move.to_refund
                            and move.location_dest_id
                            not in self.env["stock.location"].search(
                                [("id", "child_of", move.warehouse_id.view_location_id.id)]
                            )
                        ):
                            ges_pack -= move.ges_pack
                            ges_piece -= move.ges_piece
                            ges_nweight -= move.ges_nweight
                            ges_gweight = ges_nweight + (ges_pack * (move.ges_tare and move.ges_tare or 0.0))
                        else:
                            ges_pack += move.ges_pack
                            ges_piece += move.ges_piece
                            ges_nweight += move.ges_nweight
                            ges_gweight = ges_nweight + (ges_pack * (move.ges_tare and move.ges_tare or 0.0))
                line.ges_pack_inv = ges_pack
                line.ges_piece_inv = ges_piece
                line.ges_nweight_inv = ges_nweight
                line.ges_gweight_inv = ges_gweight
        invoice_line.update({'ges_pack': self.ges_pack_inv,
                             'ges_piece': self.ges_piece_inv,
                             'ges_nweight': self.ges_nweight_inv,
                             'ges_gweight': self.ges_gweight_inv,
                             'ges_tare': self.ges_tare,
                             'ges_category_id': self.ges_category_id,
                             'ges_origin_id': self.ges_origin_id,
                             'ges_brand_id': self.ges_brand_id,
                             'ges_size_id': self.ges_size_id,
                             'name': self.name
                             })
        return invoice_line
