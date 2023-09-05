# -*- coding: utf-8 -*-

import time
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class LaundryManagement(models.Model):
    _name = 'laundry.order'
    _inherit = 'mail.thread'
    _description = "Laundry Order"
    _order = 'order_date desc, id desc'

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('laundry.order')
        return super(LaundryManagement, self).create(vals)

    @api.depends('order_lines')
    def get_total(self):
        total = 0
        for obj in self:
            for each in obj.order_lines:
                total += each.amount
            obj.total_amount = total

    def confirm_order(self):
        self.state = 'order'
        sale_obj = self.env['sale.order'].create(
            {'partner_id': self.partner_id.id,
             'partner_invoice_id': self.partner_invoice_id.id,
             'partner_shipping_id': self.partner_shipping_id.id})
        self.sale_obj = sale_obj
        product_id = self.env.ref('laundry_management.laundry_service')
        self.env['sale.order.line'].create({'product_id': product_id.id,
                                            'name': 'Laundry Service',
                                            'price_unit': self.total_amount,
                                            'order_id': sale_obj.id
                                            })
        for each in self:
            for obj in each.order_lines:
                self.env['washing.washing'].create(
                    {'name': obj.product_id.name + '-Washing',
                     'user_id': obj.washing_type.assigned_person.id,
                     'description': obj.description,
                     'laundry_obj': obj.id,
                     'state': 'draft',
                     'planned_hours':obj.planned_hours,
                     'washing_date': datetime.now().strftime(
                         '%Y-%m-%d %H:%M:%S')})

    def create_invoice(self):
        if self.sale_obj.state in ['draft', 'sent']:
            self.sale_obj.action_confirm()
        self.invoice_status = self.sale_obj.invoice_status
        return {
            'name': 'Create Invoice',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sale.advance.payment.inv',
            'type': 'ir.actions.act_window',
            'context': {'laundry_sale_obj': self.sale_obj.id},
            'target': 'new'
        }

    def return_dress(self):
        self.state = 'return'

    def cancel_order(self):
        self.state = 'cancel'

    def _invoice_count(self):
        wrk_ordr_ids = self.env['account.move'].search([('invoice_origin', '=', self.sale_obj.name)])
        self.invoice_count = len(wrk_ordr_ids)

    def _work_count(self):
        if self.id:
            wrk_ordr_ids = self.env['washing.washing'].search([('laundry_obj.laundry_obj.id', '=', self.id)])
            self.work_count = len(wrk_ordr_ids)
        else:
            self.work_count = False

    def action_view_laundry_works(self):

        work_obj = self.env['washing.washing'].search(
            [('laundry_obj.laundry_obj.id', '=', self.id)])
        work_ids = []
        for each in work_obj:
            work_ids.append(each.id)
        view_id = self.env.ref('laundry_management.washing_form_view').id
        if work_ids:
            if len(work_ids) <= 1:
                value = {
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'washing.washing',
                    'view_id': view_id,
                    'type': 'ir.actions.act_window',
                    'name': _('Works'),
                    'res_id': work_ids and work_ids[0]
                }
            else:
                value = {
                    'domain': str([('id', 'in', work_ids)]),
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'washing.washing',
                    'view_id': False,
                    'type': 'ir.actions.act_window',
                    'name': _('Works'),
                    # 'res_id': work_ids
                }
            return value

    def action_view_invoice(self):
        self.ensure_one()
        inv_obj = self.env['account.move'].search(
            [('invoice_origin', '=', self.sale_obj.name)])
        inv_ids = []
        for each in inv_obj:
            inv_ids.append(each.id)
        view_id = self.env.ref('account.view_move_form').id
        if inv_ids:
            if len(inv_ids) <= 1:
                value = {
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'account.move',
                    'view_id': view_id,
                    'type': 'ir.actions.act_window',
                    'name': _('Invoice'),
                    'res_id': inv_ids and inv_ids[0]
                }
            else:
                value = {
                    'domain': str([('id', 'in', inv_ids)]),
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'account.move',
                    'view_id': False,
                    'type': 'ir.actions.act_window',
                    'name': _('Invoice'),
                    # 'res_id': inv_ids
                }
            return value

    name = fields.Char(string="Label", copy=False)
    invoice_status = fields.Selection([
        ('upselling', 'Upselling Opportunity'),
        ('invoiced', 'Fully Invoiced'),
        ('to invoice', 'To Invoice'),
        ('no', 'Nothing to Invoice')
    ], string='Invoice Status', invisible=1, related='sale_obj.invoice_status',
        store=True)
    sale_obj = fields.Many2one('sale.order', invisible=1)
    invoice_count = fields.Integer(compute='_invoice_count',
                                   string='# Invoice')
    work_count = fields.Integer(compute='_work_count', string='# Works')
    partner_id = fields.Many2one('res.partner', string='Customer',
                                 readonly=True,
                                 states={'draft': [('readonly', False)],
                                         'order': [('readonly', False)]},
                                 required=True,
                                 change_default=True, index=True,
                                 )
    partner_invoice_id = fields.Many2one('res.partner',
                                         string='Invoice Address',
                                         readonly=True, required=True,
                                         states={
                                             'draft': [('readonly', False)],
                                             'order': [('readonly', False)]},
                                         help="Invoice address for current sales order.")
    partner_shipping_id = fields.Many2one('res.partner',
                                          string='Delivery Address',
                                          readonly=True, required=True,
                                          states={
                                              'draft': [('readonly', False)],
                                              'order': [('readonly', False)]},
                                          help="Delivery address for current sales order.")
    order_date = fields.Datetime(string='Date', readonly=True, index=True,
                                 states={'draft': [('readonly', False)],
                                         'order': [('readonly', False)]},
                                 copy=False, default=fields.Datetime.now, )
    laundry_person = fields.Many2one('res.users', string='Laundry Person',
                                     required=1)
    order_lines = fields.One2many('laundry.order.line', 'laundry_obj',
                                  required=1, ondelete='cascade')
    total_amount = fields.Float(compute='get_total', string='Total', store=1)
    currency_id = fields.Many2one("res.currency", string="Currency")
    note = fields.Text(string='Terms and conditions')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('read_for_pickup', 'Ready For Pickup'),
        ('order', 'Laundry Order'),
        ('process', 'Processing'),
        ('done', 'Done'),
        ('ready_delivery', 'Ready To Delivery'),
        ('delivered','Delivered'),
        ('return', 'Returned'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True,
        track_visibility='onchange', default='draft')

    return_reason=fields.Text('Return Reason')

    delivery_type=fields.Selection([
        ('home', 'Home Delivery'),
        ('shop', 'Collect From Shop'),
        ],default="home", string="Delivery Type")

    priority_type=fields.Selection([
        ('normal', 'Normal'),
        ('Urgent', 'Urgent'),
        ],default="normal", string="Priority Type")

    pickup_date=fields.Date('Pickup Date')

    delivery_option_id=fields.Many2one('wash.delivery.option', string="Delivery Option")
    pos_order_id=fields.Many2one('pos.order', string="Pos Order No.")

    def action_pickuporder_view(self):
        self.ensure_one()
        result =  {    'name': _('Pickup Order'),
                      'type': 'ir.actions.act_window',
                      'res_model': 'pickup.order',
                      'view_mode': 'tree',
                      'domain': [('laundry_id', '=', self.id)],
                      'context': {'create': False, 'delete': False, 'edit':False}
                     }
        return result

    def action_deliveryorder_view(self):
        self.ensure_one()
        result =  {    'name': _('Delivery Order'),
                      'type': 'ir.actions.act_window',
                      'res_model': 'wash.delivery.order',
                      'view_mode': 'tree',
                      'domain': [('laundry_id', '=', self.id)],
                      'context': {'create': False, 'delete': False, 'edit':False}
                     }
        return result


