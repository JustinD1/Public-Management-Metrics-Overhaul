// jQuery(function($){
function queryDates(value){
  var test_value = value;
  console.log("Function started ajax request starting");
  $.ajax({
    type:"GET",
    url:"queryDates",
    data:{
      information: test_value
    },
    success: function( data )
    {
      console.log("ajex request success");

      console.log(jQuery.type(data));
      on()
      $( '#fill-text' ).html(
          data
      )
    },
    error: function( jqXHR, data, data2 )
    {
      console.log(jqXHR);
      // console.log(data);
      // console.log(data2);
      console.log("ajex request failed");
      console.log(jQuery.type(jqXHR));
      on()
      $( '#fill-text' ).html(jqXHR.responseText)
    }
  });
}

function on() {
  document.getElementById("overlay").style.display = "block";
}

function off() {
  document.getElementById("overlay").style.display = "none";
}
// };
