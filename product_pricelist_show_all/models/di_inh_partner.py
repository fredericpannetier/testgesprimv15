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


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.depends("property_product_pricelist")
    def _di_compute_di_pricelist_id(self):
        for p in self:
            p.di_pricelist_id = p.property_product_pricelist.id

    di_pricelist_id = fields.Integer(string="Pricelist id", compute="_di_compute_di_pricelist_id", store=True)