class LaundryManagementLine(models.Model):
    _name = 'laundry.order.line'
    _description = "Laundry Order Line"

    @api.depends('washing_type', 'extra_work', 'qty')
    def get_amount(self):
        for obj in self:
            total = obj.washing_type.amount * obj.qty
            for each in obj.extra_work:
                total += each.amount * obj.qty
            obj.amount = total

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].get('laundry.order.line')
        new_id = super(LaundryManagementLine, self).create(vals)
        return new_id

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        washing_works=self.env['washing.work'].search(['|',('is_quality_check','=',True),('is_packing','=',True)])
        print("washing_work",washing_works)
        if washing_works:
            res['extra_work']=[(6,0, (washing_work.id for washing_work in washing_works))]
            res['planned_hours'] =sum(ln.planned_hours for ln in washing_works)

        return res


    name=fields.Char('Tracking No.')
    product_id = fields.Many2one('product.product', string='Dress', required=1)
    qty = fields.Integer(string='No of items', required=1)
    picked_qty = fields.Integer(string='Picked Qty', required=1)
    description = fields.Text(string='Description')
    washing_type = fields.Many2one('washing.type', string='Washing Type',
                                   required=1)
    extra_work = fields.Many2many('washing.work', string='Extra Work')
    amount = fields.Float(compute='get_amount', string='Amount')
    laundry_obj = fields.Many2one('laundry.order', invisible=1)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('wash', 'Washing'),
        ('extra_work', 'Make Over'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, default='draft')

    planned_hours=fields.Float('Planned Minutes')
    consumed_hours=fields.Float('Consumed Minutes')


    @api.onchange('washing_type')
    def _onchange_planned_hrs(self):
        for rec in self:
            if rec.washing_type:
                rec.planned_hours = rec.planned_hours  + rec.washing_type.planned_hours

            else:
                rec.planned_hours=rec.planned_hours 


