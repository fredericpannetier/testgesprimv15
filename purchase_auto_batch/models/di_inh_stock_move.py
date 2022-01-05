# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from math import ceil
from datetime import datetime
from odoo.addons import decimal_precision as dp
from odoo.tools.float_utils import float_round
from odoo.tools import float_utils


class StockMove(models.Model):
    _inherit = "stock.move"

    ges_inventory_id = fields.Many2one(
        'ges.inventory', 'Gesprim Inventory FIFO', check_company=True)


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    @api.model
    def create(self, vals):
        group_production_lot_enabled = self.user_has_groups(
            'stock.group_production_lot')
        if group_production_lot_enabled:  # on vérifie que le suivi par lot est activé
            genlot = self.env['ir.config_parameter'].sudo(
            ).get_param('purchase_auto_batch.di_gen_lot')
            if genlot and genlot != 'none':  # si on a activé la génération auto des lots
                orig = self.env['stock.location'].browse(
                    vals.get('location_id'))
                # seulement si on est en réception fournisseur
                if vals.get('picking_id') and orig.usage != 'customer':
                    if vals['picking_id'] != False:
                        picking = self.env['stock.picking'].browse(
                            vals['picking_id'])
                        if picking.picking_type_id.code == 'incoming':  # on vérifie qu'on est pas sur un retour fournisseur
                            if not vals.get('lot_id'):  # si pas de lot saisi
                                if vals.get('move_id'):  # si on a une commande liée
                                    # si on est bien sur un move et pas sur un move_line orphelin
                                    if vals['move_id'] != False:
                                        move = self.env['stock.move'].browse(
                                            vals['move_id'])
                                        if move.product_id.tracking == 'lot':  # si l'article est paramétré en suivi par lot
                                            if genlot == 'po':  # lot = n° cde
                                                if move.purchase_line_id.order_id.id != False:  # si on est bien associé à une cde
                                                    lotexist = self.env['stock.production.lot'].search(
                                                        ['&', ('name', '=', move.purchase_line_id.order_id.name), ('product_id', '=', move.product_id.id)])
                                                    if not lotexist:  # si le lot n'existe pas, on le créé
                                                        #                                                         if 'company_id' in vals:
                                                        #                                                             data = {
                                                        #                                                             'company_id':vals['company_id'],
                                                        #                                                             'name': move.purchase_line_id.order_id.name,
                                                        #                                                             'product_id' : move.product_id.id
                                                        #                                                             }
                                                        #                                                         else:
                                                        #                                                             data = {
                                                        #                                                             'name': move.purchase_line_id.order_id.name,
                                                        #                                                             'product_id' : move.product_id.id
                                                        #                                                             }
                                                        #
                                                        #                                                         lot = self.env['stock.production.lot'].create(data)  # création du lot
                                                        #                                                         vals['lot_id'] = lot.id
                                                        vals['lot_name'] = move.purchase_line_id.order_id.name
                                                    else:
                                                        #                                                         vals['lot_id'] = lotexist.id
                                                        vals['lot_name'] = lotexist.name
                                                else:  # sinon on est forcément associé à un BL, on prendra ce n°
                                                    lotexist = self.env['stock.production.lot'].search(
                                                        ['&', ('name', '=', picking.name), ('product_id', '=', move.product_id.id)])
                                                    if not lotexist:  # si le lot n'existe pas, on le créé
                                                        #                                                         if 'company_id' in vals:
                                                        #                                                             data = {
                                                        #                                                             'company_id':vals['company_id'],
                                                        #                                                             'name': picking.name,
                                                        #                                                             'product_id' : move.product_id.id
                                                        #                                                             }
                                                        #                                                         else:
                                                        #                                                             data = {
                                                        #                                                             'name': picking.name,
                                                        #                                                             'product_id' : move.product_id.id
                                                        #                                                             }
                                                        #                                                         lot = self.env['stock.production.lot'].create(data)
                                                        #
                                                        #                                                         vals['lot_id'] = lot.id
                                                        vals['lot_name'] = picking.name
                                                    else:
                                                        #                                                         vals['lot_id'] = lotexist.id
                                                        vals['lot_name'] = lotexist.name

                                            else:  # lot = nouveau numéro selon séquence
                                                seqlot = self.env['ir.config_parameter'].sudo().get_param(
                                                    'purchase_auto_batch.di_seq_lot')  # récup de la séquence dans les paramètres
                                                sequence = self.env['ir.sequence'].browse(
                                                    int(seqlot))
                                                if 'company_id' in vals:
                                                    nextlot = self.env['ir.sequence'].with_context(
                                                        force_company=vals['company_id']).next_by_code(sequence.code) or _('New')
                                                else:
                                                    nextlot = self.env['ir.sequence'].next_by_code(
                                                        sequence.code) or _('New')

                                                lotexist = self.env['stock.production.lot'].search(
                                                    ['&', ('name', '=', nextlot), ('product_id', '=', move.product_id.id)])
                                                if not lotexist:  # si le lot n'existe pas, on le créé
                                                    #                                                     if 'company_id' in vals:
                                                    #                                                         data = {
                                                    #                                                         'company_id':vals['company_id'],
                                                    #                                                         'name': nextlot,
                                                    #                                                         'product_id' : move.product_id.id
                                                    #                                                         }
                                                    #                                                     else:
                                                    #                                                         data = {
                                                    #                                                         'name': nextlot,
                                                    #                                                         'product_id' : move.product_id.id
                                                    #                                                         }
                                                    #                                                     lot = self.env['stock.production.lot'].create(data)

                                                    #                                                     vals['lot_id'] = lot.id
                                                    vals['lot_name'] = nextlot
                                                else:
                                                    #                                                     vals['lot_id'] = lotexist.id
                                                    vals['lot_name'] = lotexist.name
        ml = super(StockMoveLine, self).create(vals)

        return ml
