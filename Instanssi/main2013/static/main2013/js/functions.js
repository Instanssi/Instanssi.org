$(document).ready(function (){
	
	/* logo effect */
	$('.logo').mouseenter(function(){
		$( this ).stop().animate( { 'opacity' : 0.9 }, 500 );
	});
	$('.logo').mouseleave(function(){
		$( this ).stop().animate( { 'opacity' : 1.0 }, 500 );
	});
	
	/* nav effect */
	$('nav li a').mouseenter(function(){
		$( this ).stop().animate( { 'opacity' : 0.9, 'top' : '-3px' }, 200 );
	});
	$('nav li a').mouseleave(function(){
		$( this ).stop().animate( { 'opacity' : 1.0, 'top' : '0px' }, 200 );
	});
	
	/* mobile nav button */
	$( 'nav .nav-btn' ).click( function(){
		$( '#page-header nav ul' ).slideToggle( 400 );
	});
	$(window).resize(function() {
		if( window.innerWidth  > 480 && !$( '#page-header nav ul' ).is(':visible')  ){
			$( '#page-header nav ul' ).show();
		} else {
			
		}

	});
	
	
	/* Nice bunch of spagetti, which adds curren-menu-item class in a right place */
	$( '.menu-item' ).each(function(){
		if( $( this ).find( 'a' ).attr('href') == window.location.pathname ) $( this ).addClass( 'current-menu-item' );
	});
	
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
