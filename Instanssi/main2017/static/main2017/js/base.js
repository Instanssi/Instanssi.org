$(function () {
    // layout-specific JS can go here.
    function layoutButton() {
        /* mobile nav button */
        $('#page-header .nav-btn').click(function (event) {
            event.preventDefault();
            var $nav = $('#page-header nav ul');
            $nav.toggleClass('active');
        });
    }

    function snek() {
        var $layer0 = $('.header-bg-0');
        var $layer1 = $('.header-bg-1');
        var $window = $(window);

        function moveLayers(offset) {
            var ww = $window.width();

            // center pattern by default
            var base = ww / 2;

            // mimic media query behavior in our procedural inline CSS
            // (offsets mostly found through trial and error)
            if (ww >= 1200) {
                base += 230;
            } else if (ww >= 980) {
                base += 230 + 65;
            } else {
                base += 230 + 140;
            }
            var pos = base + offset / 100;
            $layer1.css('background-position-x', pos);
            // TODO: Cubes!
        }
        $('body').mousemove(function (ev) {
            // TODO: Make this smoother! Keep track of the current and target offset, and animate it until we reach our goal.
            // (use requestframe if available?)
            moveLayers($window.width() / 2 - ev.pageX);
        });
        $window.resize(function(ev) {
            moveLayers(0);
        });
        moveLayers(0);
    }

    layoutButton();
    snek();
});