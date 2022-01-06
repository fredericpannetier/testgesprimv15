from odoo import models, fields, api, _
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError, ValidationError
from math import ceil
from setuptools.dist import sequence


class PriceRule(models.Model):
    _inherit = "delivery.price.rule"

    variable = fields.Selection([('weight', 'Weight'), ('volume', 'Volume'), ('wv', 'Weight * Volume'),
                                ('price', 'Price'), ('quantity', 'Quantity'), ('pallet', 'Pallet')], required=True, default='weight')
    variable_factor = fields.Selection([('weight', 'Weight'), ('volume', 'Volume'), ('wv', 'Weight * Volume'), ('price',
                                       'Price'), ('quantity', 'Quantity'), ('pallet', 'Pallet')], 'Variable Factor', required=True, default='weight')
    ges_paltyp_id = fields.Many2one(
        'di.pallet.type', string='Pallet type', help="Type of the pallet for the rule")

    @api.depends('variable', 'operator', 'max_value', 'list_base_price', 'list_price', 'variable_factor')
    def _compute_name(self):
        for rule in self:
            name = _('if %s %s  %s %.02f then') % (_(dict(self.fields_get(allfields=['variable'])['variable']['selection'])[
                rule.variable]), rule.ges_paltyp_id.name and '('+rule.ges_paltyp_id.name+')' or '', rule.operator, rule.max_value)
            if rule.list_base_price and not rule.list_price:
                name = _('%s fixed price %.02f') % (name, rule.list_base_price)
            elif rule.list_price and not rule.list_base_price:
                name = _('%s %.02f times %s %s') % (name, rule.list_price, _(dict(self.fields_get(allfields=['variable_factor'])[
                    'variable_factor']['selection'])[rule.variable_factor]), rule.ges_paltyp_id.name and rule.ges_paltyp_id.name or '')
            else:
                name = _('%s fixed price %.02f plus %.02f times %s %s') % (name, rule.list_base_price, rule.list_price, _(dict(self.fields_get(allfields=[
                    'variable_factor'])['variable_factor']['selection'])[rule.variable_factor]), rule.ges_paltyp_id.name and '('+rule.ges_paltyp_id.name+')' or '')
            rule.name = name


class ProviderGrid(models.Model):
    _inherit = 'delivery.carrier'

    def _ges_default_pallet_rounding(self):
        pallet_rounding = self.env['ir.config_parameter'].sudo(
        ).get_param('ges_base.ges_pallet_rounding')
        if not pallet_rounding:
            return 'fullpallet'
        return pallet_rounding

    ges_gasoiltax = fields.Float(
        string="Gasoil tax", help='This percentage will be added to the shipping price.')
    ges_adminfees = fields.Float(
        string='Administrative fees', help="Amount added to the shipping price.")

    ges_pallet_rounding = fields.Selection([('norounding', 'No rounding'), ('halfpallet', 'Half pallet'), ('fullpallet', 'Full pallet')], string="Pallet rounding", help="""Method to round pallet number""",
                                           default=_ges_default_pallet_rounding)

    def rate_shipment(self, order):
        self.ensure_one()
        if hasattr(self, '%s_rate_shipment' % self.delivery_type):
            res = super(ProviderGrid, self).rate_shipment(order)
            if not res['success'] or not self.free_over or order._compute_amount_total_without_delivery() < self.amount:
                res['price'] = float(res['price']) * \
                    (1.0 + (self.ges_gasoiltax / 100.0))
                res['price'] = float(res['price']) + self.ges_adminfees
            res['carrier_price'] = res['price']
            return res

    def _get_price_available(self, order):
        # copie standard
        # prise en compte de la quantité livrée si on a au moins une quantité livrée sur la pièce
        self.ensure_one()
        self = self.sudo()
        order = order.sudo()
        #total = weight = volume = quantity = 0
        total = total_delivered = amount_delivered = weight = quantity_delivered = volume = quantity = 0  # gesprim
        total_delivery = 0.0
        for line in order.order_line:
            if line.state == 'cancel':
                continue
            if line.is_delivery:
                total_delivery += line.price_total
            if not line.product_id or line.is_delivery:
                continue
            qty = line.product_uom._compute_quantity(
                line.product_uom_qty, line.product_id.uom_id)
            qty_delivered = line.product_uom._compute_quantity(
                line.qty_delivered, line.product_id.uom_id)  # gesprim
            # weight += (line.product_id.weight or 0.0) * qty
            # weight += (line.ges_nweight or 0.0)
            weight += (line.ges_gweight or 0.0)
            volume += (line.product_id.volume or 0.0) * qty
            quantity += qty
            quantity_delivered += qty_delivered  # gesprim

            if line.product_uom_qty != 0.0:  # gesprim
                # gesprim
                amount_delivered += (line.price_total /
                                     line.product_uom_qty) * line.qty_delivered

        total = (order.amount_total or 0.0) - total_delivery
        total_delivered = (amount_delivered or 0.0) - total_delivery  # gesprim

        total = order.currency_id.with_context(date=order.date_order).compute(
            total, order.company_id.currency_id)
        total_delivered = order.currency_id.with_context(date=order.date_order).compute(
            total_delivered, order.company_id.currency_id)  # gesprim
        # return self._get_price_from_picking(total, weight, volume, quantity)

        # gesprim
        if quantity_delivered != 0.0:
            return self._get_price_from_picking(total_delivered, weight, volume, quantity_delivered, order.ges_paltyp)
        else:
            return self._get_price_from_picking(total, weight, volume, quantity, order.ges_paltyp)

    # def _get_price_from_picking(self, total, weight, volume, quantity):
    def _get_price_from_picking(self, total, weight, volume, quantity, pallets):
        # copie standard
        # changement de la signature de la fonction et ajout de la prise en compte du code dest
        price = 0.0
        sequence = False  # gesprim
        criteria_found = False
        #price_dict = {'price': total, 'volume': volume, 'weight': weight, 'wv': volume * weight, 'quantity': quantity}
        if self.free_over and total >= self.amount:
            return 0

        price_dict = {'price': total, 'volume': volume, 'weight': weight, 'wv': volume * weight, 'quantity': quantity}
        lstpricepal = []  # gesprim
        lstpal = []    # gesprim
        for line in self.price_rule_ids:
            if line.variable != 'pallet':  # OK # gesprim
                test = safe_eval(line.variable + line.operator +
                                 str(line.max_value), price_dict)
                if test:
                    price = line.list_base_price + line.list_price * \
                        price_dict[line.variable_factor]
                    criteria_found = True
                    sequence = line.sequence  # gesprim
                    break
            else:  # gesprim
                if line.ges_paltyp_id and line.ges_paltyp_id.id not in lstpal:  # OK
                    pallet = False
                    if pallets:
                        pallet = pallets.filtered(
                            lambda p: p.paltyp_id.id == line.ges_paltyp_id.id)
