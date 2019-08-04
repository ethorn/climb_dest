"use strict";var currency={onReady:function(){currency.fromCookie(),$("select#currency").change(currency.onSelectChange)},onSelectChange:function(){return $.getJSON($SCRIPT_ROOT+"/_convert_currency",{c:$(this).val()},function(e){$("span.money").each(function(){var t=$(this).text()*e.rate,i=Math.round(t);$(this).text(i)}),$("span.currency").html(e.new_currency)}),!1},fromCookie:function(){if(void 0!==Cookies.get("currency")&&"EUR"!==Cookies.get("currency")){var e=Cookies.get("currency"),t=Cookies.get("rate_from_euro");1!==t&&($("select#currency").val(e),$("span.money").each(function(){var e=$(this).text()*t,i=Math.round(e);$(this).text(i)}),$("span.currency").html(e))}}};$(document).ready(currency.onReady);var filterBarMobile={onReady:function(){$(".js-mobile-filters-toggle").click(filterBarMobile.toggleMobileFilter),filterBarMobile.mainDisciplineSelectToButtons(),filterBarMobile.costSelectToButtons(),$(".js-filter-main-discipline--btn").click(filterBarMobile.mainDisciplineChange),$(".js-filter-mobile-cost-button").click(filterBarMobile.costChange),$(".js-filter-mobile-submit").click(function(){$(".js-mobile-filters-container").toggle()}),$(document).mouseup(function(e){var t=$(".js-mobile-filters-toggle"),i=$(".js-mobile-filters-container");i.is(e.target)||0!==i.has(e.target).length||t.is(e.target)||(i.removeClass("show"),$(".js-mobile-filters-container").hide())})},toggleMobileFilter:function(){$(".js-mobile-filters-container").toggle()},costSelectToButtons:function(){var e=$("select.js-filter-mobile-cost").attr("name"),t=$('<input type="hidden" class="js-hidden-mobile-cost-value" name="'+e+'">');t.val($("select.js-filter-mobile-cost").val()),t.insertAfter($("select.js-filter-mobile-cost")),$("select.js-filter-mobile-cost option").unwrap().each(function(){var e=$('<div data-cost-value="'+$(this).val()+'" class="filter-mobile-select-button js-filter-mobile-cost-button">'+$(this).text()+"</div>");$(this).val()===$(".js-hidden-mobile-cost-value").val()&&e.addClass("on"),$(this).replaceWith(e)})},mainDisciplineSelectToButtons:function(){var e=$("select.filter-main-discipline--select").attr("name"),t=$('<input type="hidden" class="js-hidden-main-discipline-value" name="'+e+'">');t.val($("select.filter-main-discipline--select").val()),t.insertAfter($("select.filter-main-discipline--select")),$("select.filter-main-discipline--select option").unwrap().each(function(){var e=$('<div data-main-discipline-value="'+$(this).val()+'" class="filter-mobile-select-button js-filter-main-discipline--btn">'+$(this).text()+"</div>");$(this).val()===$(".js-hidden-main-discipline-value").val()&&e.addClass("on"),$(this).replaceWith(e)})},costChange:function(){$(".js-filter-mobile-cost-button").removeClass("on"),$(this).addClass("on"),$("input.js-hidden-mobile-cost-value").val($(this).attr("data-cost-value").toLowerCase())},mainDisciplineChange:function(){$(".js-filter-main-discipline--btn").removeClass("on"),$(this).addClass("on"),$("input.js-hidden-main-discipline-value").val($(this).attr("data-main-discipline-value").toLowerCase())}};$(document).ready(filterBarMobile.onReady);var filterBarDesktop={onReady:function(){$(".dropdown-content").click(function(e){e.stopPropagation()}),$(".js-filter-button-dropdown").click(function(){$(".dropdown-content").not($(this).children(".dropdown-content")).removeClass("show"),$(".js-filter-button-dropdown").not($(this)).removeClass("active"),$(this).children(".dropdown-content").toggleClass("show"),$(".destinations-list-container").hasClass("opacity")||$(".destinations-list-container").addClass("opacity"),$(this).hasClass("active")&&$(".destinations-list-container").removeClass("opacity"),$(this).toggleClass("active")}),$(".js-filter-desktop-submit").click(function(){$(".destinations-list-container").removeClass("opacity"),$(this).parents(".js-filter-button-dropdown").removeClass("active"),$(this).parent("div.dropdown-content").removeClass("show")}),window.onclick=function(e){if(!e.target.matches(".js-filter-button-dropdown, .dropdown-content, .js-menu-dashboard-link")){$(".destinations-list-container").removeClass("opacity"),$(".js-filter-button-dropdown").removeClass("active");var t,i=document.getElementsByClassName("dropdown-content");for(t=0;t<i.length;t++){var n=i[t];n.classList.contains("show")&&n.classList.remove("show")}}}}};$(document).ready(filterBarDesktop.onReady);var filterLoad={onReady:function(){$("select.js-desktop-sort-by").change(function(){filterLoad.loadDestinations("desktop")}),$(".js-desktop-sortby-asc-desc").click(function(){filterLoad.changeAscDesc(event),filterLoad.loadDestinations("desktop")}),$("select.js-filter-desktop-cost").change(function(){filterLoad.loadDestinations("desktop")}),$(".js-filter-desktop-submit").on("click",function(){filterLoad.loadDestinations("desktop")}),$("select.js-mobile-sort-by").change(function(){filterLoad.loadDestinations("mobile")}),$(".js-mobile-sortby-asc-desc").click(function(){filterLoad.changeAscDesc(event),filterLoad.loadDestinations("mobile")}),$(".js-filter-mobile-submit").on("click",function(){filterLoad.loadDestinations("mobile")})},changeAscDesc:function(e){var t=$(e.target);t.toggleClass("js-asc"),t.toggleClass("js-desc"),"↑"===t.html()?t.text("↓"):"↓"===t.html()&&t.text("↑")},get desktopDataFromFilter(){var e={};if($(".js-desktop-sortby-asc-desc").is(".js-asc"))var t="ASC";else t="DESC";e.order=t;var i=$("select.js-desktop-sort-by").val();e.sort_by=i;var n=$("select.js-filter-desktop-cost").val();"any"!==n&&(e.cost=n);var s=[];$("input.js-filter-desktop-accomodation-checkbox").each(function(){$(this).is(":checked")&&s.push($(this).val())}),s.length>0&&(e.accomodation=s);var o=$("select.js-filter-desktop-main-discipline").val();"any"!==o&&(e.main_discipline=o);var a=[];$("input.js-filter-desktop-second-discipline-checkbox").each(function(){$(this).is(":checked")&&a.push($(this).val())}),a.length>0&&(e.secondary_discipline=a);var l=[];$("input.js-filter-desktop-months-checkbox").each(function(){$(this).is(":checked")&&l.push($(this).val())}),l.length>0&&(e.months=l);var c=[];return $("input.js-filter-desktop-car-checkbox").each(function(){$(this).is(":checked")&&c.push($(this).val())}),c.length>0&&(e.car=c),e},get mobileDataFromFilter(){var e={};if($(".js-mobile-sortby-asc-desc").is(".js-asc"))var t="ASC";else t="DESC";e.order=t;var i=$("select.js-mobile-sort-by").val();e.sort_by=i;var n=$("input.js-hidden-mobile-cost-value").val();"any"!==n&&(e.cost=n);var s=[];$("input.js-filter-mobile-accomodation-checkbox").each(function(){$(this).is(":checked")&&s.push($(this).val())}),s.length>0&&(e.accomodation=s);var o=$("input.js-hidden-main-discipline-value").val();"any"!==o&&(e.main_discipline=o);var a=[];$("input.js-filter-mobile-second-discipline-checkbox").each(function(){$(this).is(":checked")&&a.push($(this).val())}),a.length>0&&(e.secondary_discipline=a);var l=[];$("input.js-filter-mobile-months-checkbox").each(function(){$(this).is(":checked")&&l.push($(this).val())}),l.length>0&&(e.months=l);var c=[];return $("input.js-filter-mobile-car-checkbox").each(function(){$(this).is(":checked")&&c.push($(this).val())}),c.length>0&&(e.car=c),e},changeUrl:function(e){var t="?"+$.param(e);history.pushState(null,null,t)},loadDestinations:function(e){if("desktop"===e)var t=filterLoad.desktopDataFromFilter;else"mobile"===e&&(t=filterLoad.mobileDataFromFilter);console.log("bottom in loadDestinations"),console.log(t),filterLoad.changeUrl(t);var i=JSON.stringify(t);console.log(i),$(".destinations-list-container ul").load($SCRIPT_ROOT+"/_load_destinations",{jsonDataAsString:i},function(){currency.fromCookie()})}};$(document).ready(filterLoad.onReady);var menu={onReady:function(){$(".js-menu-mobile-button").click(function(){$(".js-menu").toggle()})}};$(document).ready(menu.onReady);var destinationHover={onReady:function(){$(".destination-container").hover(function(){$(this).find(".destination-top").addClass("invisible"),$(this).find(".destination-display-on-hover").removeClass("invisible")},function(){$(this).find(".destination-top").removeClass("invisible"),$(this).find(".destination-display-on-hover").addClass("invisible")})}};$(document).ready(destinationHover.onReady);var selectIntoButtons={onReady:function(){selectIntoButtons.init(),$("select#main_discipline option").unwrap().each(function(){var e=$('<div class="main-discipline-btn">'+$(this).text()+"</div>");$(this).replaceWith(e)}),$(document).on("click",".main-discipline-btn",function(){$(".main-discipline-btn").removeClass("on"),$(this).addClass("on"),$('input[name="'+selectIntoButtons.selectName+'"]').val($(this).text().toLowerCase())})},init:function(){selectIntoButtons.selectName=$("select#main_discipline").attr("name");var e=$('<input type="hidden" name="'+selectIntoButtons.selectName+'">');e.val($("select#main_discipline").val()),e.insertAfter($("select#main_discipline"))}};if($(document).ready(selectIntoButtons.onReady),"objectFit"in document.documentElement.style==!1)for(var container=document.getElementsByClassName("js-destination-bg-polyfill"),i=0;i<container.length;i++){var imageSource=container[i].querySelector("img").src;container[i].querySelector("img").style.display="none",container[i].style.backgroundSize="cover",container[i].style.backgroundImage="url("+imageSource+")",container[i].style.backgroundPosition="center center"}
//# sourceMappingURL=app-min.js.map