class WashingType(models.Model):
    _name = 'washing.type'
    _description = "Washing TYpe"

    name = fields.Char(string='Name', required=1)
    assigned_person = fields.Many2one('res.users', string='Assigned Person',
                                      required=1)
    amount = fields.Float(string='Service Charge', required=1)
    planned_hours=fields.Float('Planned Minutes')
    is_pos=fields.Boolean('Is Pos', default=False)


class ExtraWork(models.Model):
    _name = 'washing.work'
    _description = 'Washing Work'

    name = fields.Char(string='Name', required=1)
    assigned_person = fields.Many2one('res.users', string='Assigned Person',
                                      required=1)
    amount = fields.Float(string='Service Charge', required=1)
    planned_hours=fields.Float('Planned Minutes')

    is_quality_check=fields.Boolean('Is Quality Check')
    is_packing=fields.Boolean('Is Packing')


class Washing(models.Model):
    _name = 'washing.washing'
    _description = 'Washing Washing'

    def start_wash(self):
        if not self.laundry_works:
            self.laundry_obj.state = 'wash'
            self.laundry_obj.laundry_obj.state = 'process'
        for each in self:
            for obj in each.product_line:
                self.env['sale.order.line'].create(
                    {'product_id': obj.product_id.id,
                     'name': obj.name,
                     'price_unit': obj.price_unit,
                     'order_id': each.laundry_obj.laundry_obj.sale_obj.id,
                     'product_uom_qty': obj.quantity,
                     'product_uom': obj.uom_id.id,
                     })
        self.state = 'process'
        duration_id=self.env['bv.washing.time.duration'].create({'start_date':datetime.now(),'washing_id':self.id, 'state':'start'})
        #self.start_date= datetime.now()

    def set_to_stop(self):
        self.state='stop'
        duration_id=self.env['bv.washing.time.duration'].search([('washing_id','=',self.id),('finished_date','=',False)])
        if duration_id:
            duration_id.finished_date=datetime.now()
            duration_id.state='stop'

    def set_to_restart(self):
        self.state='restart'
        duration_id=self.env['bv.washing.time.duration'].create({'start_date':datetime.now(),'washing_id':self.id, 'state':'restart'})


    def set_to_done(self):
        self.state = 'done'
        duration_id=self.env['bv.washing.time.duration'].search([('washing_id','=',self.id),('finished_date','=',False)])
        if duration_id:
            duration_id.finished_date=datetime.now()
            duration_id.state='done'

        f = 0
        if not self.laundry_works:
            if self.laundry_obj.extra_work:
                for each in self.laundry_obj.extra_work:
                    self.create({'name': each.name,
                                 'user_id': each.assigned_person.id,
                                 'description': self.laundry_obj.description,
                                 'laundry_obj': self.laundry_obj.id,
                                 'state': 'draft',
                                 'laundry_works': True,
                                 'washing_date': datetime.now().strftime(
                                     '%Y-%m-%d %H:%M:%S')})
                self.laundry_obj.state = 'extra_work'
        laundry_obj = self.search([('laundry_obj.laundry_obj', '=',
                                    self.laundry_obj.laundry_obj.id)])
        mail_template = self.env.ref('laundry_management.email_template_order_ready')
        for each in laundry_obj:
            if each.state != 'done' or each.state == 'cancel':
                f = 1
                break
        if f == 0:
            self.laundry_obj.laundry_obj.state = 'done'

            

            delivery_id=self.env['wash.delivery.order'].create({'partner_id':self.laundry_obj.laundry_obj.partner_shipping_id.id,
                                                                'laundry_id':self.laundry_obj.laundry_obj.id
                })
            #self.laundry_obj.laundry_obj.state='ready_delivery'

            #mail_template.send_mail(self.laundry_obj.laundry_obj.id, force_send=True)
        laundry_obj1 = self.search([('laundry_obj', '=', self.laundry_obj.id)])
        f1 = 0
        for each in laundry_obj1:
            if each.state != 'done' or each.state == 'cancel':
                f1 = 1
                break
        if f1 == 0:
            self.laundry_obj.state = 'done'
            mail_template.send_mail(self.laundry_obj.laundry_obj.id, force_send=True)

            consumed_hours=sum(wash.total_duration for wash in self.env['washing.washing'].search([('laundry_obj','=',self.laundry_obj.id)]))
            if consumed_hours:
                self.laundry_obj.consumed_hours=consumed_hours
            else:
                self.laundry_obj.consumed_hours=0.0

    @api.depends('product_line')
    def get_total(self):
        total = 0
        for obj in self:
            for each in obj.product_line:
                total += each.subtotal
            obj.total_amount = total

    name = fields.Char(string='Work')
    laundry_works = fields.Boolean(default=False, invisible=1)
    user_id = fields.Many2one('res.users', string='Assigned Person')
    washing_date = fields.Datetime(string='Date')
    description = fields.Text(string='Description')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('process', 'Process'),
        ('stop', 'Stop'),
        ('restart','Restart'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, default='draft')
    laundry_obj = fields.Many2one('laundry.order.line', invisible=1)
    product_line = fields.One2many('wash.order.line', 'wash_obj',
                                   string='Products', ondelete='cascade')
    total_amount = fields.Float(compute='get_total', string='Grand Total')
    planned_hours=fields.Float('Planned Hrs')
    washing_time_duration_ids=fields.One2many('bv.washing.time.duration','washing_id')
    
    total_duration=fields.Float('Duration', compute="calculate_duration")



    @api.depends('washing_time_duration_ids')
    def calculate_duration(self):
        for rec in self:
            if rec.washing_time_duration_ids:
                rec.total_duration=sum(line.total_duration for line in rec.washing_time_duration_ids)

            else:
                rec.total_duration=0.0

        pass
        # for rec in self:
        #     datetimeFormat= '%Y-%m-%d %H:%M:%S.%f' 
        #     if rec.start_date and rec.finished_date:
        #         d1 = datetime.strptime(str(rec.start_date),datetimeFormat)

        #         d2 = datetime.strptime(str(rec.finished_date),datetimeFormat)
        #         duration=(d2-d1)
        #         print("durationdurationdurationduration",duration, duration.seconds, duration.seconds/360)
        #         rec.total_duration=duration.seconds/60
        #     else:
        #         rec.total_duration=0.0
              



