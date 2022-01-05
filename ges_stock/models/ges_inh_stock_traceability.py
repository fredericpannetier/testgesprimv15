import json

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import format_datetime

rec = 0


def autoIncrement():
    global rec
    pStart = 1
    pInterval = 1
    if rec == 0:
        rec = pStart
    else:
        rec += pInterval
    return rec


class MrpStockReport(models.TransientModel):
    _inherit = 'stock.traceability.report'

    def _make_dict_move(self, level, parent_id, move_line, unfoldable=False):
        data = super(MrpStockReport, self)._make_dict_move(
            level, parent_id, move_line, unfoldable)
        if move_line.move_id.picking_code == 'incoming':
            data[0]['ges_partner'] = move_line.move_id.picking_partner_id.name or False
        else:
            data[0]['ges_partner'] = move_line.move_id.partner_id.name or False
        return data

    @api.model
    def _final_vals_to_lines(self, final_vals, level):
        #         lines = super(MrpStockReport,self)._final_vals_to_lines(final_vals, level)
        # copie standard
        lines = []
        for data in final_vals:
            lines.append({
                'id': autoIncrement(),
                'model': data['model'],
                'model_id': data['model_id'],
                'parent_id': data['parent_id'],
                'usage': data.get('usage', False),
                'is_used': data.get('is_used', False),
                'lot_name': data.get('lot_name', False),
                'lot_id': data.get('lot_id', False),
                'reference': data.get('reference_id', False),
                'res_id': data.get('res_id', False),
                'res_model': data.get('res_model', False),
                'columns': [data.get('reference_id', False),
                            data.get('product_id', False),
                            format_datetime(self.env, data.get(
                                'date', False), tz=False, dt_format=False),
                            data.get('lot_name', False),
                            data.get('location_source', False),
                            data.get('location_destination', False),
                            data.get('ges_partner', False),
                            data.get('product_qty_uom', 0)],
                'level': level,
                'unfoldable': data['unfoldable'],
            })
        return lines
