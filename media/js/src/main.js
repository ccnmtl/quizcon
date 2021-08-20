/* global requirejs: true */

requirejs.config({
    baseUrl: quizcon.staticUrl + 'js/',
    paths: {
        'dragondrop': 'lib/dragondrop/dragon-drop.min',
    }
});

define(['dragondrop'], function(DragonDrop) {
    const demo1 = document.getElementById('dragondrop-container');
    const dragonDrop = new DragonDrop(demo1, {
        handle: '.handle',
        announcement: {
            grabbed: el => `${el.querySelector('span').innerText} grabbed`,
            dropped: el => `${el.querySelector('span').innerText} dropped`,
            reorder: (el, items) => {
                const pos = items.indexOf(el) + 1;
                const text = el.querySelector('span').innerText;
                return `The questions have been reordered, ${text} is now ` +
                    `in position #${pos} out of ${items.length}`;
            },
            cancel: 'Reordering cancelled.'
        }
    });

    dragonDrop.on('reorder', function() {
        // @todo - post the new order to the server
    });
});
