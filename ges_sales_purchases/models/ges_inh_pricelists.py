# -*- coding: utf-8 -*-

from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
from odoo import models, fields, api, _
from odoo.tools import float_repr
import xlwt
# from xlsxwriter.workbook import Workbook
import io
import datetime
from odoo.tools import date_utils
import json
# import base64
try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter


class PricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    ges_partner_id = fields.Many2one('res.partner', string='Partner')
    ges_generated = fields.Boolean(string="Generated", default=False)


class Pricelist(models.Model):
    _inherit = "product.pricelist"

    ges_base_pricelist_id = fields.Many2one('product.pricelist', 'Origin pricelist', check_company=True)
    ges_coef = fields.Float(string="Factor", help=""" Factor applied on base price """, digits=(5, 2))

    def _compute_price_rule_get_items(self, products_qty_partner, date, uom_id, prod_tmpl_ids, prod_ids, categ_ids):
        #copie standard
        self.ensure_one()
        # Load all rules
        self.env['product.pricelist.item'].flush(['price', 'currency_id', 'company_id'])
        #print(products_qty_partner)
        partners = [item[2] for item in products_qty_partner]  # ajout contrôle du client
        #print(partners)
        for partner in partners:  # ajout contrôle du client
            #print(partner)
            break  # ajout contrôle du client
        if partner and partner is not True:
            self.env.cr.execute(
                """
                SELECT
                    item.id
                FROM
                    product_pricelist_item AS item
                LEFT JOIN product_category AS categ ON item.categ_id = categ.id
                WHERE
                    (item.product_tmpl_id IS NULL OR item.product_tmpl_id = any(%s))
                    AND (item.product_id IS NULL OR item.product_id = any(%s))
                    AND (item.categ_id IS NULL OR item.categ_id = any(%s))
                    AND (item.pricelist_id = %s)
                    AND (item.date_start IS NULL OR item.date_start<=%s)
                    AND (item.date_end IS NULL OR item.date_end>=%s)
                    AND (item.ges_partner_id IS NULL OR item.ges_partner_id=%s)
                ORDER BY
                    item.applied_on, item.min_quantity desc, categ.complete_name desc, item.id desc
                """,
                (prod_tmpl_ids, prod_ids, categ_ids, self.id, date, date, partner.id))  # ajout contrôle du client
        else:
            self.env.cr.execute(
                """
                SELECT
                    item.id
                FROM
                    product_pricelist_item AS item
                LEFT JOIN product_category AS categ ON item.categ_id = categ.id
                WHERE
                    (item.product_tmpl_id IS NULL OR item.product_tmpl_id = any(%s))
                    AND (item.product_id IS NULL OR item.product_id = any(%s))
                    AND (item.categ_id IS NULL OR item.categ_id = any(%s))
                    AND (item.pricelist_id = %s)
                    AND (item.date_start IS NULL OR item.date_start<=%s)
                    AND (item.date_end IS NULL OR item.date_end>=%s)
                    AND (item.ges_partner_id IS NULL)
                ORDER BY
                    item.applied_on, item.min_quantity desc, categ.complete_name desc, item.id desc
                """,
                (prod_tmpl_ids, prod_ids, categ_ids, self.id, date, date))

        # NOTE: if you change `order by` on that query, make sure it matches
        # _order from model to avoid inconstencies and undeterministic issues.

        item_ids = [x[0] for x in self.env.cr.fetchall()]
        return self.env['product.pricelist.item'].browse(item_ids)


