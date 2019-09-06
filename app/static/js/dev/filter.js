/* -------------------------------------------------------------------------
-------
-------   Filterbar Features
-------
-------   - filterBarMobile
-------     * Show/hides filter container for mobile
-------     * Turn main discipline <Select> into Buttons
-------
-------   - filterBarDesktop
-------     * Making dropdowns work
-------
-------   - filterLoad
-------     * Triggers loadDestinations for all filter submits
-------     * Changes arrows on ASC/DESC
-------     * loadDestinations
-------
---------------------------------------------------------------------------- */

// For the filter box that appears when clicking "filter" on mobile
var filterBarMobile = {
  onReady: function () {

    // Mobile button (visible only on mobile) - Toggles the filter container
    $('.js-mobile-filters-toggle').click(filterBarMobile.toggleMobileFilter)

    // Select to buttons
    filterBarMobile.mainDisciplineSelectToButtons()
    filterBarMobile.costSelectToButtons()

    $('.js-filter-main-discipline--btn').click(filterBarMobile.mainDisciplineChange)
    $('.js-filter-mobile-cost-button').click(filterBarMobile.costChange)

    // When clicking the submit ("GO") button within filter container
    $('.js-filter-mobile-submit').click(function () {
      $('.js-mobile-filters-container').toggle()
    })

    // Hide filter container if clicking outside of it
    $(document).mouseup(function (e) {

      var filterButton = $('.js-mobile-filters-toggle')
      var container = $('.js-mobile-filters-container')
      // if the target of the click isn't the container nor a descendant of the container
      if (!container.is(e.target) && container.has(e.target).length === 0 && !filterButton.is(e.target)) {

        container.removeClass('show')
        $('.js-mobile-filters-container').hide()

      }

    })

  },

  toggleMobileFilter: function () {

    $('.js-mobile-filters-container').toggle()

  },

  costSelectToButtons: function () {

    var selectName = $('select.js-filter-mobile-cost').attr('name')

    var hidden = $('<input type="hidden" class="js-hidden-mobile-cost-value" name="' + selectName + '">')
    hidden.val($('select.js-filter-mobile-cost').val())
    hidden.insertAfter($('select.js-filter-mobile-cost'))

    $('select.js-filter-mobile-cost option').unwrap().each(function () {

      var btn = $('<div data-cost-value="' + $(this).val() + '" class="filter-mobile-select-button js-filter-mobile-cost-button">' + $(this).text() + '</div>')
      if ($(this).val() === $('.js-hidden-mobile-cost-value').val()) {

        btn.addClass('on')

      }

      $(this).replaceWith(btn)

    })

  },

  mainDisciplineSelectToButtons: function () {

    // Main discipline: Turning <SELECT> into <BUTTONS>
    var selectName = $('select.filter-main-discipline--select').attr('name')

    // add a hidden element with the same name as the select
    var hidden = $('<input type="hidden" class="js-hidden-main-discipline-value" name="' + selectName + '">')
    hidden.val($('select.filter-main-discipline--select').val())
    hidden.insertAfter($('select.filter-main-discipline--select'))

    $('select.filter-main-discipline--select option').unwrap().each(function () {

      var btn = $('<div data-main-discipline-value="' + $(this).val() + '" class="filter-mobile-select-button js-filter-main-discipline--btn">' + $(this).text() + '</div>')
      if ($(this).val() === $('.js-hidden-main-discipline-value').val()) {

        btn.addClass('on')

      }

      $(this).replaceWith(btn)

    })

  },

  costChange: function () {
    $('.js-filter-mobile-cost-button').removeClass('on')
    $(this).addClass('on')
    $('input.js-hidden-mobile-cost-value').val($(this).attr('data-cost-value').toLowerCase())
  },

  mainDisciplineChange: function () {
    $('.js-filter-main-discipline--btn').removeClass('on')
    $(this).addClass('on')
    $('input.js-hidden-main-discipline-value').val($(this).attr('data-main-discipline-value').toLowerCase())
  }

}
$(document).ready(filterBarMobile.onReady)

