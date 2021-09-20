jQuery(function($){
  /*
  Segment is for calendar.
  */
  function EventTypeChoice() {
    var choice_switch=false;
    var event_type=($("#calendar_event input:checked").val());

    if ($('#month_choice').hasClass('month_show')) {
      choice_switch=true
    };

    if (event_type == "Month") {
      $('#month_choice').toggleClass('month_show month_hide');
      $('#non-month_choice').toggleClass('month_hide month_show');
    }else if (choice_switch) {
      $('#non-month_choice').toggleClass('month_show month_hide');
      $('#month_choice').toggleClass('month_hide month_show');
    };
    $(".form_segment p .time_period_name").text(event_type.toLowerCase());
  }

  $("#repeat_count").on("input", function(){
    // console.log($(".form_segment p .time_period_name").val());
    if ($("#repeat_count").val()>1) {
      // console.log($(".form_segment p .time_period_name").val());
      $(".form_segment p .s_for_grammer").text("s");
      // console.log($(".form_segment p .time_period_name").val());
    } else {
      $(".form_segment p .s_for_grammer").text("")
    }
  });

  $("#calendar_event input:radio").change(function() {
    EventTypeChoice()
  });

  $("#reminer_time").on("input", function(){
    // console.log($("#reminer_time").val());
    if ($("#reminer_time").val() > 1) {
      $("#reminder_time_select").children("option[value='day']").text("days");
      $("#reminder_time_select").children("option[value='week']").text("weeks");
      $("#reminder_time_select").children("option[value='month']").text("months");
    } else {
      $("#reminder_time_select").children("option[value='day']").text("day");
      $("#reminder_time_select").children("option[value='week']").text("week");
      $("#reminder_time_select").children("option[value='month']").text("month");
    };
  });

  $("#mousedownSelect").mousedown(function(e){
    if ($(window).width() > 780) {

      e.preventDefault();

      var select = this;
      var scroll = select.scrollTop;

      e.target.selected = !e.target.selected;

      setTimeout(function(){select.scrollTop = scroll;}, 0);

      $(select).focus();
    }
  }).mousemove(function(e){e.preventDefault()});

  function toggleDivVisability(DivIDToHide,BooleanCheck) {
    DivIDToHide.toggle(BooleanCheck);
  }

  $("#create_Reminder").change(function(){
    toggleDivVisability($("#reminder_info"),$("#create_Reminder").is(":checked"))
    // $("#reminder_info").toggle($("#create_Reminder").is(":checked"));
  });
  /*
  This is to reset correct values when the page is refreshed
  and has none-default values.
  */

  EventTypeChoice()
  toggleDivVisability($("#reminder_info"),$("#create_Reminder").is(":checked"))
});
