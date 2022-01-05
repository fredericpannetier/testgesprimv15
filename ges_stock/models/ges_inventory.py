# -*- coding: utf-8 -*-
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo import api, fields, models, _
from odoo.tools import float_is_zero


class GesInventory(models.Model):
    _name = "ges.inventory"
    _description = "Inventory"
    _order = "date desc, id desc"

    company_id = fields.Many2one(
        'res.company', 'Company',
        readonly=True, index=True, required=True,
        states={'draft': [('readonly', False)]},
        default=lambda self: self.env.company)
    name = fields.Char(
        'Inventory Reference', default="Inventory",
        readonly=True, required=True,
        states={'draft': [('readonly', False)]})
    date = fields.Datetime(
        'Inventory Date',
        readonly=True, required=True,
        default=fields.Datetime.now,
        help="If the inventory adjustment is not validated, date at which the theoritical quantities have been checked.\n"
             "If the inventory adjustment is validated, date at which the inventory adjustment has been validated.")
    state = fields.Selection(string='Status', selection=[
        ('draft', 'Draft'),
        ('cancel', 'Cancelled'),
        ('confirm', 'In Progress'),
        ('done', 'Validated')],
        copy=False, index=True, readonly=True,
        default='draft')
    stock_move_ids = fields.One2many(
        'stock.move', 'ges_inventory_id', string='Created Moves',
        states={'done': [('readonly', True)]})
    start_empty = fields.Boolean('Empty Inventory',
                                 help="Allows to start with an empty inventory.")

    move_ids = fields.One2many("ges.inventory.move", "inventory_id", string="Moves", states={
                               'done': [('readonly', True)]})

    product_ids = fields.Many2many(
        'product.product', string='Products', check_company=True,
        domain="[('type', '=', 'product'), '|', ('company_id', '=', False), ('company_id', '=', company_id)]", readonly=True,
        states={'draft': [('readonly', False)]},
        help="Specify Products to focus your inventory on particular Products.")

    location_ids = fields.Many2many(
        'stock.location', string='Locations',
        readonly=True, check_company=True,
        states={'draft': [('readonly', False)]},
        domain="[('company_id', '=', company_id), ('usage', 'in', ['internal', 'transit'])]")

    category_ids = fields.Many2many("product.category", string="Categories")
    prefill_counted_quantity = fields.Selection(string='Counted Quantities',
                                                help="Allows to start with prefill counted quantity for each lines or "
                                                "with all counted quantity set to zero.", default='counted',
                                                selection=[('counted', 'Default to stock on hand'), ('zero', 'Default to zero')])
    exhausted = fields.Boolean(
        'Include Exhausted Products', readonly=True,
        states={'draft': [('readonly', False)]},
        help="Include also products with quantity of 0")

    def action_validate(self):
        if not self.exists():
            return
        self.ensure_one()
        if not self.user_has_groups('stock.group_stock_manager'):
            raise UserError(
                _("Only a stock manager can validate an inventory adjustment."))
        if self.state != 'confirm':
            raise UserError(_(
                "You can't validate the inventory '%s', maybe this inventory "
                "has been already validated or isn't ready.", self.name))

        self._action_done()
        self.move_ids._check_company()
        self._check_company()
        return True

    def post_inventory(self):
        # The inventory is posted as a single step which means quants cannot be moved from an internal location to another using an inventory
        # as they will be moved to inventory loss, and other quants will be created to the encoded quant location. This is a normal behavior
        # as quants cannot be reuse from inventory location (users can still manually move the products before/after the inventory if they want).
        self.mapped('stock_move_ids').filtered(
            lambda move: move.state != 'done')._action_done()
        return True

    def _action_done(self):
        negative = next((line for line in self.mapped('move_ids')
                        if line.qty < 0 and line.qty != line.qty_theo), False)
        if negative:
            raise UserError(_(
                'You cannot set a negative product quantity in an inventory line:\n\t%s - qty: %s',
                negative.product_id.display_name,
                negative.product_qty
            ))
        self.action_check()
        self.write({'state': 'done', 'date': fields.Datetime.now()})
        self.post_inventory()
        return True

    def action_check(self):
        """ Checks the inventory and computes the stock move to do """
        # tde todo: clean after _generate_moves
        for inventory in self.filtered(lambda x: x.state not in ('done', 'cancel')):
            # first remove the existing stock moves linked to this inventory
            inventory.with_context(prefetch_fields=False).mapped(
                'stock_move_ids').unlink()
            for m in inventory.move_ids:
                m.move_line_ids._generate_moves()

    def action_cancel_draft(self):
        self.mapped('stock_move_ids')._action_cancel()
        for m in self.move_ids:
            m.move_line_ids.unlink()
        self.move_ids.unlink()
        self.write({'state': 'draft'})

    def action_start(self):
        self.ensure_one()
        self.product_ids += self.env['product.product'].search(
            ['&', '&', ('categ_id', 'in', self.category_ids.ids), ('type', '=', 'product'), ('active', '=', True)])
        self._action_start()
        self._check_company()

    def _action_start(self):
        """ Confirms the Inventory Adjustment and generates its inventory lines
        if its state is draft and don't have already inventory lines (can happen
        with demo data or tests).
        """
        for inventory in self:
            if inventory.state != 'draft':
                continue
            vals = {
                'state': 'confirm',
                'date': fields.Datetime.now()
            }
            if not inventory.move_ids and not inventory.start_empty:
                self.env['ges.inventory.move'].create(
                    inventory._get_inventory_moves_values())
            inventory.write(vals)

    def _get_quantities_move_line(self, product_id):
        """Return quantities group by product_id, location_id, lot_id

        :return: a dict with keys as tuple of group by and quantity as value
        :rtype: dict
        """
        self.ensure_one()
        if self.location_ids:
            domain_loc = [('id', 'child_of', self.location_ids.ids)]
        else:
            domain_loc = [('company_id', '=', self.company_id.id),
                          ('usage', 'in', ['internal', 'transit'])]
        locations_ids = [l['id'] for l in self.env['stock.location'].search_read(domain_loc, ['id'])]

        domain = [('company_id', '=', self.company_id.id),
                  ('quantity', '!=', '0'),
                  ('location_id', 'in', locations_ids)]
        if self.prefill_counted_quantity == 'zero':
            domain.append(('product_id.active', '=', True))

        if product_id:
            domain = expression.AND(
                [domain, [('product_id', '=', product_id)]])

        fields = ['product_id', 'location_id', 'lot_id', 'quantity:sum']
        group_by = ['product_id', 'location_id', 'lot_id']

        quants = self.env['stock.quant'].read_group(
            domain, fields, group_by, lazy=False)
        return {(
            quant['location_id'] and quant['location_id'][0] or False,
            quant['lot_id'] and quant['lot_id'][0] or False):
            quant['quantity'] for quant in quants
        }

    def _get_exhausted_inventory_move_lines_vals(self, non_exhausted_set, product_id):
        """Return the values of the inventory lines to create if the user
        wants to include exhausted products. Exhausted products are products
        without quantities or quantity equal to 0.

        :param non_exhausted_set: set of tuple (product_id, location_id) of non exhausted product-location
        :return: a list containing the `stock.inventory.line` values to create
        :rtype: list
        """

        vals = []
        self.ensure_one()

        domain_loc = [('company_id', '=', self.company_id.id),
                      ('usage', '=', 'internal')]
        location_ids = [
            l['id'] for l in self.env['stock.location'].search_read(domain_loc, ['id'])]

        location_id = location_ids[0]

        for lot in self.env['stock.production.lot'].search([('product_id', '=', product_id)]):
            if ((lot.id) not in non_exhausted_set):
                vals.append({
                    'qty': 0,
                    'lot_id': lot.id,
                    'qty_theo': 0,
                    'location_id': location_id,
                    'incoming_date': lot.create_date,
                    'product_id': product_id,
                })
