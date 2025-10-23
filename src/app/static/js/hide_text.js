function node_view() {
    var selectedValue = document.getElementById('layout_type').value;
    var Text = document.getElementById('text');
    var Label = document.querySelector('label[for="text"]')
    if (selectedValue === 'gallery') {
        Text.style.display = 'none';
        Label.style.display = 'none';
        
    } else {
        Text.style.display = 'block';
        Label.style.display = 'block';
    }
}
document.addEventListener('DOMContentLoaded', node_view);
document.getElementById('layout_type').addEventListener('change', node_view);
