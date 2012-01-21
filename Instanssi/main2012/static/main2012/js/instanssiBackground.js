var _z = 0;
var _x = 0;
var _y = 0;
	
$(document).ready( function(){
	/*centerContent();*/
	/*setFooterPosition();*/
	if( !jQuery.browser.mobile )initLayerItems();
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
	$("#header").css("background-image", "url('')");
	$("#layerItems").append('<div class="layerItem" x="-100" y="0" z="26" ><img src="/static/main2012/images/cubes.png" alt="" /></div>'); 
	$("#layerItems").append('<div class="layerItem" x="440" y="100" z="16" ><img src="/static/main2012/images/leaves.png" alt="" /></div> '); 
	$("#layerItems").append('<div class="layerItem" x="540" y="150" z="22" ><img src="/static/main2012/images/leaves.png" alt="" /></div> '); 
	$("#layerItems").append('<div class="layerItem" x="450" y="150" z="20"><img src="/static/main2012/images/tree.png" alt="" /></div>'); 
	$("#layerItems").append('<div class="layerItem" x="0" y="-150" z="20" ><img src="/static/main2012/images/ground.png" alt="" /></div>'); 
	$("#layerItems").append('<div class="layerItem" x="0" y="-150" z="16" ><img src="/static/main2012/images/grass.png" alt="" /></div>');
	/*
	$(".layerItem").each( function(){
		var z = parseInt($(this).attr("z")) * 1;
		var y = parseInt($(this).attr("y")) * -1;
		var x = parseInt($(this).attr("x")) * 1;

		// wut? liikutellaan layereita, kun hiiri liikkuu
		$(this).css({
			top:  y,
			left: ( ( $(window).width()  - $(this).width() ) / 2) +  x - ($(window).width() - _x*2 ) * (-1/(z*z))
		});
	});*/
	_x = $(window).width() / 2;
	_y = $(window).height() / 2;
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
/**
 * jQuery.browser.mobile (http://detectmobilebrowser.com/)
 *
 * jQuery.browser.mobile will be true if the browser is a mobile device
 *
 **/
(function(a){jQuery.browser.mobile=/android.+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|symbian|treo|up\.(browser|link)|vodafone|wap|windows (ce|phone)|xda|xiino/i.test(a)||/1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|e\-|e\/|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(di|rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|xda(\-|2|g)|yas\-|your|zeto|zte\-/i.test(a.substr(0,4))})(navigator.userAgent||navigator.vendor||window.opera);
