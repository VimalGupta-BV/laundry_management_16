/** @odoo-module **/
// Copyright (C) 2023 - Today: GRAP (http://www.grap.coop)
// @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
// License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


import field_utils from "web.field_utils";
import { PosGlobalState } from "point_of_sale.models";
//import Registries from "point_of_sale.Registries";

// /////////////////////////////
// Overload models.Order
// /////////////////////////////
console.log("PosDeliveryOptionPosDeliveryOptionPosDeliveryOption");
const PosDeliveryOption = (PosGlobalState) =>
    class PosDeliveryOption extends PosGlobalState {


        
        async _processData(loadedData) {

             await this._processData(loadedData);
             this.delivery_option=loadedData['wash.delivery.option'];


            
    
        }


    }

Registries.Model.extend(PosGlobalState, PosDeliveryOption);