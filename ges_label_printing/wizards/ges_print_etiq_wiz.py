# -*- coding: utf-8 -*-

from odoo import api, fields, models  # , _
from builtins import str
# from datetime import date, timedelta, datetime
# import time
# import calendar
# from dateutil.relativedelta import relativedelta
# from odoo.exceptions import UserError, ValidationError


class GesPrintLabelPurchaseOrderWiz(models.TransientModel):
    _name = "ges.print.label.purchase.order.wiz"
    _description = "Wizard creation of a label from a purchase order and print it"

    po_id = fields.Many2many("purchase.order", string="Purchase order")
    label_to_print_ids = fields.Many2many(
        "ges.print.label.wiz", string="Labels to print")

    def create_print_etiq_purchase_order(self):
        #         self.env.cr.commit()
        for wiz in self.label_to_print_ids:
            if wiz.lot_id:
                lot_name = wiz.lot_id.name
            else:
                lot_name = wiz.po_name
            informations = [
                ("compname", wiz.company_id.name),
                ("compcountry", wiz.company_id.country_id.name),
                ("compstreet", wiz.company_id.street),
                ("compcity", wiz.company_id.city),
                ("compzip", wiz.company_id.zip),
                ("compphone", wiz.company_id.phone),
                ("packdate", wiz.packaging_date),
                ("shipdate", wiz.shipping_date),
                ("product", wiz.product_id.name),
                ("size", wiz.product_id.ges_size_des),
                ("category", wiz.product_id.ges_category_des),
                ("brand", wiz.product_id.ges_brand_des),
                ("barcode", wiz.barcode),
                ("qty", wiz.qty),
                ("weight", wiz.weight),
                ("partname", wiz.partner_id.name),
                ("carrier", wiz.carrier_id.name),
                ("lot", lot_name),
                ("bbd", wiz.bbd),
            ]
            if(wiz.printer_id.realname is not None and wiz.printer_id.realname != "" and wiz.model_id.text_etiq is not None and wiz.model_id.text_etiq != ""):
                wiz.env['di.printing.printing'].printetiquetteonwindows(
                    wiz.printer_id.realname, wiz.model_id.text_etiq, '[', informations, wiz.nblabel)
        return {'type': 'ir.actions.act_window_close'}

    @api.model
    def default_get(self, fields):
        res = super(GesPrintLabelPurchaseOrderWiz, self).default_get(fields)
        labels = self.env['ges.print.label.wiz']
        # on vérifie si on est dans un model
        if self.env.context.get('active_model'):
            # récup du model courant
            active_model = self.env.context['active_model']
        else:
            active_model = ''
        if active_model:
            if active_model == 'purchase.order':  # si lancé à partir des commandes

                #                 labels =[]
                po_id = self.env.context["active_id"]
                po = self.env['purchase.order'].browse(po_id)
                res["po_id"] = [(4, po.id, 0)]

                for pol in po.order_line:
                    if pol.move_ids:
                        for move in pol.move_ids:
                            for ml in move.move_line_ids:
                                if ml.state == 'done':
                                    packaging_date = move.picking_id.date_done.date()
                                    shipping_date = move.picking_id.date_done.date()
                                    quantity = ml.qty_done
                                else:
                                    packaging_date = move.picking_id.scheduled_date.date()
                                    shipping_date = move.picking_id.scheduled_date.date()
                                    quantity = ml.product_uom_qty
#                                     labels.append((0,0,{'packaging_date':packaging_date,'shipping_date':shipping_date,'product_id':pol.product_id.id,'lot_id':ml.lot_id.id and ml.lot_id.id or False,
#                                                 'qty':quantity,'weight':ml.ges_nweight,'partner_id':po.partner_id.id,'printer_id':self.env['ges.print.label.wiz']._default_printer().id,
#                                                 'model_id':self.env['ges.print.label.wiz']._default_model().id,
#                                                 'nblabel':ml.ges_pack}))


