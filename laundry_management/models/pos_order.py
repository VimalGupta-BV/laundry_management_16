# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import re

class PosOrder(models.Model):
    _inherit = 'pos.order'


    def create(self, vals):
        res=super().create(vals)
        partner_obj=self.env['res.partner']
        values={}
        if res.lines:
            if not res.partner_id:
                partner_id=partner_obj.sudo().search([('name','=','Walking Customer')], limit=1)
                if not partner_id:
                    partner_id=partner_obj.sudo().create({'name':'Walking Customer'})

                values.update({'partner_id':partner_id.id, 'partner_invoice_id':partner_id.id, 'partner_shipping_id':partner_id.id})
            else:
                values.update({'partner_id':res.partner_id.id, 'partner_invoice_id':res.partner_id.id, 'partner_shipping_id':res.partner_id.id})
            values.update({'order_date':res.date_order,'laundry_person':res.user_id.id, 
                            'delivery_type':'home' if res.to_ship else 'shop',
                            'pos_order_id':res.id

                        })
            lines=[]
            for line in res.lines:
                s=line.full_product_name
                s1 = s.replace(line.product_id.display_name, '')
                patn = re.sub(r"[\([{})\]]", "", s1)
                washing_type=False
                washing_type_obj=self.env['washing.type']
                if patn:
                    print("patnpatnpatn",patn ,type(patn))
                    washing_type=washing_type_obj.search([('name','=',patn),('is_pos','=',True)])
                    if not washing_type:
                        washing_type=washing_type_obj.create({"name":patn, 'assigned_person':res.user_id.id, 
                                                    'is_pos':True,'amount':line.price_unit})
                    print("washing_typewashing_type",washing_type)

                lines.append((0,0,{
                            'product_id':line.product_id.id,
                            'qty':line.qty,
                            'description':line.full_product_name,
                            'washing_type':washing_type.id,
                            'amount':line.price_unit
                    }))
            values.update({'order_lines':lines})
            print("valuesvalues",values,lines)
            laundry_id=self.env['laundry.order'].sudo().create(values)
            if laundry_id:
                laundry_id.confirm_order()
            print("laundry_idlaundry_id",laundry_id)

        return res
