# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = "res.partner"

    di_default_address = fields.Boolean(
        string="Default address", default=False, help="""Default adress in sale order""")
    di_company_country_code = fields.Char(
        string="Company country code", compute='_company_country_code')

    def address_get(self, adr_pref=None):
        # Copie du standard pour pouvoir mettre une adresse de fact/liv par défaut
        """ Find contacts/addresses of the right type(s) by doing a depth-first-search
        through descendants within company boundaries (stop at entities flagged ``is_company``)
        then continuing the search at the ancestors that are within the same company boundaries.
        Defaults to partners of type ``'default'`` when the exact type is not found, or to the
        provided partner itself if no type ``'default'`` is found either. """
        adr_pref = set(adr_pref or [])
        if 'contact' not in adr_pref:
            adr_pref.add('contact')
        result = {}
        visited = set()
        for partner in self:
            current_partner = partner
            while current_partner:
                to_scan = [current_partner]
                # Scan descendants, DFS
                while to_scan:
                    record = to_scan.pop(0)
                    visited.add(record)
                    if record.type in adr_pref and not result.get(record.type):
                        result[record.type] = record.id
                    if len(result) == len(adr_pref):
                        return result
                    to_scan = [c for c in record.child_ids
                               if c not in visited
                               if not c.is_company] + to_scan
                    # difmiadi - on trie la liste afin de mettre les adresses pas défaut en début de liste
                    to_scan.sort(
                        key=lambda l: l.di_default_address, reverse=True)

                # Continue scanning at ancestor if current_partner is not a commercial entity
                if current_partner.is_company or not current_partner.parent_id:
                    break
                current_partner = current_partner.parent_id

        # default to type 'contact' or the partner itself
        default = result.get('contact', self.id or False)
        for adr_type in adr_pref:
            result[adr_type] = result.get(adr_type) or default
        return result

    def _get_name(self):
        """ Utility method to allow name_get to be overrided without re-browse the partner """
        name = super(ResPartner, self)._get_name()
        partner = self
        if self.env.user.company_id.country_id.code == 'FR' and self._context.get('show_city'):
            if partner.city:
                name = "%s ‒ %s" % (name, partner.city)
        return name

    def _company_country_code(self):
        for partner in self:
            partner.di_company_country_code = self.env.user.company_id.country_id.code
