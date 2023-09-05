# -*- coding: utf-8 -*-

import time
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class WzOrderReturn(models.Model):
    _name = 'wz.order.return'
    _description="Order Return"

    reason=fields.Text('Reason')

    def cancel_order(self):
        active_id=self.env.context.get("active_id", False)
        laundry_id=self.env['laundry.order'].browse(active_id)
        if laundry_id:
            laundry_id.write({'return_reason':self.reason,'state':'return'})
