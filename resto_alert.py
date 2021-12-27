from xml.sax.saxutils import escape
import time
from openerp.osv import fields, osv
from datetime import datetime
from lxml import etree
from openerp import tools
from openerp.tools.translate import _

class resto_alert(osv.Model):
    """ 
    resto alert 
    """
    _name = 'resto.alert'
    _description = 'resto Alert'
    _columns = {
        'message': fields.text('Message', size=256, required=True),
        'alter_type': fields.selection([('specific', 'Specific Day'), \
                                    ('week', 'Every Week'), \
                                    ('days', 'Every Day')], \
                                string='Recurrency', required=True, select=True),
        'specific_day': fields.date('Day'),
        'monday': fields.boolean('Monday'),
        'tuesday': fields.boolean('Tuesday'),
        'wednesday': fields.boolean('Wednesday'),
        'thursday': fields.boolean('Thursday'),
        'friday': fields.boolean('Friday'),
        'saturday': fields.boolean('Saturday'),
        'sunday':  fields.boolean('Sunday'),
        'active_from': fields.float('Between', required=True),
        'active_to': fields.float('And', required=True),
    }
    _defaults = {
        'alter_type': 'specific',
        'specific_day': fields.date.context_today,
        'active_from': 7,
        'active_to': 23,
    }