#         lines = self.env['ges.inventory.move.line'].create(vals)
        return vals

    def _get_inventory_move_lines_values(self, product_id, move_id=False):
        """Return the values of the inventory move lines to create for this inventory.

        :return: a list containing the `ges.inventory.move.line` values to create
        :rtype: list
        """
        self.ensure_one()
        quants_groups = self._get_quantities_move_line(product_id)
        vals = []
        for (location_id, lot_id), quantity in quants_groups.items():
            lot = self.env['stock.production.lot'].browse(lot_id)
            line_values = {
                'qty': 0 if self.prefill_counted_quantity == "zero" else quantity,
                'qty_theo': quantity,
                'location_id': location_id,
                'lot_id': lot_id,
                'product_id': product_id,
                'incoming_date': lot.create_date
            }
            if move_id:
                line_values['move_id'] = move_id
            vals.append(line_values)
        if self.exhausted:
            vals += self._get_exhausted_inventory_move_lines_vals(
                {(l['lot_id']) for l in vals}, product_id)

        lines = self.env['ges.inventory.move.line'].create(vals)
        return lines.ids

    def _get_inventory_moves_values(self):
        """Return the values of the inventory moves to create for this inventory.

        :return: a list containing the `ges.inventory.move` values to create
        :rtype: list
        """
        self.ensure_one()
        quants_groups = self._get_quantities_move()
        vals = []
        for (product_id), quantity in quants_groups.items():
            line_values = {
                'inventory_id': self.id,
                'product_id': product_id,
                'qty': 0 if self.prefill_counted_quantity == "zero" else quantity,
                'qty_theo': quantity,
                'move_line_ids': [(6, 0, self._get_inventory_move_lines_values(product_id))]
            }
            vals.append(line_values)
        if self.exhausted:
            vals += self._get_exhausted_inventory_moves_vals(
                {(l['product_id']) for l in vals})
        return vals

    def _get_exhausted_inventory_moves_vals(self, non_exhausted_set):
        """Return the values of the inventory lines to create if the user
        wants to include exhausted products. Exhausted products are products
        without quantities or quantity equal to 0.

        :param non_exhausted_set: set of tuple (product_id, location_id) of non exhausted product-location
        :return: a list containing the `stock.inventory.line` values to create
        :rtype: list
        """
        self.ensure_one()
        if self.product_ids:
            product_ids = self.product_ids.ids
        else:
            product_ids = self.env['product.product'].search_read([
                '|', ('company_id', '=',
                      self.company_id.id), ('company_id', '=', False),
                ('type', '=', 'product'),
                ('active', '=', True)], ['id'])
            product_ids = [p['id'] for p in product_ids]

        vals = []
        for product_id in product_ids:

            if ((product_id) not in non_exhausted_set):
                vals.append({
                    'inventory_id': self.id,
                    'product_id': product_id,
                    'qty': 0,
                    'qty_theo': 0,
                    'move_line_ids': [(6, 0, self._get_inventory_move_lines_values(product_id))]
                })
        return vals

    def _get_quantities_move(self, product_id=False):
        """Return quantities group by product_id

        :return: a dict with keys as tuple of group by and quantity as value
        :rtype: dict
        """
        self.ensure_one()
        if self.location_ids:
            domain_loc = [('id', 'child_of', self.location_ids.ids)]
        else:
            domain_loc = [('company_id', '=', self.company_id.id),
                          ('usage', 'in', ['internal', 'transit'])]
        locations_ids = [
            l['id'] for l in self.env['stock.location'].search_read(domain_loc, ['id'])]

        domain = [('company_id', '=', self.company_id.id),
                  ('quantity', '!=', '0'),
                  ('location_id', 'in', locations_ids)]
        if self.prefill_counted_quantity == 'zero':
            domain.append(('product_id.active', '=', True))
        if product_id:
            domain = expression.AND(
                [domain, [('product_id', '=', product_id)]])
        else:
            if self.product_ids:
                domain = expression.AND(
                    [domain, [('product_id', 'in', self.product_ids.ids)]])

        fields = ['product_id', 'quantity:sum']
        group_by = ['product_id']

        quants = self.env['stock.quant'].read_group(
            domain, fields, group_by, lazy=False)
        return {(
            quant['product_id'] and quant['product_id'][0] or False):
            quant['quantity'] for quant in quants
        }


