# -*- coding: utf-8 -*-

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


class DiPricelistProductRel(models.Model):
    _name = "di.pricelist.product.rel"
    _description = "Link between pricelists and products"

    company_id = fields.Many2one('res.company', string='Company',
                                 readonly=True,  default=lambda self: self.env.user.company_id)
    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist')
    product_id = fields.Many2one('product.product', string='Product')
    price = fields.Float('Price', digits='Product Price')
    date_start = fields.Date('Start Date')
    date_end = fields.Date('End Date')


class ProductTemplate(models.Model):
    _inherit = "product.template"

    di_pricelist_item_count = fields.Integer(
        "Number of price rules", compute="_di_compute_item_count")

    def _di_compute_item_count(self):
        for template in self:
            # Pricelist item count counts the rules applicable on current template or on its variants.
            template.di_pricelist_item_count = template.env['di.pricelist.product.rel'].search_count(['&',
                                                                                                      ('product_id', 'in', template.product_variant_ids.ids), ('pricelist_id', '!=', False)])

    def di_open_pricelists(self):
        self.ensure_one()
        domain = ['&',
                  ('product_id', 'in', self.product_variant_ids.ids),
                  ('pricelist_id', '!=', False)]
        return {
            'name': _('Pricelists'),
            'view_mode': 'tree,form',
            'views': [(self.env.ref('product_pricelist_show_all.di_pricelist_product_rel_tree_view').id, 'tree'), (False, 'form')],
            'res_model': 'di.pricelist.product.rel',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': domain,
        }

    def open_pricelist_rules(self):
        self.ensure_one()
        res = super(ProductTemplate, self).open_pricelist_rules()
        res['domain'] = ['|', '|', '|',
                         ('product_tmpl_id', '=', self.id),
                         ('product_id', 'in', self.product_variant_ids.ids),
                         ('categ_id', '=', self.categ_id.id),
                         ('applied_on', '=', '3_global')
                         ]
        return res

    def _compute_item_count(self):
        for template in self:
            # Pricelist item count counts the rules applicable on current template or on its variants.
            template.pricelist_item_count = template.env['product.pricelist.item'].search_count([
                '|', '|', '|', ('product_tmpl_id', '=', template.id), ('product_id', 'in', template.product_variant_ids.ids), ('categ_id', '=', template.categ_id.id), ('applied_on', '=', '3_global')])


class ProductProduct(models.Model):
    _inherit = "product.product"

    def product_specialoffer(self, start_date_found, end_date_found, price_found, pricelist, product):
        if start_date_found or end_date_found:
            date_bidon = datetime.datetime(1900, 1, 1).date()
            promo_price = round(price_found, 2)
            standard_price = round(pricelist.get_product_price(product, 0, False, date_bidon), 2)
            if promo_price != standard_price:
                return((start_date_found.strftime("%d/%m/%Y"), end_date_found.strftime("%d/%m/%Y"), standard_price))
        return(False)

    di_pricelists = fields.One2many(
        "di.pricelist.product.rel",
        "product_id",
        string="Pricelists")

    di_pricelist_item_count = fields.Integer(
        "Number of price rules", compute="_di_compute_variant_item_count")

    def _di_compute_variant_item_count(self):
        for product in self:
            domain = ['&', ('product_id', '=', product.id),
                      ('pricelist_id', '!=', False)]
            product.di_pricelist_item_count = self.env['di.pricelist.product.rel'].search_count(
                domain)

    def di_open_pricelists(self):
        self.ensure_one()

        domain = ['&',
                  ('product_id', '=', self.id),
                  ('pricelist_id', '!=', False)]
        return {
            'name': _('Pricelists'),
            'view_mode': 'tree,form',
            'views': [(self.env.ref('product_pricelist_show_all.di_pricelist_product_rel_tree_view').id, 'tree'), (False, 'form')],
            'res_model': 'di.pricelist.product.rel',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': domain,

        }

    def _compute_variant_item_count(self):
        for product in self:
            domain = ['|', '|', '|',
                      '&', ('product_tmpl_id', '=',
                            product.product_tmpl_id.id), ('applied_on', '=', '1_product'),
                      '&', ('product_id', '=', product.id), ('applied_on',
                                                             '=', '0_product_variant'),
                      ('categ_id', '=', self.categ_id.id),
                      ('applied_on', '=', '3_global')
                      ]
            product.pricelist_item_count = self.env['product.pricelist.item'].search_count(
                domain)

    def open_pricelist_rules(self):
        self.ensure_one()
        res = super(ProductProduct, self).open_pricelist_rules()
        res['domain'] = ['|', '|', '|',
                         '&', ('product_tmpl_id', '=',
                               self.product_tmpl_id.id), ('applied_on', '=', '1_product'),
                         '&', ('product_id', '=', self.id), ('applied_on',
                                                             '=', '0_product_variant'),
                         ('categ_id', '=', self.categ_id.id),
                         ('applied_on', '=', '3_global')
                         ]
        return res


