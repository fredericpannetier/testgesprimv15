# -*- coding: utf-8 -*-

from odoo import _, api, fields, models


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    ges_pack = fields.Float(string="Number of packages", help="""Number of packages""", digits=(
        12, 2), compute="_ges_compute_value", store=True)
    ges_piece = fields.Integer(string="Number of pieces", help="""Number of pieces""", compute="_ges_compute_value", store=True)
    ges_nweight = fields.Float(string="Net weight", help="""Net weight""", digits='Product Unit of Measure', compute="_ges_compute_value", store=True)

    ges_pack_tot = fields.Float(string="Number of packages", help="""Number of packages""", digits=(12, 2), compute="_ges_compute_tot_value")
    ges_piece_tot = fields.Integer(string="Number of pieces", help="""Number of pieces""", compute="_ges_compute_tot_value")
    ges_nweight_tot = fields.Float(string="Net weight", help="""Net weight""", digits='Product Unit of Measure', compute="_ges_compute_tot_value")
    ges_value_tot = fields.Float(string="Value", help="""Value""", digits='Product Price', compute="_ges_compute_tot_value")
    ges_qte_tot = fields.Float(string="Quantity", help="""Quantity""", digits='Product Unit of Measure', compute="_ges_compute_tot_value")

    @api.depends('product_id.product_tmpl_id.qty_available', 'value')
    def _ges_compute_tot_value(self):
        for sq in self:
            # sq.ges_pack_tot = sq.product_id.product_tmpl_id.get_packs_qty(sq.product_id.product_tmpl_id.qty_available)
            # sq.ges_piece_tot = sq.product_id.product_tmpl_id.get_pieces_qty(sq.product_id.product_tmpl_id.qty_available)
            # sq.ges_nweight_tot = sq.product_id.product_tmpl_id.get_nweight_qty(sq.product_id.product_tmpl_id.qty_available)
            query = """ select sum(q.ges_pack),sum(q.ges_piece),sum(q.ges_nweight),sum(q.quantity * lot.ges_purchase_price)
                                from stock_quant q
                                left join stock_location loc on loc.id = q.location_id
                                left join stock_production_lot lot on lot.id = q.lot_id
                                where loc.usage='internal'
                                and q.product_id = %(product_id)s
                            """                            
            query_args = {'product_id': sq.product_id.id}

            self.env.cr.execute(query, query_args)

            ids = [(r[0], r[1], r[2], r[3]) for r in self.env.cr.fetchall()]
            
            for pack, piece, weight, value in ids:
                sq.ges_pack_tot = pack
                sq.ges_piece_tot = piece
                sq.ges_nweight_tot = weight
                sq.ges_value_tot = value

                # sq.ges_pack_tot = sum(totquant.ges_pack for totquant in self.env['stock.quant'].search([('location_id.usage', '=', 'internal'), ('product_id', '=', sq.product_id.id)]))
                # sq.ges_piece_tot = sum(totquant.ges_piece for totquant in self.env['stock.quant'].search([('location_id.usage', '=', 'internal'), ('product_id', '=', sq.product_id.id)]))
                # sq.ges_nweight_tot = sum(totquant.ges_nweight for totquant in self.env['stock.quant'].search([('location_id.usage', '=', 'internal'), ('product_id', '=', sq.product_id.id)]))
                # sq.ges_value_tot = sum(totquant.value for totquant in self.env['stock.quant'].search([('location_id.usage', '=', 'internal'), ('product_id', '=', sq.product_id.id)]))
            sq.ges_qte_tot = sq.product_id.product_tmpl_id.qty_available

    @api.depends('quantity')
    def _ges_compute_value(self):
        for sq in self:
            sq.ges_pack = sq.product_id.product_tmpl_id.get_packs_qty(
                sq.quantity)
            sq.ges_piece = sq.product_id.product_tmpl_id.get_pieces_qty(
                sq.quantity)
            sq.ges_nweight = sq.product_id.product_tmpl_id.get_nweight_qty(
                sq.quantity)

    @api.model
    def _get_quants_action(self, domain=None, extend=False):
        action = super(StockQuant, self)._get_quants_action(domain, extend)
        ctx = action['context'] or {}
        ges_loss_id = ctx.get('loss_id', False)
        ges_dest_id = ctx.get('dest_id', False)
        ges_name = _('Stock On Hand')
        if ges_loss_id:
            ges_name = _('Loss')
            ctx.pop('search_default_internal_loc', None)
            if domain:
                domain = domain+[('location_id.id', '=', ges_loss_id)]
            else:
                domain = [('location_id.id', '=', ges_loss_id)]
        if ges_dest_id:
            ges_name = _('Destructions')
            ctx.pop('search_default_internal_loc', None)
            if domain:
                domain = domain+[('location_id.id', '=', ges_dest_id)]
            else:
                domain = [('location_id.id', '=', ges_dest_id)]
        action['domain'] = domain
        action['name'] = ges_name
        return action