class GesInventoryMove(models.Model):
    _name = "ges.inventory.move"
    _description = "Inventory move"
    _order = "product_id"

    movelineqtymodified = False

    company_id = fields.Many2one('res.company', string='Company',
                                 readonly=True,  default=lambda self: self.env.user.company_id)
    name = fields.Char(related="product_id.name", string="Name")
    state = fields.Selection(string='Status', related='inventory_id.state')
    inventory_id = fields.Many2one('ges.inventory', string='Inventory')
    move_line_ids = fields.One2many(
        "ges.inventory.move.line", "move_id", string="Move lines")
    product_id = fields.Many2one('product.product', string='Product')
    qty_theo = fields.Float("Theoretical quantity", digits='Product Unit of Measure',
                            readonly=True, compute="_compute_qty_theo")
    pack_theo = fields.Float("Theoretical packages number", digits=(
        12, 1), readonly=True, compute="_compute_theo_qties")
    pieces_theo = fields.Float("Theoretical pieces number", digits=(
        12, 1), readonly=True, compute="_compute_theo_qties")
    nweight_theo = fields.Float(
        "Theoretical net weight", digits='Stock Weight', readonly=True, compute="_compute_theo_qties")
    qty = fields.Float("Quantity", digits='Product Unit of Measure',
                       store=True, compute="_compute_qty", inverse="_inverse_qty")
    pack = fields.Float("Packages number", digits=(
        12, 1), readonly=True, compute="_compute_qties")
    pieces = fields.Float("Pieces number", digits=(
        12, 1), readonly=True, compute="_compute_qties")
    nweight = fields.Float("Net weight", digits='Stock Weight',
                           readonly=True, compute="_compute_qties")

    @api.depends("move_line_ids.qty_theo")
    def _compute_qty_theo(self):
        for m in self:
            m.qty_theo = 0
            for ml in m.move_line_ids:
                m.qty_theo += (ml.qty_theo if ml.qty_theo else 0)

    @api.depends("move_line_ids.qty")
    def _compute_qty(self):
        GesInventoryMove.movelineqtymodified = True
        for m in self:
            m.qty = 0
            for ml in m.move_line_ids:
                m.qty += (ml.qty if ml.qty else 0)

    def _inverse_qty(self):
        # when the field is computed, the program execute the inverse function when we save
        if not GesInventoryMove.movelineqtymodified:
            for move in self:
                qty_to_add = (move.qty if move.qty else 0) - \
                    (move.qty_theo if move.qty_theo else 0)
                if qty_to_add and qty_to_add > 0:
                    premier = True
                    move_lines = move.move_line_ids.sorted(
                        lambda l: (l.incoming_date, l.id), reverse=True)
                    for ml in move_lines:
                        if premier:
                            ml.qty = (
                                ml.qty_theo if ml.qty_theo else 0) + qty_to_add
                        else:
                            ml.qty = ml.qty_theo
                        premier = False
                elif qty_to_add and qty_to_add < 0:
                    move_lines = move.move_line_ids.sorted(
                        lambda l: (l.incoming_date, l.id))
                    premier = True
                    for ml in move_lines:
                        if (ml.qty_theo if ml.qty_theo else 0) >= abs(qty_to_add):
                            ml.qty = (
                                ml.qty_theo if ml.qty_theo else 0) + qty_to_add
                            qty_to_add = 0
                        else:
                            ml.qty = 0
                            qty_to_add += (ml.qty_theo if ml.qty_theo else 0)
                        if qty_to_add >= 0:
                            break

                else:
                    move_lines = move.move_line_ids
                    for ml in move_lines:
                        ml.qty = ml.qty_theo
        GesInventoryMove.movelineqtymodified = False

    def action_show_details(self):
        """ Returns an action that will open a form view (in a popup) allowing to work on all the
        move lines of a particular move. 
        """
        self.ensure_one()

        view = self.env.ref('ges_stock.ges_inventory_move_form')

        return {
            'name': _('Detailed Operations'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'ges.inventory.move',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': self.id,
            'context': dict(
                self.env.context,
                # able to create lots, whatever the value of ` use_create_lots`.
                show_lots_m2o=self.product_id.product_tmpl_id.tracking != 'none'
            ),
        }

    @api.depends('qty_theo', 'product_id')
    def _compute_theo_qties(self):
        for ml in self:
            ml.pack_theo = ml.product_id.product_tmpl_id.get_packs_qty(
                ml.qty_theo)
            ml.pieces_theo = ml.product_id.product_tmpl_id.get_pieces_qty(
                ml.qty_theo)
            ml.nweight_theo = ml.product_id.product_tmpl_id.get_nweight_qty(
                ml.qty_theo)

    @api.depends('qty', 'product_id')
    def _compute_qties(self):
        for ml in self:
            ml.pack = ml.product_id.product_tmpl_id.get_packs_qty(ml.qty)
            ml.pieces = ml.product_id.product_tmpl_id.get_pieces_qty(ml.qty)
            ml.nweight = ml.product_id.product_tmpl_id.get_nweight_qty(ml.qty)


class GesInventoryMoveLine(models.Model):
    _name = "ges.inventory.move.line"
    _description = "Inventory move line"
    _order = "incoming_date"

    @api.model
    def _domain_location_id(self):
        if self.env.context.get('active_model') == 'ges.inventory':
            inventory = self.env['ges.inventory'].browse(
                self.env.context.get('active_id'))
            if inventory.exists() and inventory.location_ids:
                return "[('company_id', '=', company_id), ('usage', 'in', ['internal', 'transit']), ('id', 'child_of', %s)]" % inventory.location_ids.ids
        return "[('company_id', '=', company_id), ('usage', 'in', ['internal', 'transit'])]"

    company_id = fields.Many2one('res.company', string='Company',
                                 readonly=True,  default=lambda self: self.env.user.company_id)
    name = fields.Char(related="product_id.name", string="Name")
    move_id = fields.Many2one('ges.inventory.move', string='Move')
    state = fields.Selection(string='Status', related='move_id.state')
    incoming_date = fields.Datetime("Incoming date", readonly=True)
    product_id = fields.Many2one('product.product', string='Product')
    lot_id = fields.Many2one('stock.production.lot', string='Lot')
    qty_theo = fields.Float("Theoretical quantity",
                            digits='Product Unit of Measure', readonly=True)
    pack_theo = fields.Float("Theoretical packages number", digits=(
        12, 1), readonly=True, compute="_compute_theo_qties")
    pieces_theo = fields.Float("Theoretical pieces number", digits=(
        12, 1), readonly=True, compute="_compute_theo_qties")
    nweight_theo = fields.Float(
        "Theoretical net weight", digits='Stock Weight', readonly=True, compute="_compute_theo_qties")
    # , compute="_compute_qty", inverse = "_inverse_qty", store=True)
    qty = fields.Float("Quantity", digits='Product Unit of Measure')
    pack = fields.Float("Packages number", digits=(
        12, 1), readonly=True, compute="_compute_qties")
    pieces = fields.Float("Pieces number", digits=(
        12, 1), readonly=True, compute="_compute_qties")
    nweight = fields.Float("Net weight", digits='Stock Weight',
                           readonly=True, compute="_compute_qties")
    location_id = fields.Many2one(
        'stock.location', 'Location', check_company=True,
        domain=lambda self: self._domain_location_id(),
        index=True, required=True)

    @api.onchange('lot_id')
    def _onchange_lot(self):
        for line in self:
            domain_loc = [('company_id', '=', line.company_id.id),
                          ('usage', '=', 'internal')]
            location_ids = [
                l['id'] for l in self.env['stock.location'].search_read(domain_loc, ['id'])]
            line.incoming_date = line.lot_id.create_date
            line.location_id = self.env['stock.location'].browse(
                location_ids[0])

    def _get_move_values(self, qty, location_id, location_dest_id, out, pack, pieces, weight):
        self.ensure_one()
        return {
            'name': _('INV:') + (self.move_id.inventory_id.name or ''),
            'product_id': self.product_id.id,
            'product_uom': self.product_id.uom_id.id,
            'product_uom_qty': qty,
            'ges_pack': pack,
            'ges_piece': pieces,
            'ges_nweight': weight,
            'date': self.move_id.inventory_id.date,
            'company_id': self.move_id.inventory_id.company_id.id,
            'ges_inventory_id': self.move_id.inventory_id.id,
            'state': 'confirmed',
            'location_id': location_id,
            'location_dest_id': location_dest_id,
            'move_line_ids': [(0, 0, {
                'product_id': self.product_id.id,
                'lot_id': self.lot_id.id,
                'product_uom_qty': 0,  # bypass reservation here
                'product_uom_id': self.product_id.uom_id.id,
                'qty_done': qty,
                'ges_pack': pack,
                'ges_piece': pieces,
                'ges_nweight': weight,
                'package_id': False,
                'result_package_id':  False,
                'location_id': location_id,
                'location_dest_id': location_dest_id,
            })]
        }

    def _get_virtual_location(self):
        return self.product_id.with_company(self.company_id).property_stock_inventory

    def _generate_moves(self):
        vals_list = []
        for line in self:
            virtual_location = line._get_virtual_location()
            rounding = line.product_id.uom_id.rounding
            difference_qty = (line.qty if line.qty else 0) - (line.qty_theo if line.qty_theo else 0)
            difference_pack = (line.pack if line.pack else 0) - (line.pack_theo if line.pack_theo else 0)
            difference_pieces = (line.pieces if line.pieces else 0) - (line.pieces_theo if line.pieces_theo else 0)
            difference_weight = (line.nweight if line.nweight else 0) - (line.nweight_theo if line.nweight_theo else 0)
            if float_is_zero(difference_qty, precision_rounding=rounding):
                continue
            if not line.product_id:
                line.product_id = line.lot_id.product_id
            if not line.incoming_date:
                line.incoming_date = line.lot_id.create_date
            if difference_qty > 0:  # found more than expected
                location_id = line.location_id
                if not location_id:
                    domain_loc = [
                        ('company_id', '=', line.company_id.id), ('usage', '=', 'internal')]
                    location_ids = [
                        l['id'] for l in self.env['stock.location'].search_read(domain_loc, ['id'])]
                    location_id = self.env['stock.location'].browse(
                        location_ids[0])
                vals = line._get_move_values(difference_qty, virtual_location.id, location_id.id, False, difference_pack, difference_pieces, difference_weight)
            else:
                location_id = line.location_id
                if not location_id:
                    location_id = self.product_id.with_company(
                        self.company_id).property_stock_inventory
                vals = line._get_move_values(abs(difference_qty), location_id.id, virtual_location.id, True, difference_pack, difference_pieces, difference_weight)
            vals_list.append(vals)
        return self.env['stock.move'].create(vals_list)

    @api.depends('qty_theo', 'product_id')
    def _compute_theo_qties(self):
        for ml in self:
            ml.pack_theo = ml.product_id.product_tmpl_id.get_packs_qty(
                ml.qty_theo)
            ml.pieces_theo = ml.product_id.product_tmpl_id.get_pieces_qty(
                ml.qty_theo)
            ml.nweight_theo = ml.product_id.product_tmpl_id.get_nweight_qty(
                ml.qty_theo)

    @api.depends('qty', 'product_id')
    def _compute_qties(self):
        for ml in self:
            ml.pack = ml.product_id.product_tmpl_id.get_packs_qty(ml.qty)
            ml.pieces = ml.product_id.product_tmpl_id.get_pieces_qty(ml.qty)
            ml.nweight = ml.product_id.product_tmpl_id.get_nweight_qty(ml.qty)
