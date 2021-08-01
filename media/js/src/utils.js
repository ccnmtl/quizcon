
// eslint-disable-next-line no-unused-vars
function copyToClipboard(eltId) {
    var text = document.getElementById(eltId);
    text.select(); //select the text area
    document.execCommand('copy'); //copy to clipboard
}
