# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from math import ceil
from datetime import datetime
from odoo.addons import decimal_precision as dp
from odoo.tools.float_utils import float_round
from odoo.tools import float_utils
from _struct import pack
from unicodedata import category


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.model
    def create(self, vals):
        if vals.get('sale_line_id'):
            if vals["sale_line_id"] is not False and vals["sale_line_id"] != 0:
                # recherche de l'enregistrement sale order line avec
                # sale_line_id = sale_line_id
                sol = self.env['sale.order.line'].search([('id', '=', vals["sale_line_id"])], limit=1)
                if sol.id is not False:
                    vals["ges_brand_id"] = sol.ges_brand_id.id
                    vals["ges_category_id"] = sol.ges_category_id.id
                    vals["ges_origin_id"] = sol.ges_origin_id.id
                    vals["ges_size_id"] = sol.ges_size_id.id
                    vals["ges_tare"] = sol.ges_tare
                    vals["product_uom"] = sol.product_uom.id
        if vals.get('purchase_line_id'):
            pol = self.env['purchase.order.line'].search([('id', '=', vals["purchase_line_id"])], limit=1)
            if pol.id is not False:
                vals["ges_brand_id"] = pol.ges_brand_id.id
                vals["ges_category_id"] = pol.ges_category_id.id
                vals["ges_origin_id"] = pol.ges_origin_id.id
                vals["ges_size_id"] = pol.ges_size_id.id
                vals["ges_tare"] = pol.ges_tare
        res = super(StockMove, self).create(vals)
        return res

    @api.onchange('product_id')
    def _ges_product_onchange(self):
        if self.product_id:
            if self.product_id.ges_packaging_id:
                self.ges_tare = self.product_id.ges_packaging_id.tare
            self.ges_brand_id = self.product_id.ges_brand_id
            self.ges_category_id = self.product_id.ges_category_id
            self.ges_origin_id = self.product_id.ges_origin_id
            self.ges_size_id = self.product_id.ges_size_id

    @api.depends('move_line_ids.ges_amount')
    def _ges_compute_amount(self):
        for move in self:
            move.ges_amount = sum([ml.ges_amount for ml in move.move_line_ids])

    @api.depends('move_line_ids.lot_id')
    def _compute_firstlot(self):
        for move in self:
            move.ges_firstlot = ''
            for ml in move.move_line_ids.sorted(key=lambda ml: ml.id):
                move.ges_firstlot = ml.lot_id.name
                break

    ges_firstlot = fields.Char("Lot", compute="_compute_firstlot")

    ges_category_id = fields.Many2one('di.multi.table', string='Category', domain=[
                                      ('record_type', '=', 'category')], help="The category of the product.")
    ges_origin_id = fields.Many2one('di.multi.table', string='Origin', domain=[
                                    ('record_type', '=', 'origin')], help="The Origin of the product.")
    ges_brand_id = fields.Many2one('di.multi.table', string='Brand', domain=[
                                   ('record_type', '=', 'brand')], help="The Brand of the product.")
    ges_size_id = fields.Many2one('di.multi.table', string='Size', domain=[
                                  ('record_type', '=', 'size')], help="The Size of the product.")
    ges_category_des = fields.Char(related='ges_category_id.name')
    ges_origin_des = fields.Char(related='ges_origin_id.name')
    ges_brand_des = fields.Char(related='ges_brand_id.name')
    ges_size_des = fields.Char(related='ges_size_id.name')
    ges_inventory_id = fields.Many2one(
        'ges.inventory', string='Inventory', check_company=True)
    ges_pack = fields.Float(string="Number of packages", help="""Number of packages""", digits=(
        12, 2), compute='_compute_ges_values', store=True)
    ges_piece = fields.Integer(
        string="Number of pieces", help="""Number of pieces""", compute='_compute_ges_values', store=True)
    ges_nweight = fields.Float(string="Net weight", help="""Net weight""",
                               digits='Product Unit of Measure', compute='_compute_ges_values', store=True)
    ges_gweight = fields.Float(
        string="Gross weight", help="""Gross weight""", digits='Product Unit of Measure')
    ges_tare = fields.Float(
        string="Tare", help="""Tare""", digits='Product Unit of Measure')
    ges_amount = fields.Float(
        "Amount", compute="_ges_compute_amount", store=True)

    def _action_assign(self):
        super(StockMove, self)._action_assign()
        for move in self:
            for line in move.move_line_ids:
                line.qty_done = line.product_uom_qty
                line.update_ges_values()

    @api.depends('move_line_ids.ges_pack', 'move_line_ids.ges_piece', 'move_line_ids.ges_nweight', 'move_line_ids.ges_gweight')
    def _compute_ges_values(self):
        move_lines = self.env['stock.move.line']
        for move in self:
            ges_pack = 0.0
            ges_piece = 0
            ges_nweight = 0.0
            ges_gweight = 0.0
            
