from xml.sax.saxutils import escape
import time
from openerp.osv import fields, osv
from datetime import datetime
from lxml import etree
from openerp import tools
from openerp.tools.translate import _

class resto_order_line(osv.Model):
    """ 
    resto order line: one resto order can have many order lines
    """
    _name = 'resto.order.line'
    _description = 'resto order line'

    def onchange_price(self, cr, uid, ids, meal_id, context=None):
        if meal_id:
            price = self.pool.get('resto.meal').browse(cr, uid, meal_id, context=context).price
            return {'value': {'price': price}}
        return {'value': {'price': 0.0}}

    def order(self, cr, uid, ids, context=None):
        """ 
        The order_line is ordered to the supplier but isn't received yet
        """
        for order_line in self.browse(cr, uid, ids, context=context):
            order_line.write({'state': 'ordered'}, context=context)
        return self._update_order_lines(cr, uid, ids, context=context)

    def confirm(self, cr, uid, ids, context=None):
        """ 
        confirm one or more order line, update order status and create new cashmove 
        """
        cashmove_ref = self.pool.get('resto.cashmove')
        for order_line in self.browse(cr, uid, ids, context=context):
            if order_line.state != 'confirmed':
                values = {
                    'user_id': order_line.user_id.id,
                    'amount': -order_line.price,
                    'description': order_line.meal_id.name,
                    'order_id': order_line.id,
                    'state': 'order',
                    'date': order_line.date,
                }
                cashmove_ref.create(cr, uid, values, context=context)
                order_line.write({'state': 'confirmed'}, context=context)
        return self._update_order_lines(cr, uid, ids, context=context)

    def _update_order_lines(self, cr, uid, ids, context=None):
        """
        Update the state of resto.order based on its orderlines
        """
        orders_ref = self.pool.get('resto.order')
        orders = []
        for order_line in self.browse(cr, uid, ids, context=context):
            orders.append(order_line.order_id)
        for order in set(orders):
            isconfirmed = True
            for orderline in order.order_line_ids:
                if orderline.state == 'new':
                    isconfirmed = False
                if orderline.state == 'cancelled':
                    isconfirmed = False
                    orders_ref.write(cr, uid, [order.id], {'state': 'partially'}, context=context)
            if isconfirmed:
                orders_ref.write(cr, uid, [order.id], {'state': 'confirmed'}, context=context)
        return {}

    def cancel(self, cr, uid, ids, context=None):
        """
        cancel one or more order.line, update order status and unlink existing cashmoves
        """
        cashmove_ref = self.pool.get('resto.cashmove')
        for order_line in self.browse(cr, uid, ids, context=context):
            order_line.write({'state':'cancelled'}, context=context)
            cash_ids = [cash.id for cash in order_line.cashmove]
            cashmove_ref.unlink(cr, uid, cash_ids, context=context)
        return self._update_order_lines(cr, uid, ids, context=context)
    
    def _get_line_order_ids(self, cr, uid, ids, context=None):
        """
        return the list of resto.order.lines ids to which belong the  resto.order 'ids'
        """
        result = set()
        for resto_order in self.browse(cr, uid, ids, context=context):
            for lines in resto_order.order_line_ids:
                result.add(lines.id)
        return list(result)

    _columns = {
        'name': fields.related('meal_id', 'name', readonly=True),
        'order_id': fields.many2one('resto.order', 'Order', ondelete='cascade'),
        'meal_id': fields.many2one('resto.meal', 'meal', required=True),
        'date': fields.related('order_id', 'date', type='date', string="Date", readonly=True, store={
            'resto.order': (_get_line_order_ids, ['date'], 10), 
            'resto.order.line': (lambda self, cr, uid, ids, ctx: ids, [], 10),
            }),
        'supplier': fields.related('meal_id', 'supplier', type='many2one', relation='res.partner', string="Supplier", readonly=True, store=True),
        'user_id': fields.related('order_id', 'user_id', type='many2one', relation='res.users', string='User', readonly=True, store=True),
        'note': fields.text('Note'),
        'price': fields.float("Price"),
        'state': fields.selection([('new', 'New'), \
                                    ('confirmed', 'Received'), \
                                    ('ordered', 'Ordered'),  \
                                    ('cancelled', 'Cancelled')], \
                                'Status', readonly=True, select=True),
        'cashmove': fields.one2many('resto.cashmove', 'order_id', 'Cash Move', ondelete='cascade'),

    }
    _defaults = {
        'state': 'new',
    }