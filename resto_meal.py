from xml.sax.saxutils import escape
import time
from openerp.osv import fields, osv
from datetime import datetime
from lxml import etree
from openerp import tools
from openerp.tools.translate import _


class resto_meal(osv.Model):
    """ 
    resto meal 
    """
    _name = 'resto.meal'
    _description = 'resto meal'
    _columns = {
        'name': fields.char('meal', required=True, size=64),
        'category_id': fields.many2one('resto.meal.category', 'Category'),
        'description': fields.text('Description', size=256),
        'price': fields.float('Price', digits=(16,2)), #TODO: use decimal precision of 'Account', move it from meal to decimal_precision
        'supplier': fields.many2one('res.partner', 'Supplier'),
    }