class Pricelist(models.Model):
    _inherit = "product.pricelist"

    @api.depends('item_ids')
    def _di_compute_products(self):
        if self.env.user.has_group('product.group_sale_pricelist'):
            for pricelist in self:
                if pricelist:
                    pricelist.di_products = [(5, 0, 0)]
                    products_tmpl = pricelist.item_ids.mapped("product_tmpl_id")
                    products = self.env['product.product'].search([('product_tmpl_id', 'in', products_tmpl.ids)])
                    # products = self.env['product.product']
                    # products = self.env['product.product'].search([('qty_available', '>', 0)])
                    for product in products:
                        if product:
                            price_rule = pricelist.get_product_price_rule(product, 0, False)
                            rule_id = price_rule[1]
                            rule = self.env['product.pricelist.item'].browse(rule_id)
                            if rule:
                                pricelist.di_products = [(0, 0, {'company_id': pricelist.company_id.id, 'pricelist_id': pricelist.id, 'product_id': product.id, 'price': price_rule[0], 'date_start': rule.date_start, 'date_end': rule.date_end})]
                            else:
                                pricelist.di_products = [(0, 0, {'company_id': pricelist.company_id.id, 'pricelist_id': pricelist.id, 'product_id': product.id, 'price': price_rule[0]})]

    di_products = fields.One2many(
        "di.pricelist.product.rel",
        "pricelist_id",
        string="Products",
        compute="_di_compute_products",
        store=True)


class DiPricelistsByProductViewWiz(models.TransientModel):
    _name = "di.pricelists.by.product.view.wiz"
    _description = "Wizard to show pricelists by product"

    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    product_pricelists = fields.Html(string="Product pricelists")

    @api.model
    def default_get(self, fields):
        res = super(DiPricelistsByProductViewWiz, self).default_get(fields)
        wiz = self.env['di.pricelists.by.product.wiz'].browse(
            self.env.context.get('active_id'))
        res['product_pricelists'] = wiz.product_pricelists
        return res


class DiPricelistsByProductWiz(models.TransientModel):
    _name = "di.pricelists.by.product.wiz"
    _description = "Wizard to show pricelists by product"

    categ_ids = fields.Many2many(
        'product.category', string="Product category", help="If not completed, select all products")
    pricelist_ids = fields.Many2many(
        'product.pricelist', string="Pricelists", required=True)

    product_pricelists = fields.Html(string="Product pricelists")
