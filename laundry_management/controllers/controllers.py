# -*- coding: utf-8 -*-
import werkzeug
from werkzeug.urls import url_encode
import re, math, random
import base64

import logging
_logger = logging.getLogger(__name__)

from odoo.http import request, route
from odoo import _, http
from odoo.addons.website.controllers.main import Website
from odoo.exceptions import UserError
from odoo.addons.auth_signup.models.res_users import SignupError

from odoo.addons.web.controllers.home import Home,SIGN_UP_REQUEST_PARAMS
from datetime import datetime, timedelta

TAG_RE = re.compile(r'<[^>]+>')

class LaundryWebsite(Website):

	@http.route(['/order_submission/',], type='http', auth="public", website=True)
	def submission_form(self, **post):
		product_tmpl_ids=request.env['product.product'].sudo().search([('active','=',True),('detailed_type','=','service')])
		service_type_ids=request.env['washing.type'].sudo().search([])
		values={'product_tmpl_ids':product_tmpl_ids,'service_type_ids':service_type_ids}
		return request.render("laundry_management.order_submission_form",values)

	@http.route(['/order_submit/',], type='http', auth="public", website=True,methods=['POST'])
	def submit_form(self, **post):
		partner_obj=request.env['res.partner']
		print("postpostpost",post, request.httprequest.form.getlist('product_tmpl_id'), request.httprequest.form.getlist('service_type_id'), request.httprequest.form.getlist('qty'))
		lines=[]
		for product, qty, wash in zip(request.httprequest.form.getlist('product_tmpl_id'), request.httprequest.form.getlist('qty'), request.httprequest.form.getlist('service_type_id')):
			print("TTTTTTTTTTTTTTt", product, qty,wash)
			lines.append((0,0,{
					'product_id':product,
					'qty':qty,
					'washing_type':wash
				}))
		partner_id=partner_obj.sudo().search([('mobile','=',post['mobile'])],limit=1)
		if not partner_id:
			partner_id=partner_obj.sudo().create({'name':post['name'],'mobile':post['mobile'], 'street':post['address']})

		vals={
			'order_date':datetime.today(),
			'laundry_person':request.env.user.id,
			'order_lines':lines,
			'partner_id':partner_id.id,
			'partner_invoice_id':partner_id.id,
			'partner_shipping_id':partner_id.id,
			'delivery_type':post['delivery_type'],
			'priority_type':post['priority_type'],
			'pickup_date':post['pickup_date'] or False,
			'state':'read_for_pickup' if post['pickup_date'] else 'draft'

			}
		print("valsvalsvalsvals",vals)
		order_id=request.env['laundry.order'].sudo().create(vals)
		print("order_idorder_idorder_id",order_id)
		if order_id and post['pickup_date']:
			pickup_id=request.env['pickup.order'].sudo().create({
															'partner_id':partner_id.id,
															'laundry_id':order_id.id,
															'pickup_date':post['pickup_date']
				})


		return request.render("laundry_management.order_success_page" ,{'order_id':order_id})