#                                 labels = [(0,0,{'packaging_date':packaging_date,'shipping_date':shipping_date,'product_id':pol.product_id.id,'lot_id':ml.lot_id.id and ml.lot_id.id or False,
#                                                 'qty':quantity,'weight':ml.ges_nweight,'partner_id':po.partner_id.id,'printer_id':self.env['ges.print.label.wiz']._default_printer().id,
#                                                 'model_id':self.env['ges.print.label.wiz']._default_model().id,
#                                                 'nblabel':ml.ges_pack})]

                                labels += self.env['ges.print.label.wiz'].create({'packaging_date': packaging_date, 'shipping_date': shipping_date, 'product_id': pol.product_id.id, 'lot_id': ml.lot_id.id and ml.lot_id.id or False,
                                                                                  'qty': quantity, 'weight': ml.ges_nweight, 'partner_id': po.partner_id.id, 'printer_id': self.env['ges.print.label.wiz']._default_printer().id,
                                                                                  'model_id': self.env['ges.print.label.wiz']._default_model().id,
                                                                                  'nblabel': ml.ges_pack and ml.ges_pack or 1})

                    else:
                        packaging_date = po.date_order.date()
                        shipping_date = po.date_order.date()
                        quantity = pol.product_uom_qty
#                         labels.append((0,0,{'packaging_date':packaging_date,'shipping_date':shipping_date,'product_id':pol.product_id.id,'lot_id':po.name,
#                                                 'qty':quantity,'weight':pol.ges_nweight,'partner_id':po.partner_id.id,'printer_id':self.env['ges.print.label.wiz']._default_printer().id,
#                                                 'model_id':self.env['ges.print.label.wiz']._default_model().id,
#                                                 'nblabel':pol.ges_pack,'po_id':po.id}))
#                         labels = [(0,0,{'packaging_date':packaging_date,'shipping_date':shipping_date,'product_id':pol.product_id.id,'lot_id':po.name,
#                                                 'qty':quantity,'weight':pol.ges_nweight,'partner_id':po.partner_id.id,'printer_id':self.env['ges.print.label.wiz']._default_printer().id,
#                                                 'model_id':self.env['ges.print.label.wiz']._default_model().id,
#                                                 'nblabel':pol.ges_pack,'po_id':po.id})]
                        labels += self.env['ges.print.label.wiz'].create({'packaging_date': packaging_date, 'shipping_date': shipping_date, 'product_id': pol.product_id.id, 'lot_id': False, 'po_name': po.name,
                                                                          'qty': quantity, 'weight': pol.ges_nweight, 'partner_id': po.partner_id.id, 'printer_id': self.env['ges.print.label.wiz']._default_printer().id,
                                                                          'model_id': self.env['ges.print.label.wiz']._default_model().id,
                                                                          'nblabel': pol.ges_pack and pol.ges_pack or 1})

#         label_ids=[]
#         if labels:
#             for label in labels:
#                 label_ids.append(label.id)
        if labels:
            res["label_to_print_ids"] = [(6, 0, labels.ids)]

#

        return res


class GesPrintLabelWiz(models.TransientModel):
    _name = "ges.print.label.wiz"
    _description = "Wizard creation of a label and print it"

    @api.onchange("product_id")
    def onchange_product(self):
        self.lot_id = self.env['stock.production.lot']

    @api.depends("product_id")
    def _compute_show_lot(self):
        for wiz in self:
            if wiz.product_id.tracking != 'none' and not wiz.po_name:
                wiz.show_lot = True
            else:
                wiz.show_lot = False

    @api.depends("product_id")
    def _compute_show_po_name(self):
        for wiz in self:
            if wiz.product_id.tracking != 'none' and wiz.po_name:
                wiz.show_po_name = True
            else:
                wiz.show_po_name = False

    @api.depends("product_id")
    def _compute_show_lot_single(self):
        for wiz in self:
            if wiz.product_id.tracking != 'none':
                wiz.show_lot_single = True
            else:
                wiz.show_lot_single = False

    @api.depends("product_id")
    def _compute_show_po_name_single(self):
        for wiz in self:
            if wiz.product_id.tracking != 'none':
                wiz.show_po_name_single = True
            else:
                wiz.show_po_name_single = False

    @api.depends("product_id", "model_id", "lot_id", "bbd", "qty", "weight", "po_name")
    def _compute_barcode(self):
        for wiz in self:
            wiz.barcode = ""
            if wiz.model_id.with_ean128:

                if wiz.product_id.barcode:
                    GS = "\x1D"
                    gtin = "0"+wiz.product_id.barcode
                    barcode = "01" + gtin
                    if wiz.bbd:
                        expiry = wiz.bbd.strftime("%y%m%d")
                        barcode += "17" + expiry
                    if wiz.weight and wiz.weight > 0:
                        weight = round(wiz.weight, 5)
                        weightstr = str(weight)
                        pos = weightstr.find('.')
                        dec = weightstr[pos+1:]
                        if dec == "0":
                            lgdec = 0
                        else:
                            lgdec = len(dec)
                        weight = str(int(weight * (10**lgdec)))
