document.getElementById('toggleSwitch').addEventListener('change', function() {
    if (this.checked) {
        window.location.href = '/parkingspace';
    } else {
        window.location.href = '/';
    }
});
