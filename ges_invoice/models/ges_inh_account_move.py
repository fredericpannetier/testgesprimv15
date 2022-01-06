# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.onchange('partner_id')
    def _default_copies(self):
        if self.partner_id and self.partner_id.ges_inv_copies:
            self.ges_copies = self.partner_id.ges_inv_copies

    @api.model
    def _move_autocomplete_invoice_lines_create(self, vals_list):
        # copie standard
        ''' During the create of an account.move with only 'invoice_line_ids' set and not 'line_ids', this method is called
        to auto compute accounting lines of the invoice. In that case, accounts will be retrieved and taxes, cash rounding
        and payment terms will be computed. At the end, the values will contains all accounting lines in 'line_ids'
        and the moves should be balanced.

        :param vals_list:   The list of values passed to the 'create' method.
        :return:            Modified list of values.
        '''
        new_vals_list = []
        for vals in vals_list:
            if not vals.get('invoice_line_ids'):
                new_vals_list.append(vals)
                continue
# modif pour toujours mettre à jour avec les données saisies
#             if vals.get('line_ids'):
#                 vals.pop('invoice_line_ids', None)
#                 new_vals_list.append(vals)
#                 continue
# fin modif
            if not vals.get('move_type') and not self._context.get('default_move_type'):
                vals.pop('invoice_line_ids', None)
                new_vals_list.append(vals)
                continue
            vals['move_type'] = vals.get(
                'move_type', self._context.get('default_move_type', 'entry'))
            if not vals['move_type'] in self.get_invoice_types(include_receipts=True):
                new_vals_list.append(vals)
                continue

            vals['line_ids'] = vals.pop('invoice_line_ids')

            if vals.get('invoice_date') and not vals.get('date'):
                vals['date'] = vals['invoice_date']

            ctx_vals = {'default_move_type': vals.get(
                'move_type') or self._context.get('default_move_type')}
            if vals.get('currency_id'):
                ctx_vals['default_currency_id'] = vals['currency_id']
            if vals.get('journal_id'):
                ctx_vals['default_journal_id'] = vals['journal_id']
                # reorder the companies in the context so that the company of the journal
                # (which will be the company of the move) is the main one, ensuring all
                # property fields are read with the correct company
                journal_company = self.env['account.journal'].browse(
                    vals['journal_id']).company_id
                allowed_companies = self._context.get(
                    'allowed_company_ids', journal_company.ids)
                reordered_companies = sorted(
                    allowed_companies, key=lambda cid: cid != journal_company.id)
                ctx_vals['allowed_company_ids'] = reordered_companies
            self_ctx = self.with_context(**ctx_vals)
            new_vals = self_ctx._add_missing_default_values(vals)

            move = self_ctx.new(new_vals)
            new_vals_list.append(
                move._move_autocomplete_invoice_lines_values())

        return new_vals_list

    def _move_autocomplete_invoice_lines_write(self, vals):
        # copie standard
        ''' During the write of an account.move with only 'invoice_line_ids' set and not 'line_ids', this method is called
        to auto compute accounting lines of the invoice. In that case, accounts will be retrieved and taxes, cash rounding
        and payment terms will be computed. At the end, the values will contains all accounting lines in 'line_ids'
        and the moves should be balanced.

        :param vals_list:   A python dict representing the values to write.
        :return:            True if the auto-completion did something, False otherwise.

        '''
        # modif pour toujours mettre à jour avec les données saisies
        if not vals.get('invoice_line_ids'):
            return False
