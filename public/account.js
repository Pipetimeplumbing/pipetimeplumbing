const authPanel = document.getElementById('auth-panel');
const clientPanel = document.getElementById('client-panel');
const form = document.getElementById('auth-form');
let mode = 'login';
function setMode(next) {
  mode = next;
  const register = mode === 'register';
  document.getElementById('name-field').hidden = !register;
  form.elements.name.required = register;
  form.elements.password.autocomplete = register ? 'new-password' : 'current-password';
  document.getElementById('auth-submit').textContent = register ? 'Create account ↗' : 'Sign in ↗';
  document.getElementById('login-tab').setAttribute('aria-pressed', String(!register));
  document.getElementById('register-tab').setAttribute('aria-pressed', String(register));
  document.getElementById('auth-status').textContent = '';
}
document.getElementById('login-tab').onclick = () => setMode('login');
document.getElementById('register-tab').onclick = () => setMode('register');
async function loadAccount() {
  const response = await fetch('/api/account', {cache:'no-store'});
  if (response.status === 401) {authPanel.hidden=false;clientPanel.hidden=true;return;}
  if (!response.ok) throw new Error('Unable to load your account. Please try again.');
  const data = await response.json();
  authPanel.hidden=true;clientPanel.hidden=false;
  document.getElementById('welcome').textContent = `Hello, ${data.client.name}.`;
  const history = document.getElementById('history');
  history.replaceChildren();
  const messages = data.requests.filter(item => item.kind === 'messages');
  if (!messages.length) history.textContent = 'No messages yet. Send your first message from the home page.';
  for (const item of messages) {
    const article = document.createElement('article');article.className='history-item';
    const label = document.createElement('small');label.textContent=`${item.created_at} UTC · Reference ${item.id}`;
    const body = document.createElement('p');body.textContent=item.details.message;
    article.append(label,body);history.append(article);
  }
}
form.addEventListener('submit', async event => {
  event.preventDefault();
  const button=document.getElementById('auth-submit'), status=document.getElementById('auth-status');
  button.disabled=true;status.textContent='Please wait…';
  try {
    const response=await fetch(`/api/auth/${mode}`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(Object.fromEntries(new FormData(form)))});
    const data=await response.json();
    if (!response.ok) throw new Error(data.error || 'Unable to sign in.');
    form.reset();await loadAccount();status.textContent='';
  } catch(error) {status.className='status error';status.textContent=error.message;}
  finally {button.disabled=false;}
});
document.getElementById('logout').onclick=async () => {
  const button=document.getElementById('logout');button.disabled=true;
  try {
    const response=await fetch('/api/auth/logout',{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'});
    if (!response.ok) throw new Error('Unable to sign out. Please try again.');
    await loadAccount();
  } catch(error) {document.getElementById('account-status').textContent=error.message;}
  finally {button.disabled=false;}
};
loadAccount().catch(error => {document.getElementById('auth-status').textContent=error.message;});

const deleteForm = document.getElementById('delete-account-form');
deleteForm.addEventListener('submit', async event => {
  event.preventDefault();
  if (!window.confirm('Permanently delete your Pipe Time app account and its messages? This cannot be undone.')) return;
  const button = deleteForm.querySelector('button');
  const status = document.getElementById('delete-status');
  button.disabled = true;
  try {
    const response = await fetch('/api/account/delete', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(Object.fromEntries(new FormData(deleteForm)))});
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || 'Unable to delete your account.');
    deleteForm.reset();
    await loadAccount();
    document.getElementById('auth-status').textContent = 'Your account and associated app messages have been deleted.';
  } catch(error) {status.className='status error';status.textContent=error.message;}
  finally {button.disabled=false;}
});