#             ges_nbpal = 0.0
            for move_lines in move.move_line_ids:
                ges_pack += move_lines.ges_pack
                ges_piece += move_lines.ges_piece
                ges_nweight += move_lines.ges_nweight
                ges_gweight += move_lines.ges_gweight
#                 ges_nbpal += move_lines.ges_nbpal
            move.ges_pack = ges_pack
            move.ges_piece = ges_piece
            move.ges_nweight = ges_nweight
            move.ges_gweight = ges_gweight
#             move.ges_nbpal = ges_nbpal


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def _create_and_assign_production_lot(self):
        """Modification standard pour pouvoir mettre plusieurs fois le même article avec le même lot dans une même réception et que cela ne créé le lot qu'une fois"""
        """ Creates and assign new production lots for move lines."""
        lots = self.env['stock.production.lot']
        for ml in self:
            lot = self.env['stock.production.lot'].search([('product_id', '=', ml.product_id.id), ('name', '=', ml.lot_name)])
            if not lot:
                lot_vals = {
                    'company_id': ml.move_id.company_id.id,
                    'name': ml.lot_name,
                    'product_id': ml.product_id.id,
                }
                lot = self.env['stock.production.lot'].create(lot_vals)
            lots += lot
        for ml, lotv in zip(self, lots):
            ml._assign_production_lot(lotv)

    @api.depends('ges_usage_loc_dest')
    def _ges_compute_IO(self):
        for sml in self:
            if sml.ges_usage_loc_dest == 'internal':
                sml.ges_io = 'incoming'
            else:
                sml.ges_io = 'outgoing'

    @api.depends('ges_io', 'qty_done')
    def _ges_compute_sign(self):
        for sml in self:
            if sml.ges_io in ('incoming', 'entrée'):
                sml.ges_pieces_sign = sml.ges_piece
                sml.ges_packages_sign = sml.ges_pack
                sml.ges_nweight_sign = sml.ges_nweight
                if sml.state == 'done':
                    sml.ges_qty_done_sign = sml.qty_done
                else:
                    sml.ges_qty_done_sign = sml.product_uom_qty
            else:
                sml.ges_pieces_sign = -sml.ges_piece
                sml.ges_packages_sign = -sml.ges_pack
                sml.ges_nweight_sign = -sml.ges_nweight
                if sml.state == 'done':
                    sml.ges_qty_done_sign = -sml.qty_done
                else:
                    sml.ges_qty_done_sign = -sml.product_uom_qty