class GesGeneratePricesCoef(models.TransientModel):
    _name = "ges.generate.prices.coef"
    _description = "Generate prices for the selected pricelists with the indicated factor"

    def ges_generate_prices(self):
        pricelists = self.env['product.pricelist'].browse(self._context.get('active_ids', [])).filtered(lambda p: p.ges_base_pricelist_id is not False and p.ges_coef is not False and p.ges_coef != 0)
        pricelists.mapped('item_ids').filtered(lambda item: item.ges_generated is True).unlink()        

        for pricelist in pricelists:
            for itemorig in pricelist.ges_base_pricelist_id.item_ids:
                item = self.env['product.pricelist.item']
                item.create({
                        'applied_on': itemorig.applied_on,
                        'product_id': itemorig.product_id.id,
                        'product_tmpl_id': itemorig.product_tmpl_id.id,
                        'compute_price': itemorig.compute_price,
                        'fixed_price': itemorig.fixed_price * pricelist.ges_coef,
                        'pricelist_id': pricelist.id,
                        'ges_generated': True
                    })


# class GesDiPricelistsByProductWiz(models.TransientModel):
#     _inherit = "di.pricelists.by.product.wiz"

#     def set_product_pricelists(self):
#         date = datetime.date.today().strftime('%d/%m/%Y')
#         product_pricelists = _("""
#         <table class="table table-condensed table-bordered" width="100%">
#             <thead>
#                 <tr>
#                     <th width="100%">
#                         <h3 style="text-align: center">
#                         <span>Prices </span>
#                             <span>From </span>""")
#         product_pricelists = product_pricelists + "<span> %s </span>" % date
#         product_pricelists = product_pricelists + _("""
#                         </h3>
#                     </th>
#                 </tr>
#             </thead>
#         </table>
#         <table class="table table-condensed table-bordered">
#             <thead>
#                 <tr>
#                     <th>Product</th>""")

#         for pricelist in self.pricelist_ids:
#             product_pricelists = product_pricelists+"<th>%s</th>" % pricelist.name

#         product_pricelists = product_pricelists+"""
#             </tr>
#         </thead>
#         <tbody>
#         """
#         if not self.categ_ids:
#             products = self.env['product.product'].search([('qty_available', '>', 0)]).sorted(lambda p: (p.categ_id.parent_id.name and p.categ_id.parent_id.name or 'zzzzzzzzzzzzz', p.name))
#         else:
#             products = self.env['product.product'].search([('categ_id', 'in', self.categ_ids.ids), ('qty_available', '>', 0)]).sorted(lambda p: (p.categ_id.parent_id.name and p.categ_id.parent_id.name or 'zzzzzzzzzzzzz', p.name))
#         categ_name = ""
#         for product in products:
#             if product.categ_id.parent_id:
#                 if categ_name != product.categ_id.parent_id.name:
#                     product_pricelists = product_pricelists+"<tr><td><b>%s</b></td></tr>" % product.categ_id.parent_id.name
#                     categ_name = product.categ_id.parent_id.name
#             else:
#                 if categ_name != "":
#                     product_pricelists = product_pricelists+"<tr><td><b></b></td></tr>"
#                     categ_name = ""
#             product_pricelists = product_pricelists+"<tr><td>%s</td>" % product.name
#             for pricelist in self.pricelist_ids:
#                 product_pricelist = self.env['di.pricelist.product.rel'].search(['&', ('product_id', '=', product.id), ('pricelist_id', '=', pricelist.id), ('ges_partner_id', '=', False)], limit=1)
#                 date_bidon = datetime.datetime(1900, 1, 1).date()
#                 standard_price = round(pricelist.get_product_price(product, 0, False, date_bidon), 2)
#                 pricelist_price = round(product_pricelist.price, 2)
#                 if standard_price != pricelist_price and (product_pricelist.date_start or product_pricelist.date_end):
#                     product_pricelists = product_pricelists+"<td><div>%s" % "{:.2f}".format(pricelist_price)
#                     product_pricelists = product_pricelists+" %s" % pricelist.currency_id.symbol
#                     if not product_pricelist.date_start:
#                         product_pricelists = product_pricelists+_(" from 01/01/1900")
#                     else:
#                         product_pricelists = product_pricelists+_(" from %s") % product_pricelist.date_start.strftime("%d/%m/%Y")
#                     if not product_pricelist.date_end:
#                         product_pricelists = product_pricelists+_(" to 31/12/9999 </div>")
#                     else:
#                         product_pricelists = product_pricelists+_(" to %s </div>") % product_pricelist.date_end.strftime("%d/%m/%Y")
#                     product_pricelists = product_pricelists+_("<div>else %s %s</div></td>") % ("{:.2f}".format(standard_price), pricelist.currency_id.symbol)
#                 else:
#                     product_pricelists = product_pricelists+"<td>%s %s</td>" % ("{:.2f}".format(pricelist_price), pricelist.currency_id.symbol)
#             product_pricelists = product_pricelists+"</tr>"

