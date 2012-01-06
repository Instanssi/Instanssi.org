var _z = 0;
var _x = 0;
var _y = 0;
	
$(document).ready( function(){
	/*centerContent();*/
	/*setFooterPosition();*/
	updateLayerItems();
	socialMediaButtons();
	titleHover("#hearder h1");
	siteMapHover();
	navigationButtonEffect();
	ordetTicketButtonEffect();
	fixBlogImageContainer();
	
	$(window).resize(function() {/*centerContent();*/});
	
	$(document).mousemove(function(e){
		_x = e.pageX; _y = e.pageY;
		updateLayerItems();	
	
	
   });
});

function updateLayerItems(){
	initLayerItems();
	
	$(".layerItem").each( function(){
		var z = parseInt($(this).attr("z")) * 1;
		var y = parseInt($(this).attr("y")) * -1;
		var x = parseInt($(this).attr("x")) * 1;

		// wut? liikutellaan layereita, kun hiiri liikkuu
		$(this).css({
			top:  y,
			left: ( ( $(window).width()  - $(this).width() ) / 2) +  x - ($(window).width() - _x*2 ) * (-1/(z*z))
		});
	});
}

function initLayerItems(){
	$(".layerItem").each(function(){
		$(this).css({
		});
	});
}
function centerContent()
{
	var halfOfHtml = (($(window).width()-960)/2);
	$("#content").css({
		"margin-left": halfOfHtml,
	});
}
//purkkaa, purkkaa - siirretään footeria alemmas, jos sisältö #contentissa kasvaa
function setFooterPosition()
{
	var tempHeight = $("#content").height();
	$(".footerItem").each(function(){
		var newY = parseInt($(this).attr("y")) - tempHeight + 800;
		$(this).attr("y", newY); 
	});
}

function socialMediaButtons()
{
	$('.social-media img').mouseenter(function(){
		$(this).stop().animate({top: "-3", opacity: 0.8}, 200);
	});
	$('.social-media img').mouseleave(function(){
		$(this).stop().animate({top: "0", opacity: 1}, 200);
	});
}

function titleHover( target ){
	$( "#header a" ).mouseenter(function(){
		$(this).stop().animate({opacity: 0.6}, 200);
	});
	$( "#header a" ).mouseleave(function(){
		$(this).stop().animate({opacity: 1}, 200);
	});
}

function siteMapHover(){
	$( ".site-map a" ).mouseenter(function(){
		$(this).stop().animate({"margin-left": "4px"}, 200);
	});
	$( ".site-map a" ).mouseleave(function(){
		$(this).stop().animate({"margin-left": "0px"}, 200);
	});
}

function setNavigationMarker( page )
{
	var navX = 0;
	switch( page ){
		case "instanssi": 	navX = 25; break; 
		case "aikataulu": 	navX = 25; break; 
		case "kompot": 		navX = 25; break; 
		case "liput": 		navX = 25; break; 
		case "info": 		navX = 25; break; 
		case "yhteystiedot":navX = 25; break; 
		case "inenglish": 	navX = 25; break; 
	}
}

function fixBlogImageContainer()
{
	var target = $('.tr-caption-container');
	$(target).ready(function(){ 
		var width = $('.tr-caption-container').width();
		//alert("width:"+width);
	});	
}


function ordetTicketButtonEffect()
{
	$('.order-ticket a').mouseenter(function(){
		$(this).stop().animate({opacity: 0.8}, 300);
	});
	$( ".order-ticket a" ).mouseleave(function(){
		$(this).stop().animate({opacity: 1}, 300);
	});
}
function navigationButtonEffect()
{
	/*$('#navigation li').mouseenter(function(){
		$(this).stop().animate({top: '-2px'}, 200);
	});
	$( "#navigation li" ).mouseleave(function(){
		$(this).stop().animate({top: '0px'}, 200);
	});*/
}