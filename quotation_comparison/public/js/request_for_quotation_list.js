frappe.listview_settings['Request for Quotation'] = {
  onload: function(listview) {
    listview.page.add_inner_button(__("Goto Comparison Tool"), function() {
      frappe.set_route('List', 'Quotation Comparison Sheet' );
    }).addClass("btn-primary");
  }
}
