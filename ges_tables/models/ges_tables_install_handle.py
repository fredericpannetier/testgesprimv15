# -*- coding: utf-8 -*-
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo import api, fields, models, _
from odoo.tools import float_is_zero
import logging
_logger = logging.getLogger(__name__)


class GesTablesInstallHandle(models.Model):
    # Cette méthode est choisie plutôt que de tout faire en XML car cela permet de ne pas connaitre à l'avance tous les XML id
    _name = "ges.tables.install.handle"
    _description = "Handle the installation of Gesprim tables"
    _order = "name"

    name = fields.Char('Name')

    @api.model
    def create(self, vals):
        _logger.info(_("Installing Gesprim tables"))

        category_id = self.env['uom.category'].search([('name', '=', 'Unit')])
        units = self.env['uom.uom'].search(
            [('category_id', '=', category_id.id)])
        units.update({'ges_unittype': 'Piece'})

        category_id = self.env['uom.category'].search(
            [('name', '=', 'Weight')])
        units = self.env['uom.uom'].search(
            [('category_id', '=', category_id.id)])
        units.update({'ges_unittype': 'Net weight'})

        return super(GesTablesInstallHandle, self).create(vals)

    def unlink(self):
        _logger.info(_("Uninstalling Gesprim tables"))
        return super(GesTablesInstallHandle, self).unlink()
