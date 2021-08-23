/* global requirejs: true */

requirejs.config({
    baseUrl: quizcon.staticUrl + 'js/',
    paths: {
        'dragondrop': 'lib/dragondrop/dragon-drop.min',
    }
});

define(['dragondrop'], function(DragonDrop) {
    const el = document.getElementById('dragondrop-container');

    const token = $('meta[name="csrf-token"]').attr('content');
    let q_order = {ids: []};
    let url = $('meta[name="reorder-url"]').attr('content');

    function post_order() {
        console.log('reorder func');
        $('#dragondrop-container li').each(function(index, element) {
            var id = $(element).attr('data-id');
            q_order.ids.push(id);
        });
        $.ajax({
            type: 'POST',
            url: url,
            data: JSON.stringify(q_order),
            contentType: 'application/json; charset=utf-8',
            dataType: 'json',
            beforeSend: function(xhr) {
                xhr.setRequestHeader('X-CSRFToken', token);
            }
        });
    }
    const dragonDrop = new DragonDrop(el, {
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

    dragonDrop
        .on('reorder', post_order)
        .on('dropped', post_order);
});