#         product_pricelists = product_pricelists+"""
#             </tbody>
#         </table>"""
#         self.product_pricelists = product_pricelists

#     def get_xlsx_report(self, data, response):
    
#         output = io.BytesIO()
# #         wb = xlwt.Workbook(output, {'in_memory': True})
#         workbook = xlsxwriter.Workbook(output, {'in_memory': True})
#         lines = self.browse(data['ids'])
#         categ_ids = lines.categ_ids
#         pricelist_ids = lines.pricelist_ids


# #         sheet = wb.add_worksheet('Product pricelists')
# #
# #         format0 = wb.add_format({'font_size': 20, 'align': 'center', 'bold': True})
# #         format1 = wb.add_format({'font_size': 14, 'align': 'vcenter', 'bold': True})
# #         format11 = wb.add_format({'font_size': 12, 'align': 'center', 'bold': True})
# #         format21 = wb.add_format({'font_size': 10, 'align': 'center', 'bold': False})
# #         format3 = wb.add_format({'bottom': True, 'top': True, 'font_size': 12})
# #         format4 = wb.add_format({'font_size': 12, 'align': 'left', 'bold': True})
# #         font_size_8 = wb.add_format({'font_size': 8, 'align': 'center'})
# #         font_size_8_l = wb.add_format({'font_size': 8, 'align': 'left'})
# #         font_size_8_r = wb.add_format({'font_size': 8, 'align': 'right'})
# #         red_mark = wb.add_format({'font_size': 8, 'bg_color': 'red'})
# #         justify = wb.add_format({'font_size': 12})

#         sheet = workbook.add_worksheet(_('Product pricelists'))

#         format0 = workbook.add_format(
#             {'font_size': 20, 'align': 'center', 'bold': True})
#         format1 = workbook.add_format(
#             {'font_size': 14, 'align': 'vcenter', 'bold': True})
#         format11 = workbook.add_format(
#             {'font_size': 12, 'align': 'center', 'bold': True})
#         format20 = workbook.add_format(
#             {'font_size': 10, 'align': 'left', 'bold': False})
#         format21 = workbook.add_format(
#             {'font_size': 10, 'align': 'center', 'bold': False})
#         format22 = workbook.add_format(
#             {'font_size': 10, 'align': 'left', 'bold': True})
#         format23 = workbook.add_format(
#             {'font_size': 10, 'align': 'right', 'bold': False})
#         format3 = workbook.add_format(
#             {'bottom': True, 'top': True, 'font_size': 12})
#         format4 = workbook.add_format(
#             {'font_size': 12, 'align': 'left', 'bold': True})
#         font_size_8 = workbook.add_format({'font_size': 8, 'align': 'center'})
#         font_size_8_l = workbook.add_format({'font_size': 8, 'align': 'left'})
#         font_size_8_r = workbook.add_format({'font_size': 8, 'align': 'right'})
#         red_mark = workbook.add_format({'font_size': 8, 'bg_color': 'red'})
#         justify = workbook.add_format({'font_size': 12})
#         format3.set_align('center')
#         justify.set_align('justify')
#         format1.set_align('center')
#         red_mark.set_align('center')

#         sheet.merge_range(2, 1, 2, 5, _('Product pricelists'), format0)
#         col_max_width = {}
#         sheet.write(4, 1, _('Product'), format11)
#         col_max_width[1] = len(_('Product'))
#         sheet.write(4, 2, _('Stock'), format11)
#         col_max_width[2] = len(_('Stock'))
#         sheet.write(4, 3, _('Unit'), format11)
#         col_max_width[3] = len(_('Unit'))
        
