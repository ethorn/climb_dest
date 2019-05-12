/* -------------------------------------------------------------------------
-------
-------   Currency Feature
-------   - Change currency when page loads (from cookie), and when
-------   someone changes the currency select form in filter bar.
-------
---------------------------------------------------------------------------- */

var currency = {

  onReady: function() {

    // When page loads
    currency.fromCookie(); 

    // When changing currency manually in select field
    $('select#currency').change( currency.onSelectChange )
  },

  onSelectChange: function() {
    $.getJSON($SCRIPT_ROOT + '/_convert_currency', {
        c: $(this).val()
      }, function(data) {
        
        $('span.money').each(function() {
          var money = $(this).text();
          var new_money = money * data.rate;
          var new_money_round = Math.round(new_money);
          $(this).text(new_money_round);
        })
        $('span.currency').html(data.new_currency);
      });
      return false;
  },

  fromCookie: function() {
    if (Cookies.get('currency') != undefined && Cookies.get('currency') != 'EUR') {
    
      var currency = Cookies.get('currency');
      var rate_from_euro = Cookies.get('rate_from_euro');
      
      if (rate_from_euro != 1) {
        
        // takes info from cookie and makes the current currency 
        // selected in the select#currency list:
        $('select#currency').val(currency);
        
        // change from euro to current currency when refreshing:
        $('span.money').each(function() {
          var money = $(this).text();
          var new_money = money * rate_from_euro;
          var new_money_round = Math.round(new_money);
          $(this).text(new_money_round);
        });

        $('span.currency').html(currency);
      }
    }
  }

};
$(document).ready(currency.onReady)
