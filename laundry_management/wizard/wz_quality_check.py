# -*- coding: utf-8 -*-

import time
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class WzQualityCheck(models.TransientModel):
    _name = 'wz.quality.check'
    _description="Quality check Orders"


    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        active_model = self.env.context.get("active_model", False)        
        request_line_ids = []
        line_id=[]
        request_ids = self.env.context.get("active_ids", False)
        pickup_id=self.env['wash.quality.check'].search([('id','=',self.env.context.get('active_id'))])
        for req in pickup_id.laundry_id.order_lines:
         line_id.append((0,0,{
            'product_id':req.product_id.id,
            'qty':req.qty,
            'washing_type':req.washing_type
            }))
       
        res['line_ids']=line_id
        res['pickup_id']=pickup_id.id
        res['laundry_id']=pickup_id.laundry_id.id
        return res



    pickup_id=fields.Many2one('pickup.order', string="Picup Order No.")
    line_ids=fields.One2many('wz.quality.check.line', 'wz_quality_check_id')
    laundry_id = fields.Many2one('laundry.order', invisible=1)

    comment=fields.Text('Comment')



    def order_quality(self):
        active_id=self.env.context.get("active_id", False)
        quality_id=self.env['wash.quality.check'].browse(active_id)
        if quality_id:
            delivery_id=self.env['wash.delivery.order'].create({'partner_id':self.laundry_id.partner_shipping_id.id,
                                                                'laundry_id':self.laundry_id.id
                })
            quality_id.state="done"





class WzQualityCheckLine(models.TransientModel):
    _name = 'wz.quality.check.line'
    _description="Quality check Orders Line"



    wz_quality_check_id=fields.Many2one('wz.quality.check.line')
    product_id = fields.Many2one('product.product', string='Dress', required=1)
    qty = fields.Integer(string='Qty', required=1)
    washing_type = fields.Many2one('washing.type', string='Washing Type',
                                   required=1)
