# -*- coding: utf-8 -*-

import time
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class WzDeliveryOrder(models.TransientModel):
    _name = 'wz.delivery.order'
    _description="Delivery Orders"

    images=fields.Binary('Images')
    image_name=fields.Char('Image Name')


    def order_delivered(self):
        active_id=self.env.context.get("active_id", False)
        delivery_id=self.env['wash.delivery.order'].browse(active_id)
        if delivery_id:
            delivery_id.state='delivered'
            delivery_id.laundry_id.state="done"




