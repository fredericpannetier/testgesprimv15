
# -*- coding: utf-8 -*-
from odoo.exceptions import ValidationError
from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = "res.partner"

    ref = fields.Char(string='Internal Reference', index=True,
                      help="Partner code", store=True)  # modif attribut copy + ajout help

    di_param_cus_seq = fields.Boolean(
        string='Customer automatic codification', compute='_di_compute_partner_seq', store=False)
    di_param_sup_seq = fields.Boolean(
        string='Supplier automatic codification', compute='_di_compute_partner_seq', store=False)
    di_ref_required = fields.Boolean(
        string='Partner code required', compute='_di_compute_ref_required', store=False)

    @api.depends('di_param_cus_seq', 'di_param_sup_seq')
    def _di_compute_ref_required(self):
        for partner in self:
            #             if self._context.get('default_type') in ('invoice','delivery'):
            if self.type in ('invoice', 'delivery'):
                partner.di_ref_required = False
            else:
                if partner.customer_rank > 0:
                    if partner.di_param_cus_seq:
                        partner.di_ref_required = False
                    else:
                        partner.di_ref_required = True
                elif partner.supplier_rank > 0:
                    if partner.di_param_sup_seq:
                        partner.di_ref_required = False
                    else:
                        partner.di_ref_required = True
                else:
                    partner.di_ref_required = False
#                 partner.di_ref_required=True

    @api.depends('name')
    def _di_compute_partner_seq(self):
        for partner in self:
            partner.di_param_cus_seq = self.env['ir.config_parameter'].sudo(
            ).get_param('partner_codification.di_cus_seq')
            partner.di_param_sup_seq = self.env['ir.config_parameter'].sudo(
            ).get_param('partner_codification.di_sup_seq')

    # unicité du code tiers

    @api.constrains('ref')
    def _check_ref(self):
        for partner in self:
            if partner.ref:
                default_code = partner.search([
                    ('id', '!=', partner.id),
                    ('ref', '=', partner.ref)], limit=1)
                if default_code:
                    raise ValidationError(_("Code is already used"))

    @api.model
    def create(self, values):
        rp = super(ResPartner, self).create(values)
        if rp.customer_rank > 0 and rp.supplier_rank <= 0:
            # si client, séquence client
            if (rp.ref == False) and (rp.di_param_cus_seq):
                if 'company_id' in values:
                    rp.ref = self.env['ir.sequence'].with_context(
                        force_company=values['company_id']).next_by_code('di.res.partner.customer.seq') or _('New')
                else:
                    rp.ref = self.env['ir.sequence'].next_by_code(
                        'di.res.partner.customer.seq') or _('New')
        if rp.supplier_rank > 0 and rp.customer_rank <= 0:
            # si fournisseur, séquence fournisseur
            if (rp.ref == False) and (rp.di_param_sup_seq):
                if 'company_id' in values:
                    rp.ref = self.env['ir.sequence'].with_context(
                        force_company=values['company_id']).next_by_code('di.res.partner.supplier.seq') or _('New')
                else:
                    rp.ref = self.env['ir.sequence'].next_by_code(
                        'di.res.partner.supplier.seq') or _('New')
        return rp

    def copy(self, default=None):
        default = dict(default or {})
        copied_count = self.search_count(
            [('ref', '=like', u"{}%_Copy".format(self.ref))])
        if not copied_count:
            new_name = u"{}_Copy".format(self.ref)
        else:
            new_name = u"{}_Copy({})".format(self.ref, copied_count)

        default['ref'] = new_name

        return super(ResPartner, self).copy(default)