#             sml.ges_pieces_sign = sml.product_id.product_tmpl_id.get_pieces_qty(sml.ges_qty_done_sign)
#             sml.ges_packages_sign = sml.product_id.product_tmpl_id.get_pieces_qty(sml.ges_qty_done_sign)
#             sml.ges_nweight_sign = sml.product_id.product_tmpl_id.get_pieces_qty(sml.ges_qty_done_sign)

    @api.depends('ges_partner')
    def _compute_partner_name(self):
        for move in self:
            if move.ges_partner:
                move.ges_partner_name = move.ges_partner.name
            else:
                move.ges_partner_name = _("Internal")

    @api.depends('move_id.sale_line_id.price_unit', 'move_id.purchase_line_id.price_unit', 'qty_done', 'state', 'product_uom_qty', 'ges_io', 'move_id.sale_line_id.purchase_price')
    def _ges_compute_amount(self):
        for line in self:
            line.ges_amount = 0.0
            if line.move_id.sale_line_id:
                line.ges_sale_price = line.move_id.sale_line_id.price_unit
                line.ges_purchase_price = line.move_id.sale_line_id.purchase_price
                line.ges_price = line.ges_sale_price
                if line.state == 'done':
                    line.ges_amount = line.move_id.sale_line_id.price_unit * line.qty_done
                else:
                    line.ges_amount = line.move_id.sale_line_id.price_unit * line.product_uom_qty
            elif line.move_id.purchase_line_id:
                line.ges_purchase_price = line.move_id.purchase_line_id.price_unit
                line.ges_price = line.ges_purchase_price
                if line.state == 'done':
                    line.ges_amount = line.move_id.purchase_line_id.price_unit * line.qty_done
                else:
                    line.ges_amount = line.move_id.purchase_line_id.price_unit * line.product_uom_qty
            if line.ges_io in ('incoming', 'entrée'):
                line.ges_amount_sign = line.ges_amount
            else:
                line.ges_amount_sign = -line.ges_amount

    ges_category_id = fields.Many2one(related='move_id.ges_category_id', store=False)
    ges_origin_id = fields.Many2one(related='move_id.ges_origin_id', store=False)
    ges_brand_id = fields.Many2one(related='move_id.ges_brand_id', store=False)
    ges_size_id = fields.Many2one(related='move_id.ges_size_id', store=False)
    ges_suppbatch = fields.Char("Supplier lot")
    ges_pack = fields.Float(string="Number of packages",
                            help="""Number of packages""", digits=(12, 2))
    ges_piece = fields.Integer(
        string="Number of pieces", help="""Number of pieces""")
    ges_nweight = fields.Float(
        string="Net weight", help="""Net weight""", digits='Product Unit of Measure')

    ges_gweight = fields.Float(string="Gross weight", help="""Gross weight""", digits='Product Unit of Measure')
    ges_tare = fields.Float(string="Tare", related='move_id.ges_tare', store=False)


#     ges_usage_loc = fields.Selection(related='location_id.usage', store=True)
    ges_usage_loc_dest = fields.Selection(
        related='location_dest_id.usage', store=True)
    ges_partner = fields.Many2one(
        related="move_id.picking_id.partner_id", string="Partner", store=True)
    ges_partner_name = fields.Char(string="Partner", compute="_compute_partner_name", store=True)
