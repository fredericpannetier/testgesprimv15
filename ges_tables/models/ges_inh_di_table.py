# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, RedirectWarning, except_orm

import logging

_logger = logging.getLogger(__name__)


class DiMultiTable(models.Model):
    _inherit = 'di.multi.table'

    def _get_record_type(self):
        vals = [("origin", _("Origin")), ("size", _("Size")),
                ("brand", _("Brand")), ("category", _("Category"))]
        return vals

