# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class PosSession(models.Model):
    _inherit = 'pos.session'


    def _pos_ui_models_to_load(self):

        result=super()._pos_ui_models_to_load()

        result +=['wash.delivery.option']

        return result


    def _loader_params_wash_delivery_option(self):
        return {
            'search_params': {
               
                'fields': [                    
                   'name',
                ],
            }
        }

    def _get_pos_ui_wash_delivery_option(self, params):
        print("9999999999",self.env['wash.delivery.option'].search_read(**params['search_params']))
        return self.env['wash.delivery.option'].search_read(**params['search_params'])