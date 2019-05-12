var destinationHover = {

  onReady: function () {
    $('.destination-container').hover(function () {
      $(this).find('.destination-top').addClass('invisible')
      $(this).find('.destination-display-on-hover').removeClass('invisible')
    }, function () {
      $(this).find('.destination-top').removeClass('invisible')
      $(this).find('.destination-display-on-hover').addClass('invisible')
    })
  }
}
$(document).ready(destinationHover.onReady)
