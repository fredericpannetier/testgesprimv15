
# -*- coding: utf-8 -*-
from odoo.exceptions import UserError, ValidationError
from odoo import models, fields, api, _
from functools import partial
from odoo.tools.misc import formatLang, get_lang


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def di_get_texts(self, edittype):
        texts = []

        for p in self:
            if p.categ_id.ids:
                query = """ select n.text 
                                from di_default_note n                          
                                where n.item in ('product','productcat') 
                                and ((n.item = 'product' and n.product_id =   %(product_id)s )  or (n.item = 'productcat' and n.productcat_id in %(productcat_ids)s ) )                                                         
                                order by n.item                                                                                                         
                            """
                query_args = {'product_id': p.id,
                              'productcat_ids': tuple(p.categ_id.ids)}
            else:
                query = """ select n.text 
                                from di_default_note n                          
                                where n.item in ('product','productcat') 
                                and ((n.item = 'product' and n.product_id =   %(product_id)s ) )                                                         
                                order by n.item                                                                                                          
                            """
                query_args = {'product_id': p.id}

            self.env.cr.execute(query, query_args)
            for r in self.env.cr.fetchall():
                texts.append(r[0])
        return texts


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def di_get_texts(self):
        texts = []
        for order in self:
            if order.partner_id.category_id.ids:
                query = """ select n.text 
                                from di_default_note n                          
                                where n.item in ('company','partner','partnertag') 
                                and n.so_print is true
                                and ((n.item = 'company' and n.company_id =   %(company_id)s ) or (n.item = 'partner' and n.partner_id = %(partner_id)s ) or (n.item = 'partnertag' and n.partnertag_id in %(partnertag_ids)s ) )                                                         
                                order by n.item                                                                                                         
                            """
                query_args = {'company_id': order.company_id.id, 'partner_id': order.partner_id.id,
                              'partnertag_ids': tuple(order.partner_id.category_id.ids)}
            else:
                query = """ select n.text 
                                from di_default_note n                          
                                where n.item in ('company','partner','partnertag')
                                and n.so_print is true 
                                and ((n.item = 'company' and n.company_id =   %(company_id)s ) or (n.item = 'partner' and n.partner_id = %(partner_id)s ) )                                                         
                                order by n.item                                                                                                         
                            """
                query_args = {'company_id': order.company_id.id,
                              'partner_id': order.partner_id.id}

            self.env.cr.execute(query, query_args)
            for r in self.env.cr.fetchall():
                texts.append(r[0])
        return texts


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def di_get_texts(self):
        texts = []
        for line in self:
            if line.product_id.categ_id.ids:
                query = """ select n.text 
                                from di_default_note n                          
                                where n.item in ('product','productcat') 
                                and n.so_print is true
                                and ((n.item = 'product' and n.product_id =   %(product_id)s )  or (n.item = 'productcat' and n.productcat_id in %(productcat_ids)s ) )                                                         
                                order by n.item                                                                                                         
                            """
                query_args = {'product_id': line.product_id.id,
                              'productcat_ids': tuple(line.product_id.categ_id.ids)}
            else:
                query = """ select n.text 
                                from di_default_note n                          
                                where n.item in ('product','productcat') 
                                and n.so_print is true
                                and ((n.item = 'product' and n.product_id =   %(product_id)s ) )                                                         
                                order by n.item                                                                                                          
                            """
                query_args = {'product_id': line.product_id.id}

            self.env.cr.execute(query, query_args)
            for r in self.env.cr.fetchall():
                texts.append(r[0])
        return texts


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def di_get_texts(self):
        texts = []
        for order in self:
            if order.partner_id.category_id.ids:
                query = """ select n.text 
                                from di_default_note n                          
                                where n.item in ('company','partner','partnertag') 
                                and n.po_print is true
                                and ((n.item = 'company' and n.company_id =   %(company_id)s ) or (n.item = 'partner' and n.partner_id = %(partner_id)s ) or (n.item = 'partnertag' and n.partnertag_id in %(partnertag_ids)s ) )                                                         
                                order by n.item                                                                                                         
                            """
                query_args = {'company_id': order.company_id.id, 'partner_id': order.partner_id.id,
                              'partnertag_ids': tuple(order.partner_id.category_id.ids)}
            else:
                query = """ select n.text 
                                from di_default_note n                          
                                where n.item in ('company','partner','partnertag')
                                and n.po_print is true 
                                and ((n.item = 'company' and n.company_id =   %(company_id)s ) or (n.item = 'partner' and n.partner_id = %(partner_id)s ) )                                                         
                                order by n.item                                                                                                         
                            """
                query_args = {'company_id': order.company_id.id,
                              'partner_id': order.partner_id.id}

            self.env.cr.execute(query, query_args)
            for r in self.env.cr.fetchall():
                texts.append(r[0])
        return texts


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def di_get_texts(self):
        texts = []
        for line in self:
            if line.product_id.categ_id.ids:
                query = """ select n.text 
                                from di_default_note n                          
                                where n.item in ('product','productcat')
                                and n.po_print is true 
                                and ((n.item = 'product' and n.product_id =   %(product_id)s )  or (n.item = 'productcat' and n.productcat_id in %(productcat_ids)s ) )                                                         
                                order by n.item                                                                                                         
                            """
                query_args = {'product_id': line.product_id.id,
                              'productcat_ids': tuple(line.product_id.categ_id.ids)}
            else:
                query = """ select n.text 
                                from di_default_note n                          
                                where n.item in ('product','productcat')
                                and n.po_print is true 
                                and ((n.item = 'product' and n.product_id =   %(product_id)s ) )                                                         
                                order by n.item                                                                                                          
                            """
                query_args = {'product_id': line.product_id.id}

            self.env.cr.execute(query, query_args)
            for r in self.env.cr.fetchall():
                texts.append(r[0])
        return texts