# #         sheet.merge_range(4,1,4,1,'Product',format0)

#         col = 4
#         for pricelist in pricelist_ids:
#             sheet.write(4, col, pricelist.name, format11)
#             col_max_width[col] = len(pricelist.name)
# #             sheet.merge_range(4,col,4,col,pricelist.name,format11)
#             col = col+1

# #         sheet.merge_range(4,4,1,1,'Product',style)
#         if not categ_ids:
#             products = self.env['product.product'].search([('qty_available', '>', 0)]).sorted(lambda p: (p.categ_id.parent_id.name and p.categ_id.parent_id.name or 'zzzzzzzzzzzzz', p.name))
#         else:
#             products = self.env['product.product'].search([('categ_id', 'in', categ_ids.ids), ('qty_available', '>', 0)]).sorted(lambda p: (p.categ_id.parent_id.name and p.categ_id.parent_id.name or 'zzzzzzzzzzzzz', p.name))

#         row = 5
#         categ_name = ""
        
#         for product in products:

#             if product.categ_id.parent_id:
#                 if categ_name != product.categ_id.parent_id.name:
#                     categ_name = product.categ_id.parent_id.name
#                     sheet.write(row, 1, product.categ_id.parent_id.name, format22)
#                     row = row+1
#             else:
#                 if categ_name != "":
#                     categ_name = ""
#                     row = row+1

#             sheet.write(row, 1, product.name, format20)
#             if col_max_width[1] < len(product.name):
#                 col_max_width[1] = len(product.name)

#             sheet.write(row, 2, str("{:.3f}".format(product.qty_available)), format21)
#             if col_max_width[2] < len(str("{:.3f}".format(product.qty_available))):
#                 col_max_width[2] = len(str("{:.3f}".format(product.qty_available)))

#             sheet.write(row, 3, product.uom_id.name, format21)
#             if col_max_width[3] < len(product.uom_id.name):
#                 col_max_width[3] = len(product.uom_id.name)

            

# #             sheet.merge_range(row,1,row,1,product.name,format21)
#             col = 4
#             for pricelist in pricelist_ids:
#                 product_pricelist = self.env['di.pricelist.product.rel'].search(['&', ('product_id', '=', product.id), ('pricelist_id', '=', pricelist.id),], limit=1)
                
#                 pricestr = str("{:.2f}".format(product_pricelist.price)) + pricelist.currency_id.symbol
#                 sheet.write(row, col, pricestr, format23)
#                 if col_max_width[col] < len(pricestr):
#                     col_max_width[col] = len(pricestr)
# #todo
#                 #  date_bidon = datetime.datetime(1900, 1, 1).date()
#                 # standard_price = round(pricelist.get_product_price(product, 0, False, date_bidon), 2)
#                 # pricelist_price = round(product_pricelist.price, 2)
#                 # if standard_price != pricelist_price:
#                 #     product_pricelists = product_pricelists+"<td><div>%s" % pricelist_price
#                 #     product_pricelists = product_pricelists+" from %s" % product_pricelist.date_start.strftime("%d/%m/%Y")
#                 #     product_pricelists = product_pricelists+" to %s </div>" % product_pricelist.date_end.strftime("%d/%m/%Y")
#                 #     product_pricelists = product_pricelists+"<div>else %s </div></td>" % standard_price
#                 # else:
#                 #     product_pricelists = product_pricelists+"<td>%s</td>" % pricelist_price
# #                 sheet.merge_range(row,col,row,col,product_pricelist.price,format21)
#                 col = col+1
#             row = row+1

#         for colf, widthf in col_max_width.items():
#             sheet.set_column(colf, colf, widthf)
#         workbook.close()
# #         wb.close()
#         output.seek(0)
#         generated_file = output.read()
# #         response.stream.write(output.read())
#         output.close()
#         return generated_file