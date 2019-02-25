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

        // minimum delay between animations
        var DELAY = 2500;
        // track whether the user is interacting with the page or not
        var interacting = false;

        function update() {
            if(!interacting) {
                return;
            }
            interacting = false;
            // Using the clock for this keeps the look consistent when navigating.
            var x = new Date().valueOf() / 2000;
            bgElements.forEach(function(bgElement, index) {
                bgElement.css('opacity', 0.5 + 0.5 * Math.sin((x + index) * Math.PI / 4));
            });
        }

        function onInteraction() {
            interacting = true;
        }

        document.addEventListener('mouseover', onInteraction);
        document.addEventListener('mousedown', onInteraction);
        document.addEventListener('keydown', onInteraction);

        // Start the 2 s animation every 2+ s.
        // The transitions sometimes glitch on Firefox if the opacity
        // target value changes mid-transition.
        // The gap isn't too noticeable, especially with ease-in-out.
        setInterval(update, DELAY);
        update();
    }
    backgrounds();
});