class Stockpicking(models.Model):
    _inherit = 'stock.picking'

    def di_get_texts(self):
        texts = []
        for order in self:
            if order.partner_id.category_id.ids:
                query = """ select n.text 
                                from di_default_note n                          
                                where n.item in ('company','partner','partnertag')
                                and n.dn_print is true 
                                and ((n.item = 'company' and n.company_id =   %(company_id)s ) or (n.item = 'partner' and n.partner_id = %(partner_id)s ) or (n.item = 'partnertag' and n.partnertag_id in %(partnertag_ids)s ) )                                                         
                                order by n.item                                                                                                         
                            """
                query_args = {'company_id': order.company_id.id, 'partner_id': order.partner_id.id,
                              'partnertag_ids': tuple(order.partner_id.category_id.ids)}
            else:
                query = """ select n.text 
                                from di_default_note n                          
                                where n.item in ('company','partner','partnertag')
                                and n.dn_print is true 
                                and ((n.item = 'company' and n.company_id =   %(company_id)s ) or (n.item = 'partner' and n.partner_id = %(partner_id)s ) )                                                         
                                order by n.item                                                                                                         
                            """
                query_args = {'company_id': order.company_id.id,
                              'partner_id': order.partner_id.id}

            self.env.cr.execute(query, query_args)
            for r in self.env.cr.fetchall():
                texts.append(r[0])
        return texts


