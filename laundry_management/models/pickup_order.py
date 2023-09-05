# -*- coding: utf-8 -*-

import time
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class PickupOrder(models.Model):
    _name = 'pickup.order'
    _description="Pickup Orders"


    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('pickup.order')
        return super(PickupOrder, self).create(vals)

    name=fields.Char('Pickup Number')
    laundry_id=fields.Many2one('laundry.order', string="Laundry Order No.")
    partner_id=fields.Many2one('res.partner', string="Delivery Address")
    pickup_date=fields.Date('Pickup Date')
    picked_date=fields.Date('Picked Date')

    state = fields.Selection([
        ('ready', 'Ready For Pickup'),
        ('assigned_pickup', 'Assigned Pickup Person'),
        ('picked', 'picked'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, default='ready')

    employee_id=fields.Many2one('hr.employee', string="Assinged Employee")
    assidned_date=fields.Date('Assinged Date')

    def action_order_view(self):
        self.ensure_one()
        result =  {    'name': _('Laundry Order'),
                      'type': 'ir.actions.act_window',
                      'res_model': 'laundry.order',
                      'view_mode': 'form',
                      'res_id':self.laundry_id.id,
                      'target':'new',
                      'domain': [('id', '=', self.laundry_id.id)],
                      'context': {'create': False, 'delete': False, 'edit':False}
                     }
        return result

    def order_picked(self):
        self.state='picked'
        self.picked_date=datetime.today()
        self.laundry_id.confirm_order()