#                         for i in range(6):
#                             if len(weight) != 6:
#                                 weight = "0"+weight
#                             else:
#                                 break
                        while len(weight) < 6:
                            weight = "0"+weight

                        barcode += "310"+str(lgdec) + weight

                    if wiz.qty and wiz.qty > 0:
                        qtystr = str(wiz.qty)
#                         pos = qtystr.find('.')
#                         ent = qtystr[:pos]
#                         barcode += "37" + ent + GS
                        barcode += "37" + qtystr + GS

                    if wiz.lot_id:
                        lot = wiz.lot_id.name
                        barcode += "10" + lot + GS
                    elif wiz.po_name:
                        lot = wiz.po_name
                        barcode += "10" + lot + GS

                    wiz.barcode = barcode
                else:
                    wiz.barcode = ""
            else:
                wiz.barcode = wiz.product_id.barcode and wiz.product_id.barcode or ""

    def _default_printer(self):
        printer = self.env['di.printing.printer'].browse(int(
            self.env['ir.config_parameter'].sudo().get_param('ges_base.ges_default_label_printer')))
        return printer

    def _default_model(self):
        label_model = self.env['di.printing.etiqmodel'].browse(int(
            self.env['ir.config_parameter'].sudo().get_param('ges_base.ges_default_label_model')))
        return label_model

    company_id = fields.Many2one('res.company', string='Company',
                                 readonly=True,  default=lambda self: self.env.user.company_id)
    packaging_date = fields.Date(
        string="Packaging date", default=lambda self: fields.Date.today())
    shipping_date = fields.Date(
        string="Shipping date", default=lambda self: fields.Date.today())
    product_id = fields.Many2one(
        'product.product', string='Product', required=True)
    show_lot = fields.Boolean('Show lot', compute="_compute_show_lot")
    show_po_name = fields.Boolean(
        'Show purchase name as lot', compute="_compute_show_po_name")
    show_lot_single = fields.Boolean(
        'Show lot', compute="_compute_show_lot_single")
    show_po_name_single = fields.Boolean(
        'Show purchase name as lot', compute="_compute_show_po_name_single")
    lot_id = fields.Many2one('stock.production.lot', string='Lot')
    barcode = fields.Char(
        string="Barcode", compute="_compute_barcode", store=True)
    po_name = fields.Char(string="Purchase name")
    qty = fields.Integer(string="Quantity", default=0)
    weight = fields.Float(string="Weight", default=0)
    partner_id = fields.Many2one("res.partner", string='Partner')
    printer_id = fields.Many2one("di.printing.printer", string='Label printer', domain=[
                                 ('isimpetiq', '=', True)], required=True, default=_default_printer)
    model_id = fields.Many2one(
        "di.printing.etiqmodel", string='Label model', required=True, default=_default_model)
    carrier_id = fields.Many2one('delivery.carrier', 'Carrier')
    bbd = fields.Date(string="Best before date",
                      default=lambda self: fields.Date.today())
    nblabel = fields.Integer("Label number", default=1)

    def create_print_etiq(self):
        if self.lot_id:
            lot_name = self.lot_id.name
        else:
            lot_name = self.po_name

        informations = [
            ("compname", self.company_id.name),
            ("compcountry", self.company_id.country_id.name),
            ("compstreet", self.company_id.street),
            ("compcity", self.company_id.city),
            ("compzip", self.company_id.zip),
            ("compphone", self.company_id.phone),
            ("packdate", self.packaging_date),
            ("shipdate", self.shipping_date),
            ("product", self.product_id.name),
            ("size", self.product_id.ges_size_des),
            ("category", self.product_id.ges_category_des),
            ("brand", self.product_id.ges_brand_des),
            ("barcode", self.barcode),
            ("qty", self.qty),
            ("weight", self.weight),
            ("partname", self.partner_id.name),
            ("carrier", self.carrier_id.name),
            ("lot", lot_name),
            ("bbd", self.bbd),
        ]

        if(self.printer_id.realname is not None and self.printer_id.realname != "" and self.model_id.text_etiq is not None and self.model_id.text_etiq != ""):
            self.env['di.printing.printing'].printetiquetteonwindows(
                self.printer_id.realname, self.model_id.text_etiq, '[', informations, self.nblabel)
        return {'type': 'ir.actions.act_window_close'}
#
