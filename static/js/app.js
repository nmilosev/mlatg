var infofunc = function() {
  $.get( "/model", function( data ) {
    $("#usedmodel").html(data);
  });
  $.get( "/ram", function( data ) {
    $("#ramusage").html(data);
  });
  $.get( "/cpu", function( data ) {
    $("#cpuusage").html(data);
  }); 
  $.get( "/gpu", function( data ) {
    $("#gpuusage").html(data);
  });
}

setInterval(infofunc, 5000);

infofunc();

function send() {
	var text1 = $('#dropdown').val();
	console.log(text1)
	var text2 = $('#input_text2').val();
	$('#input_text2').val('');
	// alert(text);
	$(".loader").show();
	var start_time = new Date().getTime();
	$.ajax({
            url: '/ask',
            data: { "question": text1, "answer": text2 },
            type: 'POST',
            success: function(response) {
                $(".loader").hide();
                data = JSON.parse(response);
                $('#question').html(data.q);
                $('#answer').html(data.a);
                $('#grade').html(data.g);
                $('#time').html(new Date().getTime() - start_time + "ms");
                $('#messages').show();
            },
            error: function(error) {
                $(".loader").hide(); 
		console.log(error);
            }
        });	
}

$('#input_text2').on("keyup", function(event) {
  event.preventDefault();
  if (event.keyCode === 13) {
    $("#send-message").click();
  }
});

$(document).ready(function(){
  $.getJSON("/allq", function(result) {
    $('select').formSelect();
  });
});

