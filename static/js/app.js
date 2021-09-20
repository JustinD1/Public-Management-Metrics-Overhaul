
/*
Segment is for collapsing table structures
*/
function create_selector(level) {
  return "[data-level='" + level + "']";
}

$(".rowExpand").click(function(){
  var this_level = parseInt($(this).data("level"), 10);
  var this_level_selector = create_selector(this_level);
  var next_level_selector = create_selector(this_level + 1);
  var noneToggle=false;
  // $('thead > tr > '+next_level_selector).css('color','black')
  $(this).nextUntil(this_level_selector,next_level_selector).css('display',function(i,v){
    if(this.style.display === 'table-row'){
      noneToggle=true;
      return 'none';
    }else{
      noneToggle=false;
      return 'table-row';
    }
    //return this.style.display === 'table-row'?'none':'table-row';
  });
  if(noneToggle){
    // $('thead > tr > '+next_level_selector).css('color','#fff')
    $(this).nextUntil(this_level_selector).css('display','none');
  }
});

/*
This is to handle any overlay that you can close with the top right "x"
*/
function overlayToggle(){
  el = document.getElementById("overlayToggle");
  opac = document.getElementById("underlay");
  if (el.style.visibility == "visible") {
    el.style.visibility = "hidden"
    opac.style.opacity = 1.0;
    opac.style.filter = 'alpha(opacity=1.0)';
  } else {
    el.style.visibility = "visible"
    opac.style.opacity = 0.3;
    opac.style.filter = 'alpha(opacity=0.3)';
  }
  el.style.opacity
};

/*
This is to handle the burger navigation opening and closing.
*/
function handleBurgerNav(){
  element = document.getElementById("burger-icon");
  change_element_value = document.getElementById("nav-ui-burger")
  if (change_element_value.style.visibility == "hidden") {
    change_element_value.style.visibility = "visible"
  } else {
    change_element_value.style.visibility = "hidden"
  }
};

//
// var tableOffset = $("#table-1").offset().top;
// var $header = $("#table-1 > thead").clone();
// var $fixedHeader = $("#header-fixed").append($header);
//
// $(window).bind("scroll", function() {
//     var offset = $(this).scrollTop();
//
//     if (offset >= tableOffset && $fixedHeader.is(":hidden")) {
//         $fixedHeader.show();
//     }
//     else if (offset < tableOffset) {
//         $fixedHeader.hide();
//     }
// });
