document.addEventListener('DOMContentLoaded', function () {
  var infoButton = document.getElementById('info-button');
  var infoContainer = document.getElementById('info-container');

  console.log('Script loaded!');

  infoButton.addEventListener('click', function() {
    console.log('Button clicked!');
    if (infoContainer.style.display === 'none' || !infoContainer.style.display) {
      infoContainer.style.display = 'block';
      infoContainer.innerHTML = '<p>Welcome to Rent-a-Car! Here you can find the best deals for car rentals. You can rent a car up to 1 week. </p>';
    } else {
      infoContainer.style.display = 'none';
    }
  });
});


document.addEventListener('DOMContentLoaded', function () {
    var infoButton = document.getElementById('info-button');
    var infoContainer = document.getElementById('info-container');
    var passwordInput = document.getElementById('id_password1');


    passwordInput.addEventListener('blur', function () {
        var password = passwordInput.value;

        if (password.length < 8) {
            alert('Password must be at least 8 characters long.');
        }
    });
});