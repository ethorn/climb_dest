/* -------------------------------------------------------------------------
-------
-------		Add Destination Page
-------		- Make main discipline Select input into Buttons
-------
---------------------------------------------------------------------------- */

var selectIntoButtons =  {

	onReady: function() {

		// Create hidden input to keep track of selected value when replacing Select input
		selectIntoButtons.init();

		// Replace each option with a button
		$("select#main_discipline option").unwrap().each(function() {
		    var btn = $('<div class="main-discipline-btn">'+$(this).text()+'</div>');
		    //if($(this).is(':checked')) btn.addClass('on');
		    $(this).replaceWith(btn);
		});

		// Change value of hidden input when clicking the buttons
		$(document).on('click', '.main-discipline-btn', function() {
		    $('.main-discipline-btn').removeClass('on');
		    $(this).addClass('on');
		    $('input[name="' + selectIntoButtons.selectName + '"]').val($(this).text().toLowerCase());
		});
	},

	init: function() {
		
		selectIntoButtons.selectName = $('select#main_discipline').attr('name');

		// add a hidden element with the same name as the select
		var hidden = $('<input type="hidden" name="' + selectIntoButtons.selectName + '">');
		hidden.val($('select#main_discipline').val());
		hidden.insertAfter($('select#main_discipline'));
	}

};
$(document).ready( selectIntoButtons.onReady );
