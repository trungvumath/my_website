document.addEventListener('DOMContentLoaded', function() {
    // Example: Highlight header on click
    const header = document.querySelector('.header');
    if (header) {
        header.addEventListener('click', function() {
            header.style.color = '#7fdfff';
            setTimeout(() => header.style.color = '', 700);
        });
    }
});
