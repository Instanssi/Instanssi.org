$(document).ready(function (){
	
	
	/* mobile nav button */
	$( 'nav .nav-btn' ).click( function(){
		var page_header_nav_ul = $( '#page-header nav ul' );
		
		page_header_nav_ul.toggleClass( 'active' );
		
		if( page_header_nav_ul.hasClass('active') ){
			$('html, body').animate({
				scrollTop: $("#page-header nav").offset().top
			}, 400);
			console.log('ok');
		}
	});
	
	/* Countdown */
	countDown( new Date("March 1, 2013 18:00:00") );
	setInterval( function() { countDown( new Date("March 1, 2013 18:00:00") ); }, 1000*60 );
	function countDown( date ){
		var today = new Date();
		msPerDay = 24 * 60 * 60 * 1000 ;
		timeLeft = (date.getTime() - today.getTime());
		var e_daysLeft = timeLeft / msPerDay;
		daysLeft = Math.floor(e_daysLeft);
		var e_hrsLeft = (e_daysLeft - daysLeft)*24;
		hrsLeft = Math.floor(e_hrsLeft);
		var minsLeft = Math.floor((e_hrsLeft - hrsLeft)*60);

		$( '#countdown' ).html( daysLeft + " päivää, " + hrsLeft +" tuntia, " + minsLeft + " minuuttia" )
	}

	/* store +/- buttons */
	
	/* add +/- buttons */
	$( '.store-items input' ).each( function() {
		$( this ).after('<div class="inc-dec-btn" ><div>+</div><div>-</div></div>');
	});

	/* increase and decrease buttton logic  */ 
	$(".store-items .inc-dec-btn div").click(function() {
	    var $button = $( this );
	    var input = $button.parent().parent().find( "input" );
	    var oldValue = input.val();
	    var newVal = oldValue;
	
	    if( input.is(':disabled') ){	
	    	return;
	    }

	    if ( $button.text() == "+" ) {
		 	var newVal = parseFloat( oldValue ) + 1;
		} else {
		  	// Don't allow decrementing below zero
		  	if ( oldValue >= 1 ) {
		     	var newVal = parseFloat( oldValue ) - 1;
		  	}
		}
		input.val( newVal );
		filterNewStoreAmount( input );
		storeSum();
	});
	
	$( ".store-items input" ).change(function() { 
		filterNewStoreAmount( $( this ) );
		storeSum(); 
	});


	function filterNewStoreAmount( input ){
		if( isNaN( parseFloat( input.val() ) ) ){
			// if new value is not a number, force it to be 0
			input.val( 0 );
		}
		else if( parseInt( input.val() ) > input.attr('data-maxvalue') ){
			input.val( input.attr('data-maxvalue') );
		}
		else if( parseInt( input.val() ) < 0 ){
			input.val( 0 );
		}
		
		input.val( parseInt( input.val(), 10 ) );
	}


	/* count money sum of store items  */
	function storeSum(){
		var storeSum = 0;
		$( ".store-items input" ).each( function() {
			// amount * price
			storeSum += parseFloat( $( this ).val() ) * parseFloat( $( this ).parent().parent().find('.item-price').html() );
		});
		$( '.store-sum span' ).html( storeSum.toFixed(2) );
	}
	$('.store-items').append('<div class="store-sum">Yhteensä: <span></span> €</div>');
	storeSum();


	/* fancybox for images */
	$('.item-image').wrap( function(){
		return '<a href="' + $( this ).attr( 'data-bigimg' ) + '" class="fancybox">';
	});
	$(".fancybox").fancybox();

});
