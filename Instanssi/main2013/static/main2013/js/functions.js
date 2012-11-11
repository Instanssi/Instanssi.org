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
});
