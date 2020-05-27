$(function() {

    $('#show-form-first-link').click(function(e) {
		$("#show-form-first").delay(100).fadeIn(100);
 		$("#show-form-second").fadeOut(100);
		$('#show-form-second-link').removeClass('active');
		$(this).addClass('active');
		e.preventDefault();
	});
	$('#show-form-second-link').click(function(e) {
		$("#show-form-second").delay(100).fadeIn(100);
 		$("#show-form-first").fadeOut(100);
		$('#show-form-first-link').removeClass('active');
		$(this).addClass('active');
		e.preventDefault();
	});

});

$(function() {

	$('.show-replies-message').click(function(e) {
		$(this).addClass('hidden');
		$(this).siblings().removeClass('hidden');
		e.preventDefault();
	});

});

$(function() {
	$('input[name="rating"]').on('click', function() {
		$('input[name="rating"]').prop('checked', false); // Unchecks all rating checkboxes 
		$(this).prop('checked', true); // Checks the clicked checkbox
		$(this).parent().submit(); // Submits the form
	});
});

function checkPasswordMatch() {
    var password = $("#id_set_password").val();
    var confirmPassword = $("#id_confirm_password").val();

    if (password != confirmPassword) {
		$("#password-match").prop("hidden", true);
		$("#password-no-match").prop("hidden", false);
		$('input[value="Register Now"]').prop('disabled', true);
	}
	else {
		$("#password-match").prop("hidden", false);
		$("#password-no-match").prop("hidden", true);
		$('input[value="Register Now"]').prop('disabled', false);
	}
}

$(function () {
   $("#id_set_password, #id_confirm_password").keyup(checkPasswordMatch);
});

function TimedOut() {
	window.location.href = "/timed-out"
}

$(function() {
	if(typeof YOUTUBE_VIDEO_MARGIN == 'undefined') {
	  YOUTUBE_VIDEO_MARGIN=5;
	}
	$('iframe').each(function(index,item) {
	  if($(item).attr('src').match(/(https?:)?\/\/www\.youtube\.com/)) {
		var w=$(item).attr('width');
		var h=$(item).attr('height');
		var ar = h/w*100;
		ar=ar.toFixed(2);
		//Style iframe    
		$(item).css('position','absolute');
		$(item).css('top','0');
		$(item).css('left','0');    
		$(item).css('width','100%');
		$(item).css('height','100%');
		$(item).css('max-width',w+'px');
		$(item).css('max-height', h+'px');        
		$(item).wrap('<div style="max-width:'+w+'px;margin:0 auto; padding:'+YOUTUBE_VIDEO_MARGIN+'px;" />');
		$(item).wrap('<div style="position: relative;padding-bottom: '+ar+'%; height: 0; overflow: hidden;" />');
	  }
	});
	});
	
$('#id_subject').change(function () {
	var url = $('#uploadform').attr('data-topics-url'); //gets the url of the load-topics view
	var subjectId = $(this).val(); //gets the id of the subject selected

	$.ajax({ //
		url:url,
		data: {
			'subject':subjectId
		},
		success: function (data) { //data is the return of the load-topics view
			$('#id_topic').html(data); //replaces the contents of the topic input with the returned data
			$('#id_topic').prop('disabled', false); //remove the disabled attribute of the input
		}
	});
});
$('#id_topic').change(function () {
	var url = $('#uploadform').attr('data-concepts-url'); //gets the url of the load-concepts view
	var topicId = $(this).val(); //gets the id of the subject selected

	$.ajax({ //
		url:url,
		data: {
			'topic':topicId
		},
		success: function (data) { //data is the return of the load-concepts view
			$('#id_concept').html(data); //replaces the contents of the topic input with the returned data
			$('#id_concept').prop('disabled', false); //remove the disabled attribute of the input
		}
	});
});