# -*- coding: utf-8 -*-

import time
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class WzAssignDeliveryPerson(models.TransientModel):
    _name = 'assign.delivery.person'
    _description="Delivery Person Assign"

    employee_id=fields.Many2one('hr.employee', string="Assinged Employee")

    def assinged_employee(self):
        for rec in self:
            print("Cccccccccccccccc", self.env.context)
            active_id=self.env.context.get("active_id", False)
            if self.env.context.get('pickup'):
                pickup_id=self.env['pickup.order'].browse(active_id)
                pickup_id.write({'employee_id':rec.employee_id.id,'state':'assigned_pickup','assidned_date':datetime.today()})

            else: 

                delivery_id=self.env['wash.delivery.order'].browse(active_id)
                delivery_id.write({'employee_id':rec.employee_id.id,'state':'assigned_delivery','assidned_date':datetime.today()})



