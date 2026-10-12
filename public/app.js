const dateInput = document.querySelector('input[type=date]');
const today = new Date();
dateInput.min = `${today.getFullYear()}-${String(today.getMonth()+1).padStart(2,'0')}-${String(today.getDate()).padStart(2,'0')}`;
document.querySelectorAll('[data-service]').forEach(button => button.addEventListener('click', () => {
  document.querySelector('select[name=service]').value = button.dataset.service;
  document.querySelector('#book').scrollIntoView({behavior:'smooth'});
}));
for (const [id, endpoint] of [['booking-form','appointments'],['message-form','messages']]) {
  const form = document.getElementById(id);
  form.addEventListener('submit', async event => {
    event.preventDefault();
    const status = form.querySelector('.status');
    const button = form.querySelector('button');
    button.disabled = true;
    status.className = 'status';
    status.textContent = 'Sending your request…';
    try {
      const response = await fetch(`/api/${endpoint}`, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(Object.fromEntries(new FormData(form)))});
      const result = await response.json();
      if (!response.ok) throw new Error(result.error || 'Unable to send your request.');
      status.className = 'status success';
      status.textContent = endpoint === 'appointments' ? `Appointment request saved. Your time is not yet confirmed. Reference: ${result.id}.` : `Message saved for the team. Reference: ${result.id}. For immediate help, call 401-400-5521.`;
      form.reset();
    } catch (error) {
      status.className = 'status error';
      status.textContent = `${error.message} Please try again or call 401-400-5521.`;
    } finally {button.disabled = false;}
  });
}