#         enable_autocomplete = 'invoice_line_ids' in vals and 'line_ids' not in vals and True or False
#
#         if not enable_autocomplete:
#             return False
        # fin modif

        vals['line_ids'] = vals.pop('invoice_line_ids')
        for invoice in self:
            invoice_new = invoice.with_context(
                default_move_type=invoice.move_type, default_journal_id=invoice.journal_id.id).new(origin=invoice)
            invoice_new.update(vals)
            values = invoice_new._move_autocomplete_invoice_lines_values()
            values.pop('invoice_line_ids', None)
            invoice.write(values)
        return True

    @api.depends('line_ids')
    def _compute_one_lot(self):
        for move in self:
            move.ges_one_lot = True
            for line in move.line_ids:
                if not line.ges_one_lot:
                    move.ges_one_lot = False
                    break

    ges_one_lot = fields.Boolean("Only one lot by line", compute="_compute_one_lot")

    ges_copies = fields.Integer(
        string="Number of copies", default=_default_copies)

    @api.model
    def create(self, vals):
        res = super(AccountMove, self).create(vals)
        for am in res:
            if am.ges_copies == 0 or not am.ges_copies:
                if am.partner_id:
                    am.write({'ges_copies': am.partner_id.ges_inv_copies})
        return res


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.onchange('ges_pack')
    def _ges_pack_onchange(self):
        if self.product_id:
            if not self.env.context.get("noonchangepack") and self.ges_pack:
                # sauvegarde du champ pour voir si on passera dans le onchange correspondant
                quantity = self.quantity
                # sauvegarde du champ pour voir si on passera dans le onchange correspondant
                ges_piece = self.ges_piece
                # sauvegarde du champ pour voir si on passera dans le onchange correspondant
                ges_nweight = self.ges_nweight
                ges_gweight = self.ges_gweight
                if self.product_id.ges_pob and self.product_id.ges_pob != 0:
                    self.ges_piece = self.ges_pack*self.product_id.ges_pob
                else:
                    self.ges_piece = self.ges_pack
                if self.product_uom_id.ges_unittype == 'Piece':
                    self.quantity = self.ges_piece
                    if self.product_id.ges_uweight:
                        self.ges_nweight = self.quantity*self.product_id.ges_uweight
                        self.ges_gweight = self.ges_nweight + (self.ges_tare * self.ges_pack)
                elif self.product_uom_id.ges_unittype == 'Package':
                    self.quantity = self.ges_pack
                    if self.product_id.ges_uweight:
                        self.ges_nweight = self.quantity*self.product_id.ges_uweight
                        self.ges_gweight = self.ges_nweight + (self.ges_tare * self.ges_pack)
                elif self.product_uom_id.ges_unittype == 'Net weight':
                    if self.product_id.ges_uweight and self.ges_piece:
                        self.ges_nweight = self.ges_piece*self.product_id.ges_uweight
                        self.ges_gweight = self.ges_nweight + (self.ges_tare * self.ges_pack)
                    self.quantity = self.ges_nweight
                if self.quantity != quantity:
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
                if self.product_uom_id.ges_unittype == 'Piece':
                    if self.quantity != self.ges_piece:
                        # si la valeur a changé, on passe en contexte de ne pas traiter le onchange
                        self.quantity = self.ges_piece
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
                if self.product_uom_id.ges_unittype == 'Net weight':
                    if self.quantity != self.ges_nweight:
                        # si la valeur a changé, on passe en contexte de ne pas traiter le onchange
                        self.quantity = self.ges_nweight
                        self.env.context = self.with_context(
                            noonchangeqty=True).env.context
            # on rétabli le onchange dans le contexte
            self.env.context = self.with_context(
                noonchangeweight=False).env.context


    @api.onchange('ges_gweight')
    def _ges_gweight_onchange(self):
        if self.product_id:
            if not self.env.context.get("noonchangegweight") and self.ges_gweight:
                self.ges_nweight = self.ges_gweight - (self.ges_tare * self.ges_pack)
                self.env.context = self.with_context(noonchangeweight=True).env.context
                if self.product_uom_id.ges_unittype == 'Net weight':
                    if self.quantity != self.ges_nweight:
                        # si la valeur a changé, on passe en contexte de ne pas traiter le onchange
                        self.quantity = self.ges_nweight
                        self.env.context = self.with_context(
                            noonchangeqty=True).env.context
                        if self.ges_pack and self.ges_pack != 0:
                            self.ges_tare = (self.ges_gweight - self.ges_nweight) / self.ges_pack
                        else:
                            self.ges_tare = (self.ges_gweight - self.ges_nweight)
                        self.env.context = self.with_context(noonchangetare=True).env.context

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
                    if self.product_uom_id.ges_unittype == 'Net weight':
                        if self.quantity != self.ges_nweight:
                            # si la valeur a changé, on passe en contexte de ne pas traiter le onchange
                            self.quantity = self.ges_nweight
                            self.env.context = self.with_context(
                                noonchangeqty=True).env.context
            self.env.context = self.with_context(noonchangetare=False).env.context

    @api.onchange('quantity')
    def _product_uom_qty_onchange(self):
        if self.product_id:
            if not self.env.context.get("noonchangeqty") and self.quantity:
                if self.product_uom_id.ges_unittype == 'Piece':
                    if self.ges_piece != self.quantity:
                        # si la valeur a changé, on passe en contexte de ne pas traiter le onchange
                        self.ges_piece = self.quantity
                        self.env.context = self.with_context(
                            noonchangepiece=True).env.context
                elif self.product_uom_id.ges_unittype == 'Package':
                    if self.ges_pack != self.quantity:
                        # si la valeur a changé, on passe en contexte de ne pas traiter le onchange
                        self.ges_pack = self.quantity
                        self.env.context = self.with_context(
                            noonchangepack=True).env.context
                elif self.product_uom_id.ges_unittype == 'Net weight':
                    if self.ges_nweight != self.quantity:
                        # si la valeur a changé, on passe en contexte de ne pas traiter le onchange
                        self.ges_nweight = self.quantity
                        self.ges_gweight = self.ges_nweight + (self.ges_tare * self.ges_pack)
                        self.env.context = self.with_context(noonchangegweight=True).env.context
                        self.env.context = self.with_context(noonchangeweight=True).env.context
            # on rétabli le onchange dans le contexte
            self.env.context = self.with_context(
                noonchangeqty=False).env.context

    @api.depends('sale_line_ids.qty_delivered', 'sale_line_ids.move_ids', 'purchase_line_id.qty_received', 'purchase_line_id.move_ids')
    def _compute_ges_lots(self):
        # récapitule les quantités par lot, livrées pour cette ligne de facture
        ges_inv_lot = self.env['ir.config_parameter'].sudo().get_param('ges_base.ges_inv_lot')
        for move_line in self:
            move_line.ges_one_lot = True
            res = {}
            if move_line.sale_line_ids:
                for sol in move_line.sale_line_ids:
                    for sm in sol.move_ids:
                        if sm.state == 'done':
                            for sml in sm.move_line_ids:
                                lot = self.env['stock.production.lot']
                                qty = 0.0
                                if sm.location_dest_id.usage == "customer":
                                    if not sm.origin_returned_move_id or (sm.origin_returned_move_id and sm.to_refund):
                                        lot = sml.lot_id
                                        qty = sml.qty_done
                                elif sm.location_dest_id.usage != "customer" and sm.to_refund:
                                    lot = sml.lot_id
                                    qty = sml.qty_done*-1
                                if lot in res:
                                    res[lot] += qty
                                else:
                                    res[lot] = qty
            elif move_line.purchase_line_id:
                for sm in move_line.purchase_line_id.move_ids:
                    if sm.state == 'done':
                        for sml in sm.move_line_ids:
                            lot = self.env['stock.production.lot']
                            qty = 0.0
                            if sm.location_dest_id.usage == "internal":
                                if not sm.origin_returned_move_id or (sm.origin_returned_move_id and sm.to_refund):
                                    lot = sml.lot_id
                                    qty = sml.qty_done
                            elif sm.location_dest_id.usage != "internal" and sm.to_refund:
                                lot = sml.lot_id
                                qty = sml.qty_done*-1
                            if lot in res:
                                res[lot] += qty
                            else:
                                res[lot] = qty

            res = sorted(res.items(), key=lambda l: l[0].create_date)
            if res:
                if ges_inv_lot == 'first':
                    for lot, qty in res:
                        move_line.ges_one_lot = True
                        move_line.ges_lots = [(lot.name, move_line.quantity)]
                        break
                else:
                    move_line.ges_lots = [(
                        lot.name, qty
                    ) for lot, qty in res]
                    first = True
                    for lot, qty in move_line.ges_lots:
                        if first:
                            move_line.ges_one_lot = True
                            first = False
                        else:
                            move_line.ges_one_lot = False
                            break
            else:
                move_line.ges_lots = []
                move_line.ges_one_lot = True

    @api.onchange('product_id')
    def _ges_product_onchange(self):
        if self.product_id:
            if self.product_id.ges_packaging_id:
                self.ges_tare = self.product_id.ges_packaging_id.tare
            self.ges_brand_id = self.product_id.ges_brand_id
            self.ges_category_id = self.product_id.ges_category_id
            self.ges_origin_id = self.product_id.ges_origin_id
            self.ges_size_id = self.product_id.ges_size_id

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
    ges_lots = fields.Binary(
        string="Lots on the invoice line", compute="_compute_ges_lots")
    ges_one_lot = fields.Boolean("Only one lot on the line", compute="_compute_ges_lots")
    ges_purchase_price = fields.Float(string='Cost', digits='Product Price')

#     def write(self, vals):
#         res = AccountMoveLine.write(self, vals)
#         return res
#
#     @api.model_create_multi
#     @api.returns('self', lambda value:value.id)
#     def create(self, vals_list):
#         res = AccountMoveLine.create(self, vals_list)
#         return res
