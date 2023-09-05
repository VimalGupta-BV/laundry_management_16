# -*- coding: utf-8 -*-
##########################################################################

{
    'name': 'Laundry Management',
    'version': '16.0.1.0.1',
    'summary': """Complete Laundry Service Management""",
    'description': 'This module is very useful to manage all process of laundry service',
    "category": "Industries",
    'author': 'Brainvire Infotech',
    'company': 'Brainvire Infotech',
    'website': "https://www.brainvire.com/",
    'depends': ['base', 'mail', 'sale', 'account', 'uom', 'website','point_of_sale','hr'],
    'data': [
        'data/data.xml',
        'security/laundry_security.xml',
        'security/ir.model.access.csv',
        'wizard/wz_return_order.xml',
        'wizard/wz_picked_order.xml',
        'wizard/wz_delivery_order.xml',
        'wizard/wz_quality_check_view.xml',
        'sequences/tracking_number_seq_view.xml',
        'views/laundry_view.xml',
        'views/washing_view.xml',
        'views/config_view.xml',
        'views/laundry_report.xml',
        'views/laundry_label.xml',
        'data/email_template.xml',
        'wizard/wz_assign_deliveryperson.xml',       
        'views/order_submission_template.xml',
        'views/pickup_order_view.xml',
        'views/wash_deliveryorders_view.xml',        
        'views/wash_qulaity_check_view.xml'
        

    ],
    'assets': {
        'web.assets_frontend': [
          #  'laundry_management/static/src/css/bv_style.css',
            'laundry_management/static/src/js/*.js'
        ],
        'point_of_sale.assets': [
           # 'laundry_management/static/src/js/models.js',
            'laundry_management/static/src/xml/**/*.xml',
        ],
        'web.assets_backend': [],
        'web.assets_qweb': [
            'laundry_management/static/src/xml/**/*',
           
        ],
    },
    
    'images': ['static/description/banner.png'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}

