(function($){
$.fn.blogfeed = function(options) {
    var defaults = {
        postcount: 5
    };
    var options = $.extend(defaults, options);
    
    return this.each(function() {
        var $obj = $(this);
        $.getFeed({url: options.feedurl, success: function(feed) {
            var k = 0;
            var out = '';
            $.each(feed.items, function(i, item) {
                if(++k > options.postcount) { return; }
                var time = new Date(Date.parse(item.updated));
                var timestamp = ''
                    +time.getDate()+'.'
                    +(time.getMonth()+1)+'.'
                    +time.getFullYear()+' '
                    +(time.getHours() < 10 ? '0'+time.getHours() : time.getHours())+':'
                    +(time.getMinutes() < 10 ? '0'+time.getMinutes() : time.getMinutes());
                out += '<h3>'+item.title+'</h3>';
                out += '<div class="blogtext">'+item.description+'</div>';
                out += '<span class="blogtime">Posted on '+timestamp+'</span>';
            });
            $obj.html(out);
			fixBlogImageContainer();
        }});
    });
};

function fixBlogImageContainer()
{
	$('.tr-caption-container').each(function(){
		var width = $( this ).find('img').width();
		$( this ).width( width );
	});
}

})(jQuery);
