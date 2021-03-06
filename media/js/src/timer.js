let time = $('meta[name="time"]').attr('content');

function strLength(num) {
    return num.toString().length;
}

let minutes = Math.floor(time / 60);
let seconds = Math.floor(time - minutes * 60);
if (strLength(time) > 2) {
    $('#quiz-timer').html(
        `<b>0${minutes}:${seconds}</b> remaining to complete quiz.`);

} else {
    $('#quiz-timer').html(
        `<b>${minutes}:${seconds}</b> remaining to complete quiz.`);
}

const activateTimer = (time) => {
    let minutes = Math.floor(time / 60);
    let seconds = Math.floor(time - minutes * 60);
    let display_secs;
    let display_minutes;
    if (time <= 0) {
        $('#quiz-timer').html('<b>Time is up!</b>');
        document.getElementById('quiz_form').submit();
        return;
    }
    setInterval(() => {
        seconds --;
        if (seconds < 0) {
            seconds = 59;
            minutes --;
        }
        if (strLength(minutes) < 2) {
            display_minutes = '0' + minutes;
        } else {
            display_minutes = minutes;
        }
        if (strLength(seconds) < 2) {
            display_secs = '0' + seconds;
        } else {
            display_secs = seconds;
        }
        if (minutes === 0 && seconds === 0) {
            $('#quiz-timer').html('<b>Time is up!</b>');
            document.getElementById('quiz_form').submit();
            return;
        }
        $('#quiz-timer')
            .html(`<b>${display_minutes}:${display_secs}</b>` +
                 ' remaining to complete quiz.');

    }, 1000);
};
window.addEventListener('load', function() {
    activateTimer(time);
});
