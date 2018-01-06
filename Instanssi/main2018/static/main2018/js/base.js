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
    layoutButton();

    function halos() {
        var haloElements = [];
        var $container = $('.header-bg-fx');

        var haloData = [
            { class: 'halo-2018 halo-orange', x: 815, y: 171, s: 147 },
            { class: 'halo-2018 halo-green', x: 531, y: 6, s: 218 },
            { class: 'halo-2018 halo-blue', x: 202, y: 87, s: 257 },
            { class: 'halo-2018 halo-purple', x: -8, y: -17, s: 220 },
        ];

        haloData.forEach(function(cd) {
            // var src = IMAGE_BASE_PATH + cd.src;
            var $halo = $('<div class="' + cd.class + '"/>');
            $halo.css('left', cd.x / 2);
            $halo.css('top', cd.y / 2);
            $halo.css('width', cd.s / 2);
            $halo.css('height', cd.s / 2);
            $container.append($halo);
            haloElements.push($halo);
        });

        document.addEventListener('mouseover', function() {
            haloElements.forEach(function(haloElement, index) {
                var val = Math.sin(new Date().valueOf() / 1000 + index);
                haloElement.css('opacity', val * 0.5 + 0.5);
            });
        }, 500);
    }
    halos();

    function backgrounds() {
        var bgElements = [
            '.layer-cyan',
            '.layer-green',
            '.layer-purple',
            '.layer-yellow'
        ].map(function(selector) {
            return $(selector);
        });

        function update() {
            // Using the clock for this keeps the look consistent when navigating.
            var x = new Date().valueOf() / 2000;
            bgElements.forEach(function(bgElement, index) {
                bgElement.css('opacity', 0.5 + 0.5 * Math.sin((x + index) * Math.PI / 4));
            });
        }

        // Start the 2 s animation every 2.1 s.
        // The transitions sometimes glitch on Firefox if the opacity
        // target value changes mid-transition.
        // The gap isn't too noticeable, especially with ease-in-out.
        setInterval(update, 2100);
        update();
    }
    backgrounds();
});