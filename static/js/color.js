const form = document.querySelector('.form');
const colorPicker = document.querySelector('#hex_code');
const icon = document.querySelector('.icon');

icon.addEventListener('click', () => {
    colorPicker.click();
});