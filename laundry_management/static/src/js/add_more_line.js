odoo.define('laundry_management.addMoreline', function (require) {
'use strict';

console.log("1111111 Add More line in product detail");
var publicWidget = require('web.public.widget');
const Dialog = require('web.Dialog');
const {_t, qweb} = require('web.core');
const session = require('web.session');
var PortalSidebar = require('portal.PortalSidebar');

publicWidget.registry.addMoreline = publicWidget.Widget.extend({
    // select main div after div container in template 'RegistrationForm'
    selector: '.product_details',
    events: {
        'click #add-row': 'onClickaddmore',
        'click #remove-row': 'onClickremove',
 
    },

    onClickaddmore: function() {
    	var i = 1;
    	//const container = document.querySelector('.product_details')
		//container.querySelectorAll('.line-details').forEach((item, index) => {
		  // Clone it
		//var cloned = item.cloneNode(true)
		console.log("999999999kkkkkkkk");
		  // Add an increment number to label and input (so it's unique)
		  //cloned.querySelector('label').setAttribute('for', 'anything${index}')
		  //cloned.querySelector('input').setAttribute('id', 'anything${index}')
		  
		  // Append
		  //container.append(cloned)
		  //cloned.insertBefore( ".add-before" );
		//})
        /*console.log("2222222222222");
        var $clone = $( "tr.line-details" ).first().clone();
      	$clone.append( "<button type='button' class='remove-row'>-</button>" );
      	$clone.insertBefore( ".add-before" );*/

      	$("tbody tr:nth-child(1)").clone().find("input").each(function() {
		    var $clone=$(this).val('').attr('id', function(_, id) 

		    { return id + i 

			});
		  }).end().appendTo("table");
		 i++;
    },

    onClickremove: function(ev) {

    	console.log("onClickremoveonClickremove");
    	$(ev.currentTarget).closest("tr").remove();
    	//$(this).closest('tr').remove();
     },

})

console.log("Add More line in product detail");
});


/*const container = document.querySelector('.clone-container')
container.querySelectorAll('.clone-me').forEach((item, index) => {
  // Clone it
  let cloned = item.cloneNode(true)
  
  // Add an increment number to label and input (so it's unique)
  cloned.querySelector('label').setAttribute('for', `anything${index}`)
  cloned.querySelector('input').setAttribute('id', `anything${index}`)
  
  // Append
  container.append(cloned)
})*/