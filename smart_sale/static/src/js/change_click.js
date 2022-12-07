var Glang = ''
odoo.define('smart_sale.change_params', function(require) {
    var session = require('web.session');
    Glang = session.user_context.lang
})

var layout_payment = document.getElementsByClassName('report_layout_container')[0].getElementsByTagName('a')
if(layout_payment){
    for (let i = 0; i < layout_payment.length; i++) {
        if (layout_payment[i].textContent == "Preview") {
            layout_payment[i].innerText = "Xem trước"
        }
    }
}