#     export_data = fields.Binary('Data', readonly=True)
#     filename = fields.Char(string='Filename', size=256, readonly=True)

    def set_product_pricelists(self):
        date = datetime.date.today().strftime('%d/%m/%Y')
        product_pricelists = _("""
        <table class="table table-condensed table-bordered" width="100%">
            <thead>
                <tr>
                    <th width="100%">
                        <h3 style="text-align: center">
                        <span>Prices </span>
                            <span>From </span>""")
        product_pricelists = product_pricelists + "<span> %s </span>" % date
        product_pricelists = product_pricelists + _("""
                        </h3>
                    </th>
                </tr>
            </thead>
        </table>
        <table class="table table-condensed table-bordered">
            <thead>
                <tr>
                    <th>Product</th>""")

        for pricelist in self.pricelist_ids:
            pricelist.env.add_to_compute(pricelist._fields['di_products'], pricelist.search([]))
            product_pricelists = product_pricelists+"<th>%s</th>" % pricelist.name

        product_pricelists = product_pricelists+"""
            </tr>
        </thead>
        <tbody>
        """
        if not self.categ_ids:
            products = self.env['product.product'].search([('qty_available', '>', 0)]).sorted(lambda p: (p.categ_id.parent_id.name and p.categ_id.parent_id.name or 'zzzzzzzzzzzzz', p.name))
        else:
            products = self.env['product.product'].search([('categ_id', 'in', self.categ_ids.ids), ('qty_available', '>', 0)]).sorted(lambda p: (p.categ_id.parent_id.name and p.categ_id.parent_id.name or 'zzzzzzzzzzzzz', p.name))
        categ_name = ""
        for product in products:
            if product.categ_id.parent_id:
                if categ_name != product.categ_id.parent_id.name:
                    product_pricelists = product_pricelists+"<tr><td><b>%s</b></td></tr>" % product.categ_id.parent_id.name
                    categ_name = product.categ_id.parent_id.name
            else:
                if categ_name != "":
                    product_pricelists = product_pricelists+"<tr><td><b></b></td></tr>"
                    categ_name = ""
            product_pricelists = product_pricelists+"<tr><td>%s</td>" % product.name
            for pricelist in self.pricelist_ids:
                product_pricelist = self.env['di.pricelist.product.rel'].search(['&', ('product_id', '=', product.id), ('pricelist_id', '=', pricelist.id)], limit=1)
                date_bidon = datetime.datetime(1900, 1, 1).date()
                standard_price = round(pricelist.get_product_price(product, 0, False, date_bidon), 2)
                pricelist_price = round(product_pricelist.price, 2)
                if standard_price != pricelist_price and (product_pricelist.date_start or product_pricelist.date_end):
                    product_pricelists = product_pricelists+"<td><div>%s" % "{:.2f}".format(pricelist_price)
                    product_pricelists = product_pricelists+" %s" % pricelist.currency_id.symbol
                    if not product_pricelist.date_start:
                        product_pricelists = product_pricelists+_(" from 01/01/1900")
                    else:
                        product_pricelists = product_pricelists+_(" from %s") % product_pricelist.date_start.strftime("%d/%m/%Y")
                    if not product_pricelist.date_end:
                        product_pricelists = product_pricelists+_(" to 31/12/9999 </div>")
                    else:
                        product_pricelists = product_pricelists+_(" to %s </div>") % product_pricelist.date_end.strftime("%d/%m/%Y")
                    product_pricelists = product_pricelists+_("<div>else %s %s</div></td>") % ("{:.2f}".format(standard_price), pricelist.currency_id.symbol)
                else:
                    product_pricelists = product_pricelists+"<td>%s %s</td>" % ("{:.2f}".format(pricelist_price), pricelist.currency_id.symbol)
            product_pricelists = product_pricelists+"</tr>"

        product_pricelists = product_pricelists+"""
            </tbody>
        </table>"""
        self.product_pricelists = product_pricelists

    def view_product_pricelists(self):
        if self.pricelist_ids:
            self.set_product_pricelists()
            if self.product_pricelists:
                #             return self.env.ref('product_pricelist_show_all.di_action_pricelists_by_product_view')
                return {
                    'name': 'Pricelists by product',
                    'view_mode': 'form',
                    'view_id': self.env.ref('product_pricelist_show_all.di_pricelists_by_product_form_wiz').id,
                    'res_model': 'di.pricelists.by.product.view.wiz',
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                }
        else:
            return False

    def print_product_pricelists(self):
        self.set_product_pricelists()
        if self.pricelist_ids:
            return self.env.ref('product_pricelist_show_all.di_action_report_product_pricelists').report_action(self)
        else:
            return False

    def export_product_pricelists(self):
        #         self.set_product_pricelists()

        data = {
            'ids': self.ids,
            'model': self._name,
            'pricelist_ids': self.pricelist_ids,
            'categ_ids': self.categ_ids,
        }
        return {
            'type': 'ir.actions.report',
            'data': {'model': 'di.pricelists.by.product.wiz',
                     'options': json.dumps(data, default=date_utils.json_default),
                     'output_format': 'xlsx',
                     'report_name': _('Product pricelists'),
                     },
            'report_type': 'xlsx'
        }

    def get_xlsx_report(self, data, response):

        output = io.BytesIO()
#         wb = xlwt.Workbook(output, {'in_memory': True})
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        lines = self.browse(data['ids'])
        categ_ids = lines.categ_ids
        pricelist_ids = lines.pricelist_ids


