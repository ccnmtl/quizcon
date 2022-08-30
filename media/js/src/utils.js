
// eslint-disable-next-line no-unused-vars
function copyToClipboard(eltId) {
    var text = document.getElementById(eltId);
    text.select(); //select the text area
    document.execCommand('copy'); //copy to clipboard
};

var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
  return new bootstrap.Tooltip(tooltipTriggerEl)
})

jQuery("#id_show_answers_2").on("click", function() {
    jQuery("#id_show_answers_date").attr("disabled", false)
});
jQuery("#id_show_answers_1").on("click", function() {
    jQuery("#id_show_answers_date").attr("disabled", true)
});
jQuery("#id_show_answers_0").on("click", function() {
    jQuery("#id_show_answers_date").attr("disabled", true)
});
jQuery(document).ready(function() {
    if(jQuery('#id_show_answers_2').is(':checked')) {
        jQuery("#id_show_answers_date").attr("disabled", false)
    }
});
jQuery("#timerSwitch").on("click", function() {
    if(jQuery("#timerSwitch").is(":checked")){
        jQuery("#id_time").attr("disabled", false)
    } else {
        jQuery("#id_time").attr("disabled", true)
    }
});