// For filter buttons that shows on desktop
var filterBarDesktop = {

  onReady: function () {

    // Stoppoing parent from being "clicked" and executing .click() stuff when clicking child
    $('.dropdown-content').click(function (event) {

      event.stopPropagation()

    })

    // When the user clicks on a filter button (cost/accomodation/..),
    // toggle between hiding and showing the dropdown content
    // + hide all other dropdowns
    $('.js-filter-button-dropdown').click(function () {

      $('.dropdown-content').not($(this).children('.dropdown-content')).removeClass('show')
      $('.js-filter-button-dropdown').not($(this)).removeClass('active')
      $(this).children('.dropdown-content').toggleClass('show')

      if (!$('.destinations-list-container').hasClass('opacity')) {

        $('.destinations-list-container').addClass('opacity')

      }

      if ($(this).hasClass('active')) {

        $('.destinations-list-container').removeClass('opacity')

      }

      $(this).toggleClass('active')

    })

    $('.js-filter-desktop-submit').click(function () {
      $('.destinations-list-container').removeClass('opacity')
      $(this).parents('.js-filter-button-dropdown').removeClass('active')
      $(this).parent('div.dropdown-content').removeClass('show')
    })

    // Hide filter dropdowns when clicking outside the dropdown window
    window.onclick = function (event) {

      if (!event.target.matches('.js-filter-button-dropdown, .dropdown-content, .js-menu-dashboard-link')) {

        $('.destinations-list-container').removeClass('opacity')
        $('.js-filter-button-dropdown').removeClass('active')

        var dropdowns = document.getElementsByClassName('dropdown-content')
        var i
        for (i = 0; i < dropdowns.length; i++) {

          var openDropdown = dropdowns[i]
          if (openDropdown.classList.contains('show')) {

            openDropdown.classList.remove('show')

          }

        }

      }

    }

  }

}
$(document).ready(filterBarDesktop.onReady)

