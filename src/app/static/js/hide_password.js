function password_view() {
    var selectedValue = document.getElementById('role').value;
    var PassText = document.getElementById('hashed_password');
    var PassLabel = document.querySelector('label[for="hashed_password"]')
    if (selectedValue === 'USER') {
        PassText.style.display = 'none';
        PassLabel.style.display = 'none';
        
    } else {
        PassText.style.display = 'block';
        PassLabel.style.display = 'block';
    }
}
document.addEventListener('DOMContentLoaded', password_view);
document.getElementById('role').addEventListener('change', password_view);
