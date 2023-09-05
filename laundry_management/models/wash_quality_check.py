# -*- coding: utf-8 -*-

import time
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class WashQualityCheck(models.Model):
    _name = 'wash.quality.check'
    _description="Wash Quality Check"


    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('wash.quality.check')
        return super(WashQualityCheck, self).create(vals)


    name=fields.Char('Delivery No.')
    laundry_id=fields.Many2one('laundry.order', string="Laundry Order No.")
    partner_id=fields.Many2one('res.partner', string="Customer")
    state = fields.Selection([
        ('ready', 'Ready For Quality Check'),
        ('done','Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, default='ready')