// For loading destinations when filters are changed
var filterLoad = {

  // When clicking GO or changing something that loads destinations
  onReady: function () {

    // ---- DESKTOP
    // When changing "sort by" - load destinations
    $('select.js-desktop-sort-by').change(function () {
      filterLoad.loadDestinations('desktop')
    })

    // When changing "Asc/Desc" - swich arrow and load destinations
    $('.js-desktop-sortby-asc-desc').click(function () {
      filterLoad.changeAscDesc(event)
      filterLoad.loadDestinations('desktop')
    })

    // When changing  cost (<200e etc.)
    $('select.js-filter-desktop-cost').change(function () {
      filterLoad.loadDestinations('desktop')
    })

    // Submitting a desktop submit button
    $('.js-filter-desktop-submit').on('click', function () {
      filterLoad.loadDestinations('desktop')
    })

    // ---- MOBILE

    // When changing "sort by" - load destinations
    $('select.js-mobile-sort-by').change(function () {
      filterLoad.loadDestinations('mobile')
    })

    // When changing "Asc/Desc" - swich arrow and load destinations
    $('.js-mobile-sortby-asc-desc').click(function () {
      filterLoad.changeAscDesc(event)
      filterLoad.loadDestinations('mobile')
    })

    // Submitting GO button in mobile filter container
    $('.js-filter-mobile-submit').on('click', function () {
      filterLoad.loadDestinations('mobile')
    })

  },

  changeAscDesc: function (event) {

    var e = $(event.target)

    e.toggleClass('js-asc')
    e.toggleClass('js-desc')
    if (e.html() === '\u2191') {

      e.text('\u2193')

    } else if (e.html() === '\u2193') {

      e.text('\u2191')

    }

  },

  get desktopDataFromFilter () {

    var desktopJsonData = {}

    // Order
    if ($('.js-desktop-sortby-asc-desc').is('.js-asc')) {
      var dataOrder = 'ASC'
    } else {
      dataOrder = 'DESC'
    }

    desktopJsonData.order = dataOrder

    // Sort By (SELECT)
    var dataSortBy = $('select.js-desktop-sort-by').val()
    desktopJsonData.sort_by = dataSortBy

    // Cost (SELECT)
    var dataCost = $('select.js-filter-desktop-cost').val()
    if (dataCost !== 'any') {
      desktopJsonData.cost = dataCost
    }

    // Accomodation (CHECKBOXES)
    var dataAccomodation = []
    $('input.js-filter-desktop-accomodation-checkbox').each(function () {
      if ($(this).is(':checked')) {
        dataAccomodation.push($(this).val())
      }
    })
    if (dataAccomodation.length > 0) {
      desktopJsonData.accomodation = dataAccomodation
    }

    // Discipline (SELECT AND CHECKBOXES)
    var dataMainDiscipline = $('select.js-filter-desktop-main-discipline').val()
    if (dataMainDiscipline !== 'any') {
      desktopJsonData.main_discipline = dataMainDiscipline
    }

    var dataSecondaryDiscipline = []

    $('input.js-filter-desktop-second-discipline-checkbox').each(function () {
      if ($(this).is(':checked')) {
        dataSecondaryDiscipline.push($(this).val())
      }
    })
    if (dataSecondaryDiscipline.length > 0) {
      desktopJsonData.secondary_discipline = dataSecondaryDiscipline
    }

    // Months (CHECKBOXES)
    var dataMonths = []

    $('input.js-filter-desktop-months-checkbox').each(function () {
      if ($(this).is(':checked')) {
        dataMonths.push($(this).val())
      }
    })
    if (dataMonths.length > 0) {
      desktopJsonData.months = dataMonths
    }

    // Car (CHECKBOXES)
    var dataCar = []

    $('input.js-filter-desktop-car-checkbox').each(function () {
      if ($(this).is(':checked')) {
        dataCar.push($(this).val())
      }
    })
    if (dataCar.length > 0) {
      desktopJsonData.car = dataCar
    }

    // ALL DATA TOGETHER
    /*
    desktopJsonData = {
      order: dataOrder,
      sort_by: dataSortBy,
      cost: dataCost,
      accomodation: dataAccomodation,
      main_discipline: dataMainDiscipline,
      secondary_discipline: dataSecondaryDiscipline,
      months: dataMonths,
      car: dataCar
    } */

    return desktopJsonData

  },

  get mobileDataFromFilter () {

    var mobileJsonData = {}

    // Order
    if ($('.js-mobile-sortby-asc-desc').is('.js-asc')) {
      var dataOrder = 'ASC'
    } else {
      dataOrder = 'DESC'
    }
    mobileJsonData.order = dataOrder

    // Sort By (SELECT)
    var dataSortBy = $('select.js-mobile-sort-by').val()
    mobileJsonData.sort_by = dataSortBy

    // Cost (BUTTONS)
    var dataCost = $('input.js-hidden-mobile-cost-value').val()
    if (dataCost !== 'any') {
      mobileJsonData.cost = dataCost
    }

    // Accomodation (CHECKBOXES)
    var dataAccomodation = []
    $('input.js-filter-mobile-accomodation-checkbox').each(function () {
      if ($(this).is(':checked')) {
        dataAccomodation.push($(this).val())
      }
    })
    if (dataAccomodation.length > 0) {
      mobileJsonData.accomodation = dataAccomodation
    }

    // Discipline (BUTTONS and CHECKBOXES)
    var dataMainDiscipline = $('input.js-hidden-main-discipline-value').val()
    if (dataMainDiscipline !== 'any') {
      mobileJsonData.main_discipline = dataMainDiscipline
    }

    var dataSecondaryDiscipline = []

    $('input.js-filter-mobile-second-discipline-checkbox').each(function () {
      if ($(this).is(':checked')) {
        dataSecondaryDiscipline.push($(this).val())
      }
    })
    if (dataSecondaryDiscipline.length > 0) {
      mobileJsonData.secondary_discipline = dataSecondaryDiscipline
    }

    // Months (CHECKBOXES)
    var dataMonths = []

    $('input.js-filter-mobile-months-checkbox').each(function () {
      if ($(this).is(':checked')) {
        dataMonths.push($(this).val())
      }
    })
    if (dataMonths.length > 0) {
      mobileJsonData.months = dataMonths
    }

    // Car (CHECKBOXES)
    var dataCar = []

    $('input.js-filter-mobile-car-checkbox').each(function () {
      if ($(this).is(':checked')) {
        dataCar.push($(this).val())
      }
    })
    if (dataCar.length > 0) {
      mobileJsonData.car = dataCar
    }

    return mobileJsonData

  },

  // Change URL with history API
  changeUrl: function (jsonData) {
    var url = '?' + $.param(jsonData)
    history.pushState(null, null, url)
  },

  // AJAX CALL WITH .load(URL,data,callback)
  loadDestinations: function (from) {

    if (from === 'desktop') {
      var jsonData = filterLoad.desktopDataFromFilter
    } else if (from === 'mobile') {
      jsonData = filterLoad.mobileDataFromFilter
    }
    // console.log('bottom in loadDestinations') // eslint-disable-line no-console
    // console.log(jsonData) // eslint-disable-line no-console
    // Change url
    filterLoad.changeUrl(jsonData)

    var jsonDataAsString = JSON.stringify(jsonData)
    // console.log(jsonDataAsString)
    // Ajax load (sends request to route('/_load_destinations'))
    $('.destinations-list-container ul').load($SCRIPT_ROOT + '/_load_destinations', { jsonDataAsString: jsonDataAsString }, function () {
      // On success
      currency.fromCookie() // correcting currency after getting in new destinations
    })
  }

}

$(document).ready(filterLoad.onReady)
