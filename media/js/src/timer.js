let time = $('meta[name="time"]').attr('content');

if (time.toString().length > 2) {
    $('#quiz-timer').html(`<b>0${time}:00</b> remaining to complete quiz.`);

} else {
    $('#quiz-timer').html(`<b>${time}:00</b> remaining to complete quiz.`);
}

const activateTimer = (time) => {
    let minutes = time - 1;
    let seconds = 60;
    let display_secs;
    let display_minutes;

    const timer = setInterval(() => {
        seconds --;
        if (seconds < 0) {
            seconds = 59;
            minutes --;
        }
        if (minutes.toString().length < 2) {
            display_minutes = '0' + minutes;
        } else {
            display_minutes = minutes;
        }
        if (seconds.toString().length < 2) {
            display_secs = '0' + seconds;
        } else {
            display_secs = seconds;
        }
        if (minutes === 0 && seconds === 0) {
            $('#quiz-timer').html('<b>00:00</b>');
            setTimeout(() => {
                clearInterval(timer);
                // alert('Time over');
            }, 500);
        }
        $('#quiz-timer')
            .html(`<b>${display_minutes}:${display_secs}</b>` +
                 ' remaining to complete quiz.');

    }, 1000);
};

document.getElementById('start-timer').addEventListener('click', (event) => {
    activateTimer(time);
});
