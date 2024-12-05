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

    function bubbles() {
        var bubbles = document.querySelectorAll('.kupla');

        function applyPosition(element) {
            var state = element._state;
            element.style.right = `${state.x}px`;
            element.style.top = `${state.y}px`;
            element.style.opacity = `${state.opacity}`;
        }

        function resetBubble(element) {
            element._state = {
                x: Math.random() * 200,
                y: Math.random() * 20 + 200,
                vx: Math.random() - 0.5,
                vy: -9 - Math.random() * 8,
                opacity: 0.8 + Math.random() * 0.2,
            };
            applyPosition(element);
        }
        function tickBubble(element, dt) {
            var state = element._state;
            state.x += state.vx * dt;
            state.y += state.vy * dt;
            
            if (state.y < -200) {
                resetBubble(element);
            } else {
                applyPosition(element);
            }
        }
        bubbles.forEach(resetBubble);

        var lastTime = 0;
        function run(time) {
            var dt = (lastTime ? time - lastTime : 0) / 1000;
            lastTime = time;
            // const time = new Date();
            bubbles.forEach(function (element) {
                tickBubble(element, dt);
            });
            requestAnimationFrame(run);
        }

        requestAnimationFrame(run);

    }
    bubbles();
});
