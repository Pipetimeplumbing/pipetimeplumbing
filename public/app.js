const bookingStatus = document.getElementById('booking-status');
function openBooking(event) {
  event.preventDefault();
  if (window.HCPWidget && typeof window.HCPWidget.openModal === 'function') {
    try {
      window.HCPWidget.openModal();
      bookingStatus.textContent = '';
      bookingStatus.className = 'status';
      return;
    } catch (error) {
      // Let the customer retry or call if the booking provider fails.
    }
  }
  bookingStatus.className = 'status error';
  bookingStatus.textContent = 'Online booking is still loading or temporarily unavailable. Please try again in a moment, or call 401-400-5521.';
  document.getElementById('book').scrollIntoView({behavior: 'smooth'});
}
// Use the provider's service selection and availability without inventing slots.
document.querySelectorAll('a[href="#book"], [data-service], [data-hcp-booking]').forEach(button => {
  button.addEventListener('click', openBooking);
});
for (const [id, endpoint] of [['message-form','messages']]) {
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
      status.textContent = `Message saved for the team. Reference: ${result.id}. For immediate help, call 401-400-5521.`;
      form.reset();
    } catch (error) {
      status.className = 'status error';
      status.textContent = `${error.message} Please try again or call 401-400-5521.`;
    } finally {button.disabled = false;}
  });
}