#         sheet = wb.add_worksheet('Product pricelists')
#
#         format0 = wb.add_format({'font_size': 20, 'align': 'center', 'bold': True})
#         format1 = wb.add_format({'font_size': 14, 'align': 'vcenter', 'bold': True})
#         format11 = wb.add_format({'font_size': 12, 'align': 'center', 'bold': True})
#         format21 = wb.add_format({'font_size': 10, 'align': 'center', 'bold': False})
#         format3 = wb.add_format({'bottom': True, 'top': True, 'font_size': 12})
#         format4 = wb.add_format({'font_size': 12, 'align': 'left', 'bold': True})
#         font_size_8 = wb.add_format({'font_size': 8, 'align': 'center'})
#         font_size_8_l = wb.add_format({'font_size': 8, 'align': 'left'})
#         font_size_8_r = wb.add_format({'font_size': 8, 'align': 'right'})
#         red_mark = wb.add_format({'font_size': 8, 'bg_color': 'red'})
#         justify = wb.add_format({'font_size': 12})

        sheet = workbook.add_worksheet(_('Product pricelists'))

        format0 = workbook.add_format(
            {'font_size': 20, 'align': 'center', 'bold': True})
        format1 = workbook.add_format(
            {'font_size': 14, 'align': 'vcenter', 'bold': True})
        format11 = workbook.add_format(
            {'font_size': 12, 'align': 'center', 'bold': True})
        format20 = workbook.add_format(
            {'font_size': 10, 'align': 'left', 'bold': False})
        format21 = workbook.add_format(
            {'font_size': 10, 'align': 'center', 'bold': False})
        format22 = workbook.add_format(
            {'font_size': 10, 'align': 'left', 'bold': True})
        format23 = workbook.add_format(
            {'font_size': 10, 'align': 'right', 'bold': False})
        format3 = workbook.add_format(
            {'bottom': True, 'top': True, 'font_size': 12})
        format4 = workbook.add_format(
            {'font_size': 12, 'align': 'left', 'bold': True})
        font_size_8 = workbook.add_format({'font_size': 8, 'align': 'center'})
        font_size_8_l = workbook.add_format({'font_size': 8, 'align': 'left'})
        font_size_8_r = workbook.add_format({'font_size': 8, 'align': 'right'})
        red_mark = workbook.add_format({'font_size': 8, 'bg_color': 'red'})
        justify = workbook.add_format({'font_size': 12})
        format3.set_align('center')
        justify.set_align('justify')
        format1.set_align('center')
        red_mark.set_align('center')

        sheet.merge_range(2, 1, 2, 5, _('Product pricelists'), format0)
        col_max_width = {}
        sheet.write(4, 1, _('Product'), format11)
        col_max_width[1] = len(_('Product'))
        sheet.write(4, 2, _('Stock'), format11)
        col_max_width[2] = len(_('Stock'))
        sheet.write(4, 3, _('Unit'), format11)
        col_max_width[3] = len(_('Unit'))
        
#         sheet.merge_range(4,1,4,1,'Product',format0)

        col = 4
        for pricelist in pricelist_ids:
            pricelist.env.add_to_compute(pricelist._fields['di_products'], pricelist.search([]))
            sheet.write(4, col, pricelist.name, format11)
            col_max_width[col] = len(pricelist.name)
#             sheet.merge_range(4,col,4,col,pricelist.name,format11)
            col = col+1

#         sheet.merge_range(4,4,1,1,'Product',style)
        if not categ_ids:
            products = self.env['product.product'].search([('qty_available', '>', 0)]).sorted(lambda p: (p.categ_id.parent_id.name and p.categ_id.parent_id.name or 'zzzzzzzzzzzzz', p.name))
        else:
            products = self.env['product.product'].search([('categ_id', 'in', categ_ids.ids), ('qty_available', '>', 0)]).sorted(lambda p: (p.categ_id.parent_id.name and p.categ_id.parent_id.name or 'zzzzzzzzzzzzz', p.name))

        row = 5
        categ_name = ""
        
        for product in products:

            if product.categ_id.parent_id:
                if categ_name != product.categ_id.parent_id.name:
                    categ_name = product.categ_id.parent_id.name
                    sheet.write(row, 1, product.categ_id.parent_id.name, format22)
                    row = row+1
            else:
                if categ_name != "":
                    categ_name = ""
                    row = row+1

            sheet.write(row, 1, product.name, format20)
            if col_max_width[1] < len(product.name):
                col_max_width[1] = len(product.name)

            sheet.write(row, 2, str("{:.3f}".format(product.qty_available)), format21)
            if col_max_width[2] < len(str("{:.3f}".format(product.qty_available))):
                col_max_width[2] = len(str("{:.3f}".format(product.qty_available)))

            sheet.write(row, 3, product.uom_id.name, format21)
            if col_max_width[3] < len(product.uom_id.name):
                col_max_width[3] = len(product.uom_id.name)

            