#    ges_io = fields.Char(string="Incoming/ Outgoing", compute='_ges_compute_IO', store=True)  # TODO changer en Selection
    ges_io = fields.Selection(string='Incoming/ Outgoing', selection=[('incoming', 'Incoming'), ('outgoing', 'Outgoing')], compute='_ges_compute_IO')    
    ges_pieces_sign = fields.Integer(
        string='Pieces', compute='_ges_compute_sign', store=True)
    ges_packages_sign = fields.Float(
        string='Packages', compute='_ges_compute_sign', store=True, digits=(12, 2))
    ges_nweight_sign = fields.Float(
        string='Net weight', compute='_ges_compute_sign', store=True)
    ges_qty_done_sign = fields.Float(
        'Quantity', digits='Product Unit of Measure', compute='_ges_compute_sign', store=True)
    ges_amount = fields.Float(
        "Amount", digits="Product Price", compute="_ges_compute_amount", store=True)
    ges_amount_sign = fields.Float(
        "Amount", digits="Product Price", compute="_ges_compute_amount", store=True)
    ges_sale_price = fields.Float(
        "Sale price", digits="Product Price", compute="_ges_compute_amount", store=True)
    ges_purchase_price = fields.Float(
        "Purchase price", digits="Product Price", compute="_ges_compute_amount", store=True)
    ges_price = fields.Float("Price", digits="Product Price",
                             compute="_ges_compute_amount", store=True, group_operator=False)

    @api.onchange('ges_pack')
    def _ges_pack_onchange(self):
        if self.product_id:
            if not self.env.context.get("noonchangepack") and self.ges_pack:
                # sauvegarde du champ pour voir si on passera dans le onchange correspondant
                qty_done = self.qty_done
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
                    self.qty_done = self.ges_piece
                    if self.product_id.ges_uweight:
                        self.ges_nweight = self.qty_done*self.product_id.ges_uweight
                        self.ges_gweight = self.ges_nweight + (self.ges_tare * self.ges_pack)
                elif self.product_uom_id.ges_unittype == 'Package':
                    self.qty_done = self.ges_pack
                    if self.product_id.ges_uweight:
                        self.ges_nweight = self.qty_done*self.product_id.ges_uweight
                        self.ges_gweight = self.ges_nweight + (self.ges_tare * self.ges_pack)
                elif self.product_uom_id.ges_unittype == 'Net weight':
                    if self.product_id.ges_uweight and self.ges_piece:
                        self.ges_nweight = self.ges_piece*self.product_id.ges_uweight
                        self.ges_gweight = self.ges_nweight + (self.ges_tare * self.ges_pack)
                    self.qty_done = self.ges_nweight
                if self.qty_done != qty_done:
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
                    if self.qty_done != self.ges_piece:
                        # si la valeur a changé, on passe en contexte de ne pas traiter le onchange
                        self.qty_done = self.ges_piece
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
                    if self.qty_done != self.ges_nweight:
                        # si la valeur a changé, on passe en contexte de ne pas traiter le onchange
                        self.qty_done = self.ges_nweight
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
                if self.product_uom_id.ges_unittype == 'Net weight':
                    if self.qty_done != self.ges_nweight:
                        # si la valeur a changé, on passe en contexte de ne pas traiter le onchange
                        self.qty_done = self.ges_nweight
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
                    if self.product_uom_id.ges_unittype == 'Net weight':
                        if self.qty_done != self.ges_nweight:
                            # si la valeur a changé, on passe en contexte de ne pas traiter le onchange
                            self.qty_done = self.ges_nweight
                            self.env.context = self.with_context(
                                noonchangeqty=True).env.context
            self.env.context = self.with_context(noonchangetare=False).env.context

    @api.onchange('qty_done')
    def _product_uom_qty_onchange(self):
        if self.product_id:
            if not self.env.context.get("noonchangeqty") and self.qty_done:
                if self.product_uom_id.ges_unittype == 'Piece':
                    if self.ges_piece != self.qty_done:
                        # si la valeur a changé, on passe en contexte de ne pas traiter le onchange
                        self.ges_piece = self.qty_done
                        self.env.context = self.with_context(
                            noonchangepiece=True).env.context
                elif self.product_uom_id.ges_unittype == 'Package':
                    if self.ges_pack != self.qty_done:
                        # si la valeur a changé, on passe en contexte de ne pas traiter le onchange
                        self.ges_pack = self.qty_done
                        self.env.context = self.with_context(
                            noonchangepack=True).env.context
                elif self.product_uom_id.ges_unittype == 'Net weight':
                    if self.ges_nweight != self.qty_done:
                        # si la valeur a changé, on passe en contexte de ne pas traiter le onchange
                        self.ges_nweight = self.qty_done
                        self.ges_gweight = self.ges_nweight + (self.ges_tare * self.ges_pack)
                        self.env.context = self.with_context(noonchangeweight=True).env.context
                        self.env.context = self.with_context(noonchangegweight=True).env.context
            # on rétabli le onchange dans le contexte
            self.env.context = self.with_context(noonchangeqty=False).env.context

    @api.model
    def create(self, vals):
        
        ml = super(StockMoveLine, self).create(vals)
        group_production_lot_enabled = self.user_has_groups('stock.group_production_lot')
        if group_production_lot_enabled:  # on vérifie que le suivi par lot est activé
            if ml.picking_id and ml.location_id.usage != 'customer':  # seulement si on est en réception fournisseur
                if ml.picking_id is not False:
                    # on vérifie qu'on est pas sur un retour fournisseur
                    if ml.picking_id.picking_type_id.code == 'incoming':
                        if ml.lot_id:
                            ml.lot_id.ges_update_suppbatch()
        return ml

    def write(self, vals):
        group_production_lot_enabled = self.user_has_groups(
            'stock.group_production_lot')
        if group_production_lot_enabled:  # on vérifie que le suivi par lot est activé
            for ml in self:
                if ml.picking_id and ml.location_id.usage != 'customer':  # seulement si on est en réception fournisseur
                    if ml.picking_id is not False:
                        # on vérifie qu'on est pas sur un retour fournisseur
                        if ml.picking_id.picking_type_id.code == 'incoming':
                            if ml.lot_id:
                                ml.lot_id.ges_update_suppbatch()
        res = super(StockMoveLine, self).write(vals)
        return res

    def update_ges_values(self):
        for ml in self:
            if ml.state != 'done':
                line = False
                if ml.move_id.sale_line_id:
                    line = ml.move_id.sale_line_id
                    qty = line.product_uom_qty
                if ml.move_id.purchase_line_id:
                    line = ml.move_id.purchase_line_id
                    qty = line.product_qty
                if line:
                    if ml.qty_done == qty:
                        ml.ges_pack = line.ges_pack
                        ml.ges_piece = line.ges_piece
                        ml.ges_nweight = line.ges_nweight
                        ml.ges_gweight = line.ges_gweight
                    else:
                        if qty != 0:
                            ml.ges_pack = ml.qty_done/qty*line.ges_pack
                            ml.ges_piece = ml.qty_done/qty*line.ges_piece
                            ml.ges_nweight = ml.qty_done/qty*line.ges_nweight
                            ml.ges_gweight = ml.qty_done/qty*line.ges_gweight
                    # pour éviter tout problème d'arrondi
                    if ml.product_uom_id.ges_unittype == 'Piece':
                        ml.ges_piece = ml.qty_done
                    elif ml.product_uom_id.ges_unittype == 'Package':
                        ml.ges_pack = ml.qty_done
                    elif ml.product_uom_id.ges_unittype == 'Net weight':
                        ml.ges_nweight = ml.qty_done
                        ml.ges_gweight = ml.ges_nweight + (ml.ges_tare * ml.ges_pack)

    def _get_aggregated_product_quantities(self, **kwargs):
        """Returns dictionary of products and corresponding values of interest + gesprim values

        Unfortunately because we are working with aggregated data, we have to loop through the
        aggregation to add more values to each datum. This extension adds on the gesprim values.

        returns: dictionary {same_key_as_super: {same_values_as_super, ges_pack, pieces, nweight, ...}, ...}
        """
