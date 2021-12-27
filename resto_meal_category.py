from xml.sax.saxutils import escape
import time
from openerp.osv import fields, osv
from datetime import datetime
from lxml import etree
from openerp import tools
from openerp.tools.translate import _


class resto_meal_category(osv.Model):
    """ 
    resto meal category 
    """
    _name = 'resto.meal.category'
    _description = 'resto meal category'
    _columns = {
        'name': fields.char('Category'), #such as PIZZA, SANDWICH, PASTA, CHINESE, BURGER, ...
    }