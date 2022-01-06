# -*- coding: utf-8 -*-

from odoo.exceptions import ValidationError
from odoo import models, fields, api, _


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.depends('name')
    def _di_compute_prod_seq(self):
        for prod in self:
            prod.di_param_prod_seq = self.env['ir.config_parameter'].sudo(
            ).get_param('product_codification.di_prod_seq')

    di_param_prod_seq = fields.Boolean(
        string='Automatic codification', compute='_di_compute_prod_seq')

    def copy(self, default=None):
        default = dict(default or {})

        copied_count = self.search_count(
            [('default_code', '=like', u"{}%_Copy".format(self.default_code))])
        if not copied_count:
            new_name = u"{}_Copy".format(self.default_code)
        else:
            new_name = u"{}_Copy({})".format(self.default_code, copied_count)

        default['default_code'] = new_name
        return super(ProductTemplate, self).copy(default)


class ProductProduct(models.Model):
    _inherit = "product.product"

    default_code = fields.Char('Internal Reference', index=True)

    # unicité du code article

    @api.constrains('default_code')
    def _check_default_code(self):
        for prod in self:
            if prod.default_code:
                default_code = prod.search([
                    ('id', '!=', prod.id),
                    ('default_code', '=', prod.default_code)], limit=1)
                if default_code:
                    raise ValidationError(_("Default code is already used"))

    @api.model
    def create(self, values):
        pp = super(ProductProduct, self).create(values)
        if (pp.default_code == False) and (pp.di_param_prod_seq):
            if 'company_id' in values:
                pp.default_code = self.env['ir.sequence'].with_context(
                    force_company=values['company_id']).next_by_code('di.product.product.product.seq') or _('New')
            else:
                pp.default_code = self.env['ir.sequence'].next_by_code(
                    'di.product.product.product.seq') or _('New')
        return pp
