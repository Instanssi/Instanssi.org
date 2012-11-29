$(document).ready(function (){
	
	$( 'nav .nav-btn' ).click( function(){
		$( '#page-header nav ul' ).toggleClass( 'active' );
	});
	/* mobile nav button */
	/*
	$( 'nav .nav-btn' ).click( function(){
		
		var page_header_nav_ul = $( '#page-header nav ul' );
		
		if( !page_header_nav_ul.is(':visible') ){
			$('html, body').animate({
				scrollTop: $("#page-header nav").offset().top
			}, 400);
		}
		
		page_header_nav_ul.slideToggle( 400 );
	});
	
	$(window).resize(function() {
		if( window.innerWidth  > 480 && !$( '#page-header nav ul' ).is(':visible')  ){
			$( '#page-header nav ul' ).show();
		} else {
			
		}

	});
	*/
	
	
	/* Countdown */
	countDown( new Date("March 7, 2013 18:00:00") );
	setInterval( function() { countDown( new Date("March 7, 2013 18:00:00") ); }, 1000*60 );
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
	
});
