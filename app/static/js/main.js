document.addEventListener('DOMContentLoaded', () => {
  const markInputs = document.querySelectorAll('.marks');
  const totalField = document.getElementById('totalMarks');
  const percentField = document.getElementById('percentage');
  const streamField = document.getElementById('stream_selected');
  const eligibilityHint = document.getElementById('eligibilityHint');

  function updateMarks() {
    const values = [...markInputs].map((input) => parseFloat(input.value) || 0);
    const total = values.reduce((a, b) => a + b, 0);
    const percentage = values.length ? total / values.length : 0;
    if (totalField) totalField.value = total.toFixed(2);
    if (percentField) percentField.value = percentage.toFixed(2);
  }

  function updateHint() {
    if (!streamField || !eligibilityHint) return;
    if (streamField.value === 'Science') {
      eligibilityHint.textContent = 'Science requires 60% aggregate and minimum 60 in Maths and Science.';
    } else if (streamField.value === 'Commerce') {
      eligibilityHint.textContent = 'Commerce requires minimum 55% aggregate.';
    } else {
      eligibilityHint.textContent = 'Humanities is open to all pass students.';
    }
  }

  markInputs.forEach((input) => input.addEventListener('input', updateMarks));
  if (streamField) streamField.addEventListener('change', updateHint);
  updateMarks();
  updateHint();
});
