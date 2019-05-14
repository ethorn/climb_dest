/* global $SCRIPT_ROOT, Cookies */
/* -------------------------------------------------------------------------
-------
-------   Currency Feature
-------   - Change currency when page loads (from cookie), and when
-------   someone changes the currency select form in filter bar.
-------
---------------------------------------------------------------------------- */

var currency = {

  onReady: function () {

    // When page loads
    currency.fromCookie()

    // When changing currency manually in select field
    $('select#currency').change(currency.onSelectChange)
  },

  onSelectChange: function () {
    $.getJSON($SCRIPT_ROOT + '/_convert_currency', {
      c: $(this).val()
    }, function (data) {

      $('span.money').each(function () {
        var money = $(this).text()
        var newMoney = money * data.rate
        var newMoneyRounded = Math.round(newMoney)
        $(this).text(newMoneyRounded)
      })
      $('span.currency').html(data.new_currency)
    })
    return false
  },

  fromCookie: function () {
    if (Cookies.get('currency') !== undefined && Cookies.get('currency') !== 'EUR') {

      var currency = Cookies.get('currency')
      var rateFromEuro = Cookies.get('rate_from_euro')

      if (rateFromEuro !== 1) {

        // takes info from cookie and makes the current currency
        // selected in the select#currency list:
        $('select#currency').val(currency)

        // change from euro to current currency when refreshing:
        $('span.money').each(function () {
          var money = $(this).text()
          var newMoney = money * rateFromEuro
          var newMoneyRounded = Math.round(newMoney)
          $(this).text(newMoneyRounded)
        })

        $('span.currency').html(currency)
      }
    }
  }

}
$(document).ready(currency.onReady)
