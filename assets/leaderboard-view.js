/* Owns leaderboard fetching, refresh and rendering for the current route. */
(() => {
  'use strict';
  const $ = (id) => document.getElementById(id);
  const escape = (value) =>
    String(value ?? '').replace(
      /[&<>"']/g,
      (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]
    );
  function create({ records, accountFor, avatar, loadProfiles, rememberAccounts, clearAccounts }) {
    function renderContributor(login, rows) {
      const row = rows.find((r) => r.githubLogin.toLowerCase() === login?.toLowerCase()),
        panel = $('contributorDetails');
      panel.hidden = !row;
      if (!row) {
        panel.innerHTML = '';
        return;
      }
      const account = accountFor(row.githubLogin);
      panel.innerHTML = `<header class="contributor-heading"><p class="dialog-eyebrow">THE CONTRIBUTIONS</p><div class="contributor-title-line"><h2>Constructions by ${escape(account.name)}</h2><a href="https://github.com/${encodeURIComponent(account.githubLogin)}" target="_blank" rel="noopener noreferrer">@${escape(account.githubLogin)} ↗</a></div></header><div class="contribution-list">${row.instanceIds
        .map((id) => {
          const r = records().find((r) => r.id === id);
          return `<div class="contribution-row"><a class="contribution-solution" href="#case/${encodeURIComponent(id)}/solution" aria-haspopup="dialog"><span class="contribution-check" aria-hidden="true">✓</span><span><strong>${escape(r.title)}</strong><small>${r.credit.origin === 'starting-example' ? 'Starting Fermat example' : 'Contributed construction'} · q = ${r.q}</small></span><span class="contribution-read">Read the construction ↗</span></a><a href="#case/${encodeURIComponent(id)}" aria-label="View instance: ${escape(r.title)}">Instance →</a></div>`;
        })
        .join('')}</div>`;
    }
    function paintCommentContributor(login, rows) {
      const row = rows.find((r) => r.githubLogin.toLowerCase() === login?.toLowerCase()),
        panel = $('contributorDetails');
      panel.hidden = !row;
      if (!row) {
        panel.innerHTML = '';
        return;
      }
      const account = accountFor(row.githubLogin);
      panel.innerHTML = `<header class="contributor-heading"><div class="contributor-title-line"><h2>Comments by <code>${escape(account.githubLogin)}</code></h2><a href="https://github.com/${encodeURIComponent(account.githubLogin)}" target="_blank" rel="noopener noreferrer">@${escape(account.githubLogin)} ↗</a></div></header><div class="comment-contribution-list">${(
        row.comments || []
      )
        .map((c) => {
          const record = records().find((r) => r.id === c.instanceId);
          return `<article class="comment-contribution"><a href="#case/${encodeURIComponent(c.instanceId)}/discussion/${c.number}"><strong>${escape(record?.title || c.instanceId)}</strong><small>${escape(new Date(c.createdAt).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' }))} · ${c.isReply ? 'Reply' : 'Comment'} · Read comment →</small></a><div class="comment-preview discussion-markdown"></div></article>`;
        })
        .join('')}</div>`;
      panel.querySelectorAll('.comment-preview').forEach((node, i) => {
        HodgeDiscussionMarkdown.render(node, row.comments[i].body, row.comments[i].url);
        let remaining = 240,
          truncated = false;
        function shorten(parent) {
          for (const child of [...parent.childNodes]) {
            if (remaining <= 0) {
              child.remove();
              truncated = true;
              continue;
            }
            if (child.nodeType === 3) {
              const text = child.textContent;
              if (text.length > remaining) {
                child.textContent = text.slice(0, remaining).replace(/\s+\S*$/, '');
                truncated = true;
              }
              remaining -= text.length;
            } else if (child.nodeType === 1) {
              if (child.matches('.discussion-math-inline,.discussion-math-display,pre'))
                remaining -= (child.querySelector('annotation')?.textContent || child.textContent)
                  .length;
              else shorten(child);
            }
          }
        }
        shorten(node);
        if (truncated) node.append('…');
      });
    }
    function highlightContributor(login, { scroll = true } = {}) {
      document
        .querySelectorAll('#leaderboardRows .contributor-highlight')
        .forEach((row) => row.classList.remove('contributor-highlight'));
      if (!login) return;
      const row = document.getElementById(`contributor-${login.toLowerCase()}`);
      if (!row) return;
      row.classList.add('contributor-highlight');
      if (!scroll) return;
      row.focus({ preventScroll: true });
      const panel = $('contributorDetails');
      if (!panel.hidden)
        panel.scrollIntoView({
          block: 'start',
          behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth'
        });
    }
    function paintRanking(rows, comments) {
      $('leaderboardRows').innerHTML = rows
        .map((row) => {
          const account = accountFor(row.githubLogin);
          return `<tr id="contributor-${escape(row.githubLogin.toLowerCase())}" tabindex="-1"><td class="leaderboard-rank">${row.rank}</td><td><a class="github-account" href="${'#leaderboard/' + encodeURIComponent(row.githubLogin) + (comments ? '/comments' : '')}" aria-label="View ${comments ? 'comments by' : 'constructions by'} ${escape(account.name)}">${avatar(account)}<span><strong>${escape(account.name)}</strong><span class="account-handle">@${escape(account.githubLogin)}</span></span><span class="account-arrow" aria-hidden="true">↗</span></a></td><td class="leaderboard-score">${row.score}<span>${comments ? (row.score === 1 ? 'comment' : 'comments') : row.score === 1 ? 'solve' : 'solves'}</span></td></tr>`;
        })
        .join('');
    }
    const rankings = new Map(),
      contributorComments = new Map();
    let current = null,
      request = null,
      credits = null;
    let rankingSignature = '',
      detailsSignature = '',
      refreshing = false,
      scrollPending = false;

    function paint(rows) {
      const comments = current.mode === 'comments';
      const signature = JSON.stringify([
        current.mode,
        rows,
        rows.map((row) => accountFor(row.githubLogin))
      ]);
      if (signature !== rankingSignature) {
        paintRanking(rows, comments);
        rankingSignature = signature;
      }
      $('leaderboardMessage').hidden = rows.length > 0;
      $('leaderboardMessage').textContent = comments
        ? 'No discussion comments yet.'
        : 'The first solve starts the board.';
    }
    function details(row, comments = []) {
      const signature = JSON.stringify([
        current.mode,
        row,
        comments,
        row && accountFor(row.githubLogin)
      ]);
      if (signature === detailsSignature) return;
      detailsSignature = signature;
      if (current.mode === 'comments')
        paintCommentContributor(current.login, row ? [{ ...row, comments }] : []);
      else renderContributor(current.login, row ? [row] : []);
    }
    async function show(destination, { refresh = false, quiet = false } = {}) {
      if (!quiet) scrollPending = !!destination.login;
      request?.abort();
      const pending = (request = new AbortController());
      current = destination;
      const valid = () => request === pending && !pending.signal.aborted;
      const { mode, login } = destination,
        comments = mode === 'comments';
      for (const [id, active] of [
        ['rankSolves', !comments],
        ['rankComments', comments]
      ])
        $(id).setAttribute('aria-pressed', String(active));
      $('rankingColumn').textContent = comments ? 'Comments' : 'Solves';
      document
        .querySelector('.leaderboard-table')
        .setAttribute(
          'aria-label',
          comments
            ? 'GitHub accounts ranked by comments'
            : 'GitHub accounts ranked by known constructions'
        );
      document.querySelector('#leaderboardView .information-deck').textContent = comments
        ? 'Contributors ranked by comments and replies across the atlas.'
        : 'Contributors to the challenge, ranked by number of solves.';
      let rows = rankings.get(mode);
      const selected = () =>
        rows?.find((row) => row.githubLogin.toLowerCase() === login?.toLowerCase());
      if (rows) {
        paint(rows);
        details(selected(), contributorComments.get(login?.toLowerCase())?.comments);
      } else {
        $('leaderboardRows').replaceChildren();
        rankingSignature = '';
        details(null);
        $('leaderboardMessage').hidden = false;
        $('leaderboardMessage').textContent = 'Loading the leaderboard…';
      }
      $('leaderboardRetry').hidden = true;
      try {
        if (!rows || refresh) {
          if (comments) {
            const data = await HodgeAccount.request('/api/comment-leaderboard', {
              signal: pending.signal
            });
            if (!valid()) return;
            rows = data.rows;
            rememberAccounts(rows);
          } else {
            credits ||= fetch('leaderboard/credits.json')
              .then((response) => {
                if (!response.ok) throw Error('Leaderboard unavailable.');
                return response.json();
              })
              .catch((error) => {
                credits = null;
                throw error;
              });
            rows = HodgeLeaderboard.rank(await credits, records());
            try {
              await loadProfiles(
                rows.map((row) => row.githubLogin),
                pending.signal
              );
            } catch {
              /* Keep displaying the username when profiles are unavailable. */
            }
          }
          if (!valid()) return;
          rankings.set(mode, rows);
          paint(rows);
        }
        const row = selected(),
          key = row?.githubLogin.toLowerCase();
        const cached = contributorComments.get(key);
        details(row, cached?.comments);
        if (!comments || !row || (!refresh && cached && Date.now() - cached.time < 15000)) return;
        if (!cached)
          $('contributorDetails').querySelector('.comment-contribution-list').innerHTML =
            '<p class="comment-load-status" role="status">Loading comments…</p>';
        try {
          const data = await HodgeAccount.request(
            '/api/comment-leaderboard/' + encodeURIComponent(row.githubLogin),
            { signal: pending.signal }
          );
          if (!valid()) return;
          contributorComments.set(key, { comments: data.comments, time: Date.now() });
          // Always clear a previous loading/error message, including for an empty result.
          if ($('contributorDetails').querySelector('.comment-load-status,.comment-load-error'))
            detailsSignature = '';
          details(row, data.comments);
        } catch (error) {
          if (!valid()) return;
          const panel = $('contributorDetails');
          panel.querySelector('.comment-load-status')?.remove();
          panel.querySelector('.comment-load-error')?.remove();
          const message = document.createElement('p');
          message.className = 'comment-load-error';
          message.setAttribute('role', 'status');
          message.textContent = 'Comments could not be refreshed. ';
          const retry = document.createElement('button');
          retry.className = 'discussion-button';
          retry.textContent = 'Try again';
          retry.onclick = () => show(current, { refresh: true, quiet: true });
          message.append(retry);
          panel.append(message);
        }
      } catch (error) {
        if (!valid()) return;
        $('leaderboardMessage').hidden = false;
        $('leaderboardMessage').textContent = rows
          ? 'The leaderboard could not be refreshed.'
          : 'The leaderboard could not be loaded.';
        $('leaderboardRetry').hidden = false;
      } finally {
        if (valid()) {
          highlightContributor(login, { scroll: scrollPending });
          scrollPending = false;
        }
      }
    }
    async function refresh() {
      if (document.hidden || current?.mode !== 'comments' || refreshing) return;
      refreshing = true;
      try {
        await show(current, { refresh: true, quiet: true });
      } finally {
        refreshing = false;
      }
    }
    function leave() {
      request?.abort();
      current = null;
      scrollPending = false;
    }
    for (const [id, mode] of [
      ['rankSolves', 'solves'],
      ['rankComments', 'comments']
    ])
      $(id).addEventListener('click', () => {
        location.hash = HodgeRoutes.leaderboard(mode);
      });
    $('leaderboardRetry').addEventListener('click', () => show(current, { refresh: true }));
    setInterval(refresh, 30000);
    window.addEventListener('focus', refresh);
    document.addEventListener('visibilitychange', refresh);
    document.addEventListener('hodge-session-change', () => {
      request?.abort();
      rankings.clear();
      contributorComments.clear();
      clearAccounts();
      rankingSignature = detailsSignature = '';
      if (current) show(current, { refresh: true, quiet: true });
    });
    return { show, leave };
  }
  window.HodgeLeaderboardView = { create };
})();
