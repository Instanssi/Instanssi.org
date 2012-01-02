var _z = 0;
var _x = 0;
var _y = 0;
	
$(document).ready( function(){
	centerContent();
	setFooterPosition();
	updateLayerItems();
	$(window).resize(function() {centerContent();});
	
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