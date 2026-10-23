/* User identity stays with GitHub; access tokens never enter browser storage. */
(() => {
  'use strict';
  const button = document.getElementById('githubSignIn');
  if (!button) return;
  let session = null,
    connected = false;
  const panel = document.createElement('div');
  panel.className = 'account-menu';
  panel.hidden = true;
  const identity = document.createElement('span');
  identity.className = 'account-identity';
  const profile = document.createElement('a');
  profile.textContent = 'GitHub profile ↗';
  profile.target = '_blank';
  profile.rel = 'noopener noreferrer';
  const logout = document.createElement('button');
  logout.type = 'button';
  logout.textContent = 'Sign out';
  const message = document.createElement('p');
  message.setAttribute('role', 'status');
  message.hidden = true;
  panel.append(identity, profile, logout, message);
  button.parentElement.append(panel);
  function feedback(text) {
    message.textContent = text;
    message.hidden = false;
    panel.hidden = false;
    button.setAttribute('aria-expanded', 'true');
  }
  function render() {
    button.replaceChildren();
    button.removeAttribute('aria-disabled');
    button.setAttribute('aria-expanded', 'false');
    panel.hidden = true;
    message.hidden = true;
    if (session) {
      const image = document.createElement('img');
      image.src = session.user.avatar;
      image.alt = '';
      image.width = 22;
      image.height = 22;
      const label = document.createElement('span');
      label.textContent = '@' + session.user.login;
      button.append(image, label);
      button.setAttribute('aria-label', 'GitHub account: ' + session.user.login);
      button.setAttribute('aria-haspopup', 'true');
      identity.textContent = session.user.name;
      profile.href = session.user.url;
      profile.hidden = false;
      logout.hidden = false;
    } else {
      button.textContent = 'Sign in with GitHub ↗';
      button.removeAttribute('aria-label');
      button.removeAttribute('aria-haspopup');
      profile.hidden = true;
      logout.hidden = true;
      identity.textContent = '';
      if (!connected) button.setAttribute('aria-disabled', 'true');
    }
  }
  async function refresh() {
    try {
      const response = await fetch('/api/session', {
        credentials: 'same-origin',
        cache: 'no-store'
      });
      if (!response.ok) throw new Error('unavailable');
      const data = await response.json();
      session = data.user ? data : null;
      connected = data.connected === true;
    } catch {
      session = null;
      connected = false;
    }
    render();
    document.dispatchEvent(
      new CustomEvent('hodge-session-change', { detail: { user: session?.user || null } })
    );
  }
  function signIn() {
    if (!connected) {
      feedback('GitHub sign-in is unavailable. Please try again shortly.');
      return;
    }
    const target = new URL('/auth/github', location.href);
    target.searchParams.set('returnTo', '/' + (location.hash || '#home'));
    location.assign(target.href);
  }
  async function request(url, options = {}) {
    const response = await fetch(url, {
      ...options,
      credentials: 'same-origin',
      cache: 'no-store',
      headers: {
        ...options.headers,
        ...(options.method === 'POST'
          ? { 'Content-Type': 'application/json', 'X-CSRF-Token': session?.csrf || '' }
          : {})
      }
    });
    const data = await response.json();
    if (!response.ok) {
      const error = new Error(
        data.error || 'The discussion could not be reached. Please try again.'
      );
      error.status = response.status;
      throw error;
    }
    return data;
  }
  window.HodgeAccount = {
    get user() {
      return session?.user || null;
    },
    signIn,
    request,
    refresh,
    ready: null
  };
  button.addEventListener('click', () => {
    if (session) {
      panel.hidden = !panel.hidden;
      button.setAttribute('aria-expanded', String(!panel.hidden));
      return;
    }
    signIn();
  });
  logout.addEventListener('click', async () => {
    logout.disabled = true;
    try {
      const response = await fetch('/api/sign-out', {
        method: 'POST',
        credentials: 'same-origin',
        headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': session?.csrf || '' },
        body: '{}'
      });
      if (!response.ok) throw new Error('failed');
      session = null;
      render();
      await refresh();
      button.focus();
    } catch {
      feedback('Could not sign out. Please try again.');
    } finally {
      logout.disabled = false;
    }
  });
  document.addEventListener('click', (event) => {
    if (!panel.contains(event.target) && !button.contains(event.target)) {
      panel.hidden = true;
      button.setAttribute('aria-expanded', 'false');
    }
  });
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && !panel.hidden) {
      panel.hidden = true;
      button.setAttribute('aria-expanded', 'false');
      button.focus();
    }
  });
  window.HodgeAccount.ready = refresh();
})();
