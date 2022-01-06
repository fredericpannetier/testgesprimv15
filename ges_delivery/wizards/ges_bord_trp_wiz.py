# -*- coding: utf-8 -*-

from odoo import api, fields, models

import calendar
import datetime
 
class GesBordTrpWiz(models.TransientModel):
    _name = "ges.bordtrp.wiz"
    _description = "Impression bordereaux transport"
    
    company_id = fields.Many2one('res.company', string='Société', readonly=True,  default=lambda self: self.env.user.company_id)
    date_sel = fields.Date(string='Date', help="Selection date", required=True,
                           default=datetime.date(datetime.date.today().year, datetime.date.today().month,
                                                     calendar.mdays[datetime.date.today().month]))
    transp_deb = fields.Char(default="", string="Carrier from")
    transp_fin = fields.Char(required=True, default="zzzzzzzzzzzzzzzzzzzzzzzzzzzzzz", string="Carrier to")
    stock_picking_ids = fields.Many2many('stock.picking', string='Stock pickings')
    
    
    def edit_bordereau(self):
        # on récupère les livraisons du jour
        wdate       = self.date_sel
        date_deb    = datetime.datetime(wdate.year,wdate.month,wdate.day,0,0,0,0).strftime("%Y-%m-%d %H:%M:%S")
        date_fin    = datetime.datetime(wdate.year,wdate.month,wdate.day,23,59,59,0).strftime("%Y-%m-%d %H:%M:%S")
        stock_pickings1 = self.env['stock.picking'].search([('date_done','>',date_deb),('date_done','<',date_fin)])
        # on filtre sur les expéditions
        stock_pickings2 = stock_pickings1.filtered(lambda sp: sp.picking_type_id.code == 'outgoing')
        # on filtre sur les transporteurs de la sélection
        if self.transp_deb=="" or not self.transp_deb or self.transp_deb==" ":
            # si pas de selection début, on va prendre les expéditions sans transporteur et inférieur à transporteur fin
            stock_pickings3 = stock_pickings2.filtered(lambda sp: sp.carrier_id.name == False or sp.carrier_id.name <= self.transp_fin)
        else:
            # sinon on teste transporteur début/transporteur fin
            stock_pickings3 = stock_pickings2.filtered(lambda sp:  sp.carrier_id and  sp.carrier_id.name >= self.transp_deb and sp.carrier_id.name <= self.transp_fin)
        self.stock_picking_ids=stock_pickings3
        if self.stock_picking_ids:
            return self.env.ref('ges_delivery.ges_wiz_report_bordtrp').report_action(self)
        return {}
#         wspId = 0
#         for stpick in stock_pickings3.sorted(key=lambda sp: sp.carrier_id.name):
#             # à chaque rupture de transporteur on lance un bordereau
#             if wspId != stpick.carrier_id.id:
#                 if wspId != 0:
#                     self.carrier_id = wspId
#                     self.stock_picking_ids = stock_pickings3.filtered(lambda sp: sp.carrier_id.id == wspId)
#                     self.env.ref('difodoo_ventes.di_wiz_report_bordtrp').report_action(self)
#                 wspId = stpick.carrier_id.id
#         if wspId != 0:
#             # rupture finale
#             self.carrier_id = wspId
#             self.stock_picking_ids = stock_pickings3.filtered(lambda sp: sp.carrier_id.id == wspId)
#             self.env.ref('difodoo_ventes.di_wiz_report_bordtrp').report_action(self)
#         return {}
    
    
    
    
    
    