#             sheet.merge_range(row,1,row,1,product.name,format21)
            col = 4
            for pricelist in pricelist_ids:
                product_pricelist = self.env['di.pricelist.product.rel'].search(['&', ('product_id', '=', product.id), ('pricelist_id', '=', pricelist.id)], limit=1)
                
                pricestr = str("{:.2f}".format(product_pricelist.price)) + pricelist.currency_id.symbol
                sheet.write(row, col, pricestr, format23)
                if col_max_width[col] < len(pricestr):
                    col_max_width[col] = len(pricestr)
#todo
                #  date_bidon = datetime.datetime(1900, 1, 1).date()
                # standard_price = round(pricelist.get_product_price(product, 0, False, date_bidon), 2)
                # pricelist_price = round(product_pricelist.price, 2)
                # if standard_price != pricelist_price:
                #     product_pricelists = product_pricelists+"<td><div>%s" % pricelist_price
                #     product_pricelists = product_pricelists+" from %s" % product_pricelist.date_start.strftime("%d/%m/%Y")
                #     product_pricelists = product_pricelists+" to %s </div>" % product_pricelist.date_end.strftime("%d/%m/%Y")
                #     product_pricelists = product_pricelists+"<div>else %s </div></td>" % standard_price
                # else:
                #     product_pricelists = product_pricelists+"<td>%s</td>" % pricelist_price
#                 sheet.merge_range(row,col,row,col,product_pricelist.price,format21)
                col = col+1
            row = row+1

        for colf, widthf in col_max_width.items():
            sheet.set_column(colf, colf, widthf)
        workbook.close()
#         wb.close()
        output.seek(0)
        generated_file = output.read()
#         response.stream.write(output.read())
        output.close()
        return generated_file


class DiPricelistsPrintWiz(models.TransientModel):
    _name = "di.pricelists.print.wiz"
    _description = "Wizard to print pricelists"

    # @api.depends("pricelist_ids")
    # def _compute_pricelist_ids(self):
    #     for wiz in self:
    #         wiz.pricelist_ids_ids = wiz.pricelist_ids.ids

    pricelist_ids = fields.Many2many('product.pricelist', string="Pricelists", required=True)
    # pricelist_ids_ids = fields.Char(string="Pricelists ids", compute="_compute_pricelist_ids")
    partner_ids = fields.Many2many('res.partner', string="Partners")  # , domain="[('di_pricelist_id', 'in', pricelist_ids.ids)]")
    prices_type = fields.Selection(selection=[("general", "General"), ("partner", "Partner"), ("general_promo", "General (Promo only)"), ("partner_promo", "Partner (Promo only)")], string="Prices type", default="general")

    @api.model
    def default_get(self, fields):
        res = super(DiPricelistsPrintWiz, self).default_get(fields)
        pricelists = self.env['product.pricelist'].browse(self.env.context.get('active_ids'))
        res['pricelist_ids'] = pricelists
        return res

    def print_pricelists(self):
        if self.prices_type == 'general':
            return self.env.ref('product_pricelist_show_all.di_action_report_print_pricelists_general').report_action(self)
        elif self.prices_type == 'partner':
            if not self.partner_ids:
                self.partner_ids = self.env['res.partner'].search([('di_pricelist_id', 'in', self.pricelist_ids.ids)])
            else:
                self.partner_ids = self.partner_ids.filtered(lambda p: p.di_pricelist_id in self.pricelist_ids.ids)
            return self.env.ref('product_pricelist_show_all.di_action_report_print_pricelists_partner').report_action(self)
        elif self.prices_type == 'general_promo':
            return self.env.ref('product_pricelist_show_all.di_action_report_print_pricelists_general_promo').report_action(self)
        elif self.prices_type == 'partner_promo':
            if not self.partner_ids:
                self.partner_ids = self.env['res.partner'].search([('di_pricelist_id', 'in', self.pricelist_ids.ids)])
            else:
                self.partner_ids = self.partner_ids.filtered(lambda p: p.di_pricelist_id in self.pricelist_ids.ids)
            return self.env.ref('product_pricelist_show_all.di_action_report_print_pricelists_partner_promo').report_action(self)