class SaleOrderInherit(models.Model):
    _name = 'wash.order.line'
    _description = 'Washing Order LINE'

    @api.depends('price_unit', 'quantity')
    def compute_amount(self):
        total = 0
        for obj in self:
            total += obj.price_unit * obj.quantity
        obj.subtotal = total

    wash_obj = fields.Many2one('washing.washing', string='Order Reference',
                               ondelete='cascade')
    name = fields.Text(string='Description', required=True)
    uom_id = fields.Many2one('uom.uom', 'Unit of Measure ', required=True)
    quantity = fields.Integer(string='Quantity')
    product_id = fields.Many2one('product.product', string='Product')
    price_unit = fields.Float('Unit Price', default=0.0,
                              related='product_id.list_price')
    subtotal = fields.Float(compute='compute_amount', string='Subtotal',
                            readonly=True, store=True)



class WashingTimeDuration(models.Model):
    _name="bv.washing.time.duration"
    _description="time Duration"

    start_date=fields.Datetime('Start Date')
    finished_date=fields.Datetime('Finished Date')
    total_duration=fields.Float('Duration', compute="calculate_duration")
    washing_id=fields.Many2one('washing.washing')
    state = fields.Selection([
        ('start', 'Start'),
        ('stop', 'Stop'),
        ('restart','Restart'),
        ('done', 'Done'),
    ], string='Status', readonly=True, copy=False, index=True, default='start')

    @api.depends('start_date','finished_date')
    def calculate_duration(self):
        for rec in self:
            datetimeFormat= '%Y-%m-%d %H:%M:%S.%f' 
            if rec.start_date and rec.finished_date:
                d1 = datetime.strptime(str(rec.start_date),datetimeFormat)

                d2 = datetime.strptime(str(rec.finished_date),datetimeFormat)
                duration=(d2-d1)
                print("durationdurationdurationduration",duration, duration.seconds, duration.seconds/360)
                rec.total_duration=duration.seconds/60
            else:
                rec.total_duration=0.0


