document.getElementById('id_username').addEventListener('blur', validateField);
document.getElementById('id_email').addEventListener('blur', validateField);
document.getElementById('id_password1').addEventListener('blur', validateField);
document.getElementById('id_password2').addEventListener('blur', validateField);

function validateField(event) {
    const fieldName = event.target.name;
    const value = event.target.value;
    fetch('/rent_app/validate_field/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
        },
        body: JSON.stringify({ fieldName: fieldName, value: value }),
    })
    .then(response => response.json())
    .then(data => {
        const errorSpan = document.getElementById(fieldName + '_error');
        if (data.is_valid) {
            errorSpan.textContent = '';
        } else {
            errorSpan.textContent = data.error;
        }
    });
}
