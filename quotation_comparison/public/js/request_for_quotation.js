frappe.ui.form.on('Request for Quotation', {
	refresh: function(frm) {
		set_custom_buttons(frm);
	}
});

let set_custom_buttons = function(frm){
	if(frm.doc.docstatus==1){
		//Comparison Sheet
		frm.add_custom_button('Compare Quotations', () => {
			create_comparison_sheet(frm);
		});
	}
}

let create_comparison_sheet = function(frm){
	console.log("create_comparison_sheet");
	frappe.model.open_mapped_doc({
		method: "quotation_comparison.quotation_comparison.doctype.quotation_comparison_sheet.quotation_comparison_sheet.create_comparison_sheet",
		frm: frm
	});
}
