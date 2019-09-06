var menu = {

  onReady: function () {

    $('.js-menu-mobile-button').click(function () {
      $('.js-menu').toggle();
    });

  }

}

$(document).ready(menu.onReady)