#         aggregated_move_lines = super()._get_aggregated_product_quantities(**kwargs)
# copie standard
        aggregated_move_lines = {}
        for move_line in self:
            name = move_line.product_id.display_name
            description = move_line.move_id.description_picking
            if description == name or description == move_line.product_id.name:
                description = False
            uom = move_line.product_uom_id
#             line_key = str(move_line.product_id.id) + "_" + name + (description or "") + "uom " + str(uom.id) # modif gesprim
            if move_line.move_id.sale_line_id:
                line_key = str(move_line.product_id.id) + "_" + name + (description or "") + \
                    "uom " + str(uom.id) + "_" + \
                    str(move_line.move_id.sale_line_id.price_unit)
            else:
                line_key = str(move_line.product_id.id) + "_" + \
                    name + (description or "") + "uom " + str(uom.id)

            if line_key not in aggregated_move_lines:
                #                 aggregated_move_lines[line_key] = {'name': name,
                #                                                        'description': description,
                #                                                        'qty_done': move_line.qty_done,
                #                                                        'product_uom': uom.name,
                #                                                        'product': move_line.product_id,
                #                                                         }
                # modif gesprim
                if move_line.move_id.sale_line_id:
                    aggregated_move_lines[line_key] = {'name': name,
                                                       'description': description,
                                                       'qty_done': move_line.qty_done,
                                                       'product_uom': uom.name,
                                                       'product': move_line.product_id,
                                                       'ges_price_unit': move_line.move_id.sale_line_id.price_unit,
                                                       'sale_line_id': move_line.move_id.sale_line_id,
                                                       'purchase_line_id': self.env['purchase.order.line'],
                                                       'ges_category_des': move_line.move_id.ges_category_des,
                                                       'ges_origin_des': move_line.move_id.ges_origin_des,
                                                       'ges_brand_des': move_line.move_id.ges_brand_des,
                                                       'ges_size_des': move_line.move_id.ges_size_des,
                                                       'ges_pack': move_line.ges_pack,
                                                       'ges_piece': move_line.ges_piece,
                                                       'ges_nweight': move_line.ges_nweight,
                                                       'ges_gweight': move_line.ges_gweight,
                                                       }
                elif move_line.move_id.purchase_line_id:
                    aggregated_move_lines[line_key] = {'name': name,
                                                       'description': description,
                                                       'qty_done': move_line.qty_done,
                                                       'product_uom': uom.name,
                                                       'product': move_line.product_id,
                                                       'ges_price_unit': move_line.move_id.purchase_line_id.price_unit,
                                                       'sale_line_id': self.env['sale.order.line'],
                                                       'purchase_line_id': move_line.move_id.purchaseline_id,
                                                       'ges_category_des': move_line.move_id.ges_category_des,
                                                       'ges_origin_des': move_line.move_id.ges_origin_des,
                                                       'ges_brand_des': move_line.move_id.ges_brand_des,
                                                       'ges_size_des': move_line.move_id.ges_size_des,
                                                       'ges_pack': move_line.ges_pack,
                                                       'ges_piece': move_line.ges_piece,
                                                       'ges_nweight': move_line.ges_nweight,
                                                       'ges_gweight': move_line.ges_gweight,
                                                       }

                else:
                    aggregated_move_lines[line_key] = {'name': name,
                                                       'description': description,
                                                       'qty_done': move_line.qty_done,
                                                       'product_uom': uom.name,
                                                       'product': move_line.product_id,
                                                       'sale_line_id': self.env['sale.order.line'],
                                                       'purchase_line_id': self.env['purchase.order.line'],
                                                       'ges_category_des': move_line.move_id.ges_category_des,
                                                       'ges_origin_des': move_line.move_id.ges_origin_des,
                                                       'ges_brand_des': move_line.move_id.ges_brand_des,
                                                       'ges_size_des': move_line.move_id.ges_size_des,
                                                       'ges_pack': move_line.ges_pack,
                                                       'ges_piece': move_line.ges_piece,
                                                       'ges_nweight': move_line.ges_nweight,
                                                       'ges_gweight': move_line.ges_gweight,
                                                       }
            else:
                aggregated_move_lines[line_key]['qty_done'] += move_line.qty_done
                aggregated_move_lines[line_key]['ges_pack'] += move_line.ges_pack
                aggregated_move_lines[line_key]['ges_piece'] += move_line.ges_piece
                aggregated_move_lines[line_key]['ges_nweight'] += move_line.ges_nweight
                aggregated_move_lines[line_key]['ges_gweight'] += move_line.ges_gweight

