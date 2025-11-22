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
        function applyState(element) {
            var state = element._state;
            var baseScale = Math.min(0.5, state.t);
            var scaleX = baseScale + Math.sin(state.phase + state.t * 2.0) * 0.05;
            var scaleY = baseScale + Math.cos(state.phase + state.t * 2.0) * 0.05;
            element.style.right = `${state.x}px`;
            element.style.top = `${state.y}px`;
            element.style.opacity = `${state.opacity * Math.min(1.0, state.t)}`;
            element.style.transform = `scale(${scaleX}, ${scaleY})`;
        }

        function resetState(element) {
            element._state = {
                x: Math.random() * 200,
                y: Math.random() * 50 + 250,
                vx: (Math.random() - 0.5) * 30,
                vy: -9 - Math.random() * 8,
                opacity: 0.8 + Math.random() * 0.2,
                t: 0,
                phase: Math.random() * 10,
            };
            applyState(element);
        }
        function tickBubble(element, dt) {
            var state = element._state;
            state.x += state.vx * dt;
            state.y += state.vy * dt;

            state.vx += -state.vx * 0.01 * dt;

            state.vy += (-5) * dt;
            state.vy += -state.vy * 0.01 * dt;

            state.t += dt;
            
            if (state.y < -200) {
                resetState(element);
            } else {
                applyState(element);
            }
        }
        
        var lastTime = 0;
        function run(time) {
            var dt = (lastTime ? time - lastTime : 0) / 1000;
            lastTime = time;
            bubbles.forEach(function (element) {
                tickBubble(element, dt);
            });
            requestAnimationFrame(run);
        }

        var bubbleTypes = [
            { className: "kupla kupla1", src: "/static/main2026/images/web-kupla1.png" },
            { className: "kupla kupla2", src: "/static/main2026/images/web-kupla2.png" },
        ];
        var bg = document.querySelector('.header-background');
        var bubbles = [];
        function addBubbles(count) {
            for (var i = 0; i < count; i++) {
                var bubbleType = bubbleTypes[i % bubbleTypes.length];
                var bubble = document.createElement('img');
                Object.assign(bubble, bubbleType);
                bg.appendChild(bubble);
                resetState(bubble);
                tickBubble(bubble, Math.random() * 20 * Math.random());
                bubbles.push(bubble);
            }
        }
        addBubbles(5);
        requestAnimationFrame(run);
    }
    bubbles();
});
