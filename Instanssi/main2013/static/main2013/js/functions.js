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