#                     for pallet in pallets:
                    if pallet:
                        if self.ges_pallet_rounding == 'halfpallet':
                            nb = pallet.pallet_num*2
                            nba = ceil(nb)
                            nbpal = nba/2
                        elif self.ges_pallet_rounding == 'fullpallet':
                            nbpal = ceil(pallet.pallet_num)
                        else:
                            nbpal = pallet.pallet_num

                        ges_price_dict_pal = {'pallet': nbpal}
                        if line.ges_paltyp_id == pallet.paltyp_id:
                            test = safe_eval(
                                line.variable + line.operator + str(line.max_value), ges_price_dict_pal)
                            if test:
                                if line.list_price != 0 :
                                    price_pal = line.list_base_price + line.list_price * ges_price_dict_pal[line.variable_factor]
                                else:
                                    price_pal = line.list_base_price

                                lstpricepal.append(
                                    {'pallet_id': line.ges_paltyp_id.id, 'price_pal': price_pal, 'sequence': line.sequence})
                                lstpal.append(line.ges_paltyp_id.id)
    #                             criteria_found = True

                else:  # OK
                    if pallets:
                        sumpal = sum([pallet.pallet_num for pallet in pallets])
                        if self.ges_pallet_rounding == 'halfpallet':
                            nb = sumpal*2
                            nba = ceil(nb)
                            nbpal = nba/2
                        elif self.ges_pallet_rounding == 'fullpallet':
                            nbpal = ceil(sumpal)
                        else:
                            nbpal = sumpal

                        ges_price_dict_pal = {'pallet': nbpal}
                        test = safe_eval(
                            line.variable + line.operator + str(line.max_value), ges_price_dict_pal)
                        if test:
                            price += line.list_base_price + line.list_price * \
                                ges_price_dict_pal[line.variable_factor]
                            criteria_found = True
                            sequence = line.sequence
                            break

        # gesprim
        price_pal = 0.0
        if lstpricepal:
            for dictpal in lstpricepal:
                if not criteria_found or (criteria_found and dictpal['sequence'] < sequence):
                    price_pal += dictpal['price_pal']
            criteria_found = True
            price = price_pal

        # fin gesprim

        if not criteria_found:
            raise UserError(
                _("No price rule matching this order; delivery cost cannot be computed."))

        return price
