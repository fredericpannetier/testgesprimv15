# -*- coding: utf-8 -*-

from odoo import api, fields, models

import calendar
import datetime
 
class GesCarrierCtroWiz(models.TransientModel):
    _name = "ges.carrier.ctrl.wiz"
    _description = "Print carrier control"
    
    company_id = fields.Many2one('res.company', string='Company', readonly=True,  default=lambda self: self.env.user.company_id)
    begin_date = fields.Date(required=True, default=datetime.date(datetime.date.today().year, datetime.date.today().month, 1), string="Begin date")
    end_date = fields.Date(required=True, default=datetime.date(datetime.date.today().year, datetime.date.today().month, calendar.mdays[datetime.date.today().month]), string="End date")
    
    carrier_begin = fields.Char(default=" ", string="Carrier begin")
    carrier_end = fields.Char(required=True, default="zzzzzzzzzzzzzzz", string="Carrier end")
    stock_picking_ids = fields.Many2many('stock.picking', string='Stock pickings')
        
    def print_carrier_ctrl(self):
        # on récupére les livraisons du jour
        wdate = self.begin_date
        date_b = datetime.datetime(wdate.year,wdate.month,wdate.day,0,0,0,0).strftime("%Y-%m-%d %H:%M:%S")
        wdate = self.end_date
        date_e = datetime.datetime(wdate.year,wdate.month,wdate.day,23,59,59,0).strftime("%Y-%m-%d %H:%M:%S")
        stock_pickings1 = self.env['stock.picking'].search([('date_done','>',date_b),('date_done','<',date_e)])
        # on filtre sur les expéditions
        stock_pickings2 = stock_pickings1.filtered(lambda sp: sp.picking_type_id.code == 'outgoing')
        # on filtre sur les transporteurs de la sélection
        if self.carrier_begin==" ":
            # si pas de selection début, on va prendre les expéditions sans transporteur et inférieur é transporteur fin
            stock_pickings3 = stock_pickings2.filtered(lambda sp: sp.carrier_id.name == False or sp.carrier_id.name <= self.carrier_end)
        else:
            # sinon on teste transporteur début/transporteur fin
            stock_pickings3 = stock_pickings2.filtered(lambda sp:  sp.carrier_id and  sp.carrier_id.name >= self.carrier_begin and sp.carrier_id.name <= self.carrier_end)
        self.stock_picking_ids=stock_pickings3
        if self.stock_picking_ids:
            return self.env.ref('ges_delivery.ges_report_carrier_ctrl').report_action(self)
        return {}
    
    
    
    
    
    