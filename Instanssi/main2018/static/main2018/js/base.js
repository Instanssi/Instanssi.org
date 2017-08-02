/* global $ */

$(function () {
    'use strict';

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

    function cubes() {
        var $container = $('.header-bg-cubes');
        // var IMAGE_BASE_PATH = '/static/main2018/images/';

        var cubeData = [
            { class: 'cube-2017 cube-2017-0', x: '200px', y: '15px', s: '192px' },
            // omnomnom
            { class: 'cube-2017 cube-2017-1', x: '570px', y: '220px', s: '96px' },
            { class: 'cube-2017 cube-2017-2', x: '770px', y: '50px', s: '128px' },
        ];

        cubeData.forEach(function(cd) {
            // var src = IMAGE_BASE_PATH + cd.src;
            var $cube = $('<div class="' + cd.class + '"/>');
            $cube.css('left', cd.x);
            $cube.css('top', cd.y);
            $cube.css('width', cd.s);
            $cube.css('height', cd.s);
            $container.append($cube);
        });
    }

    layoutButton();
    snek();
    cubes();
});