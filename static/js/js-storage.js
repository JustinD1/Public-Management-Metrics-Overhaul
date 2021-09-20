function toggleVisability(Div){
  var x = document.getElementById(Div);
  console.log(x);
  if(x.style.display==="none"){
    x.style.display="block";
  } else {
    x.style.display="none";
  };
};

function catagorySelect(aug){
  var catagory = aug;

  $('.content_container').find(".content").each(function(index){
    var element_catagory = $(this).data('catagory');
    console.log(element_catagory);

    if ((catagory=='All') || (catagory==element_catagory)) {
      $(this)[0].style.display="block";
    } else {
      $(this)[0].style.display="none";
    };
  });
};

function toggleView(){
  $('.content_container').each(function(index){
    object_container = $(this).data('view');

    // console.log('Data-view: '+object_container);
    // console.log('Selected value: '+$('#view_seletion').val());
    // console.log((object_container==$('#view_seletion').val()));

    if (object_container==$('#view_seletion').val()) {
      $(this)[0].style.display="block";
    } else {
      $(this)[0].style.display="none";
    };
  })
};

function openClose() {
  // console.log($("div.popup-overlay.active").length);
  if ($("div.popup-overlay.active").length === 0) {
    // console.log(".popup-overlay.active")
    $(".popup-overlay, .popup-content").addClass("active");
  } else {
    $(".popup-overlay, .popup-content").removeClass("active");
    // console.log(".popup-overlay")
  };
};

function confirmDelete(item){
  var item_delete = item;
  var file = $("#item-"+item_delete);
  var file_name = file.find("span:nth-child(1)").text();
  var file_disc = file.find("span:nth-child(2)").text();
  var file_date = file.find("span:nth-child(3)").text();

  // console.log(item_delete);
  // console.log(file_name, file_disc, file_date);

  $(".popup-content form p").find("span:nth-child(1)").text(file_name);
  $(".popup-content form p").find("span:nth-child(2)").text(file_date);

  $("#deleteID").attr('value',item_delete);
  openClose()


};
// $(".open").on("click", function() {
//   $(".popup-overlay, .popup-content").addClass("active");
// });
//
// //removes the "active" class to .popup and .popup-content when the "Close" button is clicked
// $(".close, .popup-overlay").on("click", function() {
//   $(".popup-overlay, .popup-content").removeClass("active");
// });
