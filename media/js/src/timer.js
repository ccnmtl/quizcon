let time = $('meta[name="time"]').attr('content');
let submitted = $('meta[name="submitted"]').attr('content');

function strLength(num) {
    return num.toString().length;
}

let minutes = Math.floor(time / 60);
let seconds = Math.floor(time - minutes * 60);
let display_secs;
let display_minutes;
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
$('#quiz-timer')
    .html(`<strong>${display_minutes}:${display_secs}</strong>` +
         ' remaining to complete quiz.');


const activateTimer = (time) => {
    let minutes = Math.floor(time / 60);
    let seconds = Math.floor(time - minutes * 60);
    let display_secs;
    let display_minutes;
    if (time <= 0) {
        $('#quiz-timer').html('<strong>Time is up!</strong>');
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
            $('#quiz-timer').html('<strong>Time is up!</strong>');
            document.getElementById('quiz_form').submit();
            return;
        }
        $('#quiz-timer')
            .html(`<strong>${display_minutes}:${display_secs}</strong>` +
                 ' remaining to complete quiz.');

    }, 1000);
};
window.addEventListener('load', function() {
    if (time && submitted === 'False') {
        activateTimer(time);
    }
});
