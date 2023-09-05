# -*- coding: utf-8 -*-

import time
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class WzPickecOrder(models.TransientModel):
    _name = 'wz.picked.order'
    _description="Picked Orders"


    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        active_model = self.env.context.get("active_model", False)        
        request_line_ids = []
        line_id=[]
        request_ids = self.env.context.get("active_ids", False)
        pickup_id=self.env['pickup.order'].search([('id','=',self.env.context.get('active_id'))])
        for req in pickup_id.laundry_id.order_lines:
         line_id.append((0,0,{
            'product_id':req.product_id.id,
            'qty':req.qty,
            'picked_qty':req.picked_qty if req.picked_qty >0 else req.qty,
            'washing_type':req.washing_type
            }))
       
        res['line_ids']=line_id
        res['pickup_id']=pickup_id.id
        res['laundry_id']=pickup_id.laundry_id.id
        return res



    pickup_id=fields.Many2one('pickup.order', string="Picup Order No.")
    line_ids=fields.One2many('wz.picked.order.line', 'wz_picked_order_id')
    laundry_id = fields.Many2one('laundry.order', invisible=1)


    def order_picked_items(self):
        for rec in self:
            if rec.line_ids:
                extra_lines=[]
                for req_line in rec.line_ids:
                    for line in rec.laundry_id.order_lines:
                        if req_line.product_id == line.product_id:
                            line.picked_qty=req_line.picked_qty
                        

                for req_line1 in rec.line_ids:
                    if req_line1.extra_product:
                        extra_lines.append((0,0, {
                                    'laundry_obj':rec.laundry_id.id,
                                    'product_id':req_line.product_id.id,
                                    'qty':req_line.qty,
                                    'picked_qty':req_line.picked_qty,
                                    'washing_type':req_line.washing_type.id
                                }))

                rec.laundry_id.write({'order_lines':extra_lines})
                rec.pickup_id.order_picked()


   




class WzPickecOrderline(models.TransientModel):
    _name = 'wz.picked.order.line'
    _description="Picked Orders Line"



    wz_picked_order_id=fields.Many2one('wz.picked.order')
    product_id = fields.Many2one('product.product', string='Dress', required=1)
    qty = fields.Integer(string='No of items', required=1)
    picked_qty = fields.Integer(string='Picked Qty', required=1)
    washing_type = fields.Many2one('washing.type', string='Washing Type',
                                   required=1)
    extra_product=fields.Boolean('Extra Product')


    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:

            self.extra_product=True

        else:
            self.extra_product=False