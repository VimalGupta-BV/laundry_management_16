# -*- coding: utf-8 -*-

import time
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class WashDeliveryOrders(models.Model):
    _name = 'wash.delivery.order'
    _description="Wash Delivery Orders"


    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('wash.delivery.order')
        return super(WashDeliveryOrders, self).create(vals)

    name=fields.Char('Delivery No.')
    laundry_id=fields.Many2one('laundry.order', string="Laundry Order No.")
    partner_id=fields.Many2one('res.partner', string="Delivery Address")
    state = fields.Selection([
        ('ready', 'Ready For Delivery'),
        ('assigned_delivery', 'Assigned Delivery Person'),
        ('on_the_way', 'On the Way'),
        ('delivered','Delivered'),
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



class WashDeliveryOption(models.Model):
    _name = 'wash.delivery.option'
    _description="Wash Delivery Options"


    name=fields.Char('Name')
    