class StockMove(models.Model):
    _inherit = 'stock.move'

    def di_get_texts(self):
        texts = []
        for line in self:
            if line.product_id.categ_id.ids:
                query = """ select n.text 
                                from di_default_note n                          
                                where n.item in ('product','productcat') 
                                and n.dn_print is true
                                and ((n.item = 'product' and n.product_id =   %(product_id)s )  or (n.item = 'productcat' and n.productcat_id in %(productcat_ids)s ) )                                                         
                                order by n.item                                                                                                         
                            """
                query_args = {'product_id': line.product_id.id,
                              'productcat_ids': tuple(line.product_id.categ_id.ids)}
            else:
                query = """ select n.text 
                                from di_default_note n                          
                                where n.item in ('product','productcat') 
                                and n.dn_print is true
                                and ((n.item = 'product' and n.product_id =   %(product_id)s ) )                                                         
                                order by n.item                                                                                                          
                            """
                query_args = {'product_id': line.product_id.id}

            self.env.cr.execute(query, query_args)
            for r in self.env.cr.fetchall():
                texts.append(r[0])
        return texts


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    def di_get_texts(self):
        texts = []
        for line in self:
            if line.product_id.categ_id.ids:
                query = """ select n.text 
                                from di_default_note n                          
                                where n.item in ('product','productcat') 
                                and n.dn_print is true
                                and ((n.item = 'product' and n.product_id =   %(product_id)s )  or (n.item = 'productcat' and n.productcat_id in %(productcat_ids)s ) )                                                         
                                order by n.item                                                                                                         
                            """
                query_args = {'product_id': line.product_id.id,
                              'productcat_ids': tuple(line.product_id.categ_id.ids)}
            else:
                query = """ select n.text 
                                from di_default_note n                          
                                where n.item in ('product','productcat') 
                                and n.dn_print is true
                                and ((n.item = 'product' and n.product_id =   %(product_id)s ) )                                                         
                                order by n.item                                                                                                          
                            """
                query_args = {'product_id': line.product_id.id}

            self.env.cr.execute(query, query_args)
            for r in self.env.cr.fetchall():
                texts.append(r[0])
        return texts


class AccountMove(models.Model):
    _inherit = 'account.move'

    def di_get_texts(self):
        texts = []
        for order in self:
            if order.partner_id.category_id.ids:
                query = """ select n.text 
                                from di_default_note n                          
                                where n.item in ('company','partner','partnertag') 
                                and n.inv_print is true
                                and ((n.item = 'company' and n.company_id =   %(company_id)s ) or (n.item = 'partner' and n.partner_id = %(partner_id)s ) or (n.item = 'partnertag' and n.partnertag_id in %(partnertag_ids)s ) )                                                         
                                order by n.item                                                                                                         
                            """
                query_args = {'company_id': order.company_id.id, 'partner_id': order.partner_id.id,
                              'partnertag_ids': tuple(order.partner_id.category_id.ids)}
            else:
                query = """ select n.text 
                                from di_default_note n                          
                                where n.item in ('company','partner','partnertag') 
                                and n.inv_print is true
                                and ((n.item = 'company' and n.company_id =   %(company_id)s ) or (n.item = 'partner' and n.partner_id = %(partner_id)s ) )                                                         
                                order by n.item                                                                                                         
                            """
                query_args = {'company_id': order.company_id.id,
                              'partner_id': order.partner_id.id}

            self.env.cr.execute(query, query_args)
            for r in self.env.cr.fetchall():
                texts.append(r[0])
        return texts


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def di_get_texts(self):
        texts = []
        for line in self:
            if line.product_id:
                if line.product_id.categ_id.ids:
                    query = """ select n.text 
                                    from di_default_note n                          
                                    where n.item in ('product','productcat') 
                                    and n.inv_print is true
                                    and ((n.item = 'product' and n.product_id =   %(product_id)s )  or (n.item = 'productcat' and n.productcat_id in %(productcat_ids)s ) )                                                         
                                    order by n.item                                                                                                         
                                """
                    query_args = {'product_id': line.product_id.id, 'productcat_ids': tuple(
                        line.product_id.categ_id.ids)}
                else:
                    query = """ select n.text 
                                    from di_default_note n                          
                                    where n.item in ('product','productcat') 
                                    and n.inv_print is true
                                    and ((n.item = 'product' and n.product_id =   %(product_id)s ) )                                                         
                                    order by n.item                                                                                                          
                                """
                    query_args = {'product_id': line.product_id.id}

                self.env.cr.execute(query, query_args)
                for r in self.env.cr.fetchall():
                    texts.append(r[0])
        return texts