# fin standard

        # for aggregated_move_line in aggregated_move_lines:
        #     packs = aggregated_move_lines[aggregated_move_line]['product'].product_tmpl_id.get_packs_qty(
        #         aggregated_move_lines[aggregated_move_line]['qty_done'])
        #     pieces = aggregated_move_lines[aggregated_move_line]['product'].product_tmpl_id.get_pieces_qty(
        #         aggregated_move_lines[aggregated_move_line]['qty_done'])
        #     nweight = aggregated_move_lines[aggregated_move_line]['product'].product_tmpl_id.get_nweight_qty(
        #         aggregated_move_lines[aggregated_move_line]['qty_done'])
        #     gweight = aggregated_move_lines[aggregated_move_line]['product'].product_tmpl_id.get_nweight_qty(
        #         aggregated_move_lines[aggregated_move_line]['qty_done'])
            
        #     # category = aggregated_move_lines[aggregated_move_line]['product'].product_tmpl_id.ges_category_des
        #     # origin = aggregated_move_lines[aggregated_move_line]['product'].product_tmpl_id.ges_origin_des
        #     # brand = aggregated_move_lines[aggregated_move_line]['product'].product_tmpl_id.ges_brand_des
        #     # size = aggregated_move_lines[aggregated_move_line]['product'].product_tmpl_id.ges_size_des

        #     aggregated_move_lines[aggregated_move_line]['ges_pack'] = packs
        #     aggregated_move_lines[aggregated_move_line]['ges_piece'] = pieces
        #     aggregated_move_lines[aggregated_move_line]['ges_nweight'] = nweight
        #     aggregated_move_lines[aggregated_move_line]['ges_gweight'] = gweight
            # aggregated_move_lines[aggregated_move_line]['ges_category_des'] = category
            # aggregated_move_lines[aggregated_move_line]['ges_origin_des'] = origin
            # aggregated_move_lines[aggregated_move_line]['ges_brand_des'] = brand
            # aggregated_move_lines[aggregated_move_line]['ges_size_des'] = size

        return aggregated_move_lines
