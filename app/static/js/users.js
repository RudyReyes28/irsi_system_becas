// static/js/users.js

document.addEventListener('DOMContentLoaded', function () {
  // Confirmar eliminación
  document.querySelectorAll('.delete-btn').forEach(button => {
    button.addEventListener('click', function () {
      const userId = this.dataset.id;
      if (confirm('¿Estás seguro de eliminar este usuario?')) {
        fetch(`/users/${userId}/delete`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('input[name="csrf_token"]').value
          }
        }).then(res => {
          if (res.redirected) {
            window.location.href = res.url;
          }
        });
      }
    });
  });

  // Toggle activo/inactivo vía AJAX
  document.querySelectorAll('.active-toggle').forEach(toggle => {
    toggle.addEventListener('change', function () {
      const userId = this.dataset.id;
      fetch(`/users/${userId}/toggle_active`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': document.querySelector('input[name="csrf_token"]').value
        }
      })
      .then(response => response.json())
      .then(data => {
        if (!data.success) {
          alert('Error al actualizar estado.');
        }
      });
    });
  });
});