class LaundryManagementInvoice(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    def create_invoices(self):
        context = self._context
        if context.get('laundry_sale_obj'):
            sale_orders = self.env['sale.order'].browse(
                context.get('laundry_sale_obj'))

        else:
            sale_orders = self.env['sale.order'].browse(
                self._context.get('active_ids', []))
        if self.advance_payment_method == 'delivered':
            sale_orders._create_invoices()
        elif self.advance_payment_method == 'all':
            sale_orders._create_invoices()(final=True)
        else:
            # Create deposit product if necessary
            if not self.product_id:
                vals = self._prepare_deposit_product()
                self.product_id = self.env['product.product'].create(vals)

            self.env['ir.config_parameter'].sudo().set_param('sale.default_deposit_product_id', self.product_id.id)
            sale_line_obj = self.env['sale.order.line']
            for order in sale_orders:
                if self.advance_payment_method == 'percentage':
                    amount = order.amount_untaxed * self.amount / 100
                else:
                    amount = self.amount
                if self.product_id.invoice_policy != 'order':
                    raise UserError(_(
                        'The product used to invoice a down payment should have an invoice policy set to "Ordered'
                        ' quantities". Please update your deposit product to be able to create a deposit invoice.'))
                if self.product_id.type != 'service':
                    raise UserError(_(
                        "The product used to invoice a down payment should be of type 'Service'. Please use another "
                        "product or update this product."))
                taxes = self.product_id.taxes_id.filtered(
                    lambda
                        r: not order.company_id or r.company_id == order.company_id)
                if order.fiscal_position_id and taxes:
                    tax_ids = order.fiscal_position_id.map_tax(taxes).ids
                else:
                    tax_ids = taxes.ids
                so_line = sale_line_obj.create({
                    'name': _('Advance: %s') % (time.strftime('%m %Y'),),
                    'price_unit': amount,
                    'product_uom_qty': 0.0,
                    'order_id': order.id,
                    'discount': 0.0,
                    'product_uom': self.product_id.uom_id.id,
                    'product_id': self.product_id.id,
                    'tax_id': [(6, 0, tax_ids)],
                })
                self._create_invoice(order, so_line, amount)
        if self._context.get('open_invoices', False):
            return sale_orders.action_view_invoice()
        return {'type': 'ir.actions.act_window_close'}

    def _create_invoice(self, order, so_line, amount):
        if (
                self.advance_payment_method == 'percentage' and self.amount <= 0.00) or (
                self.advance_payment_method == 'fixed' and self.fixed_amount <= 0.00):
            raise UserError(
                _('The value of the down payment amount must be positive.'))
        if self.advance_payment_method == 'percentage':
            amount = order.amount_untaxed * self.amount / 100
            name = _("Down payment of %s%%") % (self.amount,)
        else:
            amount = self.fixed_amount
            name = _('Down Payment')

        invoice_vals = {
            'move_type': 'out_invoice',
            'invoice_origin': order.name,
            'invoice_user_id': order.user_id.id,
            'narration': order.note,
            'partner_id': order.partner_invoice_id.id,
            'fiscal_position_id': order.fiscal_position_id.id or order.partner_id.property_account_position_id.id,
            'partner_shipping_id': order.partner_shipping_id.id,
            'currency_id': order.pricelist_id.currency_id.id,
            'ref': order.client_order_ref,
            'invoice_payment_term_id': order.payment_term_id.id,
            'team_id': order.team_id.id,
            'campaign_id': order.campaign_id.id,
            'medium_id': order.medium_id.id,
            'source_id': order.source_id.id,
            'invoice_line_ids': [(0, 0, {
                'name': name,
                'price_unit': amount,
                'quantity': 1.0,
                'product_id': self.product_id.id,
                'product_uom_id': so_line.product_uom.id,

                'sale_line_ids': [(6, 0, [so_line.id])],
                'analytic_tag_ids': [(6, 0, so_line.analytic_tag_ids.ids)],
                'analytic_account_id': order.analytic_account_id.id or False,
            })],
        }
        if order.fiscal_position_id:
            invoice_vals['fiscal_position_id'] = order.fiscal_position_id.id
        invoice = self.env['account.move'].create(invoice_vals)
        invoice.message_post_with_view('mail.message_origin_link',
                                       values={'self': invoice,
                                               'origin': order},
                                       subtype_id=self.env.ref(
                                           'mail.mt_note').id)
