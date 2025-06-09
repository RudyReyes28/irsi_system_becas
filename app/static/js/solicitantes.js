// Manejador del formulario multi-paso
document.addEventListener('DOMContentLoaded', function() {
  const steps = document.querySelectorAll('.step');
  let currentStep = 0;

  function showStep(index) {
    steps.forEach((step, i) => {
      step.classList.toggle('d-none', i !== index);
    });
  }

  document.querySelectorAll('.next-step').forEach(button => {
    button.addEventListener('click', () => {
      if (currentStep < steps.length - 1) {
        currentStep++;
        showStep(currentStep);
      }
    });
  });

  document.querySelectorAll('.prev-step').forEach(button => {
    button.addEventListener('click', () => {
      if (currentStep > 0) {
        currentStep--;
        showStep(currentStep);
      }
    });
  });

  // Inicialmente mostrar el primer step
  showStep(currentStep);
});

// Funcionalidad adicional de búsqueda en list.html si se necesita
// (por ejemplo, filtros dinámicos con fetch/AJAX)