var closeBox = {

  onReady: function () {
    if (Cookies.get('announcements') === undefined) {
      $('.announcements').show()
    }

    $('.js-close-box').click(function () {
      $('.announcements').hide()
      Cookies.set('announcements', 'close');
    })

  }

}

$(document).ready(closeBox.onReady)