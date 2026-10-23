/* Native GitHub conversations, loaded only when an instance's panel is opened. */
(() => {
  'use strict';
  const escape = (s) =>
    String(s ?? '').replace(
      /[&<>"']/g,
      (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]
    );
  const drafts = new Map();
  let current;
  let discussionIndex = null,
    linksReady;
  function internalLink(href) {
    if (!discussionIndex) return null;
    try {
      const url = new URL(href, location.href),
        match = url.pathname.match(/^\/([^/]+\/[^/]+)\/discussions\/(\d+)\/?$/i);
      if (
        url.hostname === 'hodge.computer' &&
        url.protocol === 'https:' &&
        !url.port &&
        !url.username &&
        !url.password &&
        ['/', '/index.html'].includes(url.pathname) &&
        /^#(?:home|case\/[^/]+(?:\/discussion(?:\/\d+)?)?|technical-information(?:\/[^#]*)?|leaderboard(?:\/[^/]+)?)$/.test(
          url.hash
        )
      )
        return url.hash;
      if (
        !['https:', 'http:'].includes(url.protocol) ||
        url.hostname !== 'github.com' ||
        url.username ||
        url.password ||
        url.port ||
        !match ||
        match[1].toLowerCase() !== discussionIndex.repository.toLowerCase()
      )
        return null;
      const comment = url.hash.match(/^#discussioncomment-(\d+)$/);
      if (url.hash && !comment && !/^#discussion-\d+$/.test(url.hash)) return null;
      const entry = Object.entries(discussionIndex.instances).find(
        ([, thread]) => String(thread.number) === match[2]
      );
      return entry
        ? `#case/${encodeURIComponent(entry[0])}/discussion${comment ? '/' + comment[1] : ''}`
        : null;
    } catch {
      return null;
    }
  }
  function localizeLinks(root) {
    const links = [
      ...(root.matches?.('a[href]') ? [root] : []),
      ...root.querySelectorAll('a[href]')
    ];
    for (const link of links) {
      if (link.matches('.discussion-github,[data-github-original]')) continue;
      const route = internalLink(link.href);
      if (!route) continue;
      link.href = route;
      link.removeAttribute('target');
      link.removeAttribute('rel');
    }
  }
  function startLinks() {
    return (linksReady ||= (async () => {
      try {
        const response = await fetch('discussions/index.json', { cache: 'no-cache' });
        if (!response.ok) return;
        discussionIndex = await response.json();
        localizeLinks(document);
        // Covers comments, replies, previews, and links in dynamically loaded prose.
        new MutationObserver((changes) => {
          for (const change of changes)
            for (const node of change.addedNodes) if (node.nodeType === 1) localizeLinks(node);
        }).observe(document.body, { childList: true, subtree: true });
      } catch {
        /* The original GitHub links remain usable if the mapping is unavailable. */
      }
    })());
  }
  const counts = new Map();
  let countsLoading = false,
    countsUpdated = 0,
    countsVersion = 0;
  function countChanged(id, count) {
    if (!Number.isSafeInteger(count) || count < 0 || counts.get(id) === count) return;
    counts.set(id, count);
    document.dispatchEvent(new CustomEvent('hodge-discussion-counts'));
  }
  async function refreshCounts() {
    if (countsLoading || document.hidden || Date.now() - countsUpdated < 60000) return;
    countsLoading = true;
    countsUpdated = Date.now();
    const version = countsVersion;
    try {
      await HodgeAccount.ready;
      const data = await HodgeAccount.request('/api/discussion-counts');
      if (version !== countsVersion) return;
      for (const [id, count] of Object.entries(data.counts || {}))
        if (Number.isSafeInteger(count) && count >= 0) counts.set(id, count);
      document.dispatchEvent(new CustomEvent('hodge-discussion-counts'));
    } catch {
      /* Counts are optional; every discussion link remains usable. */
    } finally {
      countsLoading = false;
    }
  }
  async function startCounts() {
    await HodgeAccount.ready;
    refreshCounts();
    addEventListener('focus', refreshCounts);
    document.addEventListener('visibilitychange', refreshCounts);
    setInterval(refreshCounts, 60000);
    document.addEventListener('hodge-session-change', () => {
      countsVersion++;
      counts.clear();
      countsUpdated = 0;
      document.dispatchEvent(new CustomEvent('hodge-discussion-counts'));
      refreshCounts();
    });
  }
  const element = (tag, className, text) => {
    const n = document.createElement(tag);
    n.className = className;
    if (text !== undefined) n.textContent = text;
    return n;
  };
  function link(text, url, native = false) {
    const n = element('a', '', text);
    try {
      const u = new URL(url);
      if (u.protocol !== 'https:' || u.hostname !== 'github.com') throw Error();
      n.href = u.href;
      n.target = '_blank';
      n.rel = 'noopener noreferrer';
      if (native) n.dataset.githubOriginal = '';
      else localizeLinks(n);
    } catch {}
    return n;
  }
  const commentNumber = (comment) => {
    try {
      return new URL(comment.url).hash.match(/^#discussioncomment-(\d+)$/)?.[1];
    } catch {
      return null;
    }
  };
  const button = (text, run) => {
    const n = element('button', 'discussion-button', text);
    n.type = 'button';
    n.addEventListener('click', run);
    return n;
  };
  function markup(record) {
    return `<section id="instanceDiscussion" class="discussion-panel" aria-labelledby="discussionHeading" tabindex="-1" data-instance="${escape(record.id)}" hidden>
    <header class="discussion-header"><div><p class="dialog-eyebrow">THE COMMON ROOM</p><h2 id="discussionHeading">Discussion <span class="discussion-count" hidden></span></h2></div><div class="discussion-tools"><a class="discussion-github" target="_blank" rel="noopener noreferrer" hidden>View on GitHub ↗</a><button type="button" class="discussion-refresh discussion-button" aria-label="Refresh discussion" aria-busy="false"><span>Refresh</span></button></div></header>
    <p class="discussion-context">${escape(record.title)} <span>·</span> Questions, calculations, and independent checks</p>
    <div class="discussion-notice" role="status" aria-live="polite"></div>
    <details class="discussion-intro" hidden><summary>About this thread</summary><div class="discussion-markdown"></div></details>
    <div class="discussion-feed" aria-label="Discussion for ${escape(record.title)}"></div>
    <button type="button" class="discussion-more discussion-button" hidden>Load more comments</button>
    <div class="discussion-access"></div>
    <form class="discussion-composer" hidden>
      <div class="discussion-reply-target" hidden><span></span><button type="button" class="discussion-cancel discussion-button">Cancel reply</button></div>
      <div class="discussion-editor-heading"><label for="discussionDraft">Add to the discussion</label><button class="discussion-preview-toggle discussion-button" type="button" aria-pressed="false">Preview</button></div>
      <textarea id="discussionDraft" rows="5" maxlength="30000" aria-describedby="discussionHelp" placeholder="Share an idea, calculation, or question…"></textarea>
      <div class="discussion-preview discussion-markdown" hidden></div>
      <div class="composer-footer"><span id="discussionHelp">Markdown and LaTeX: <code>$x^2$</code> inline, <code>$$…$$</code> on its own line.</span><button type="submit" class="discussion-submit">Post comment ↗</button></div>
      <p class="discussion-post-status" role="status" aria-live="polite"></p>
    </form>
  </section>`;
  }
  function mount(panel) {
    current?.destroy();
    const id = panel.dataset.instance,
      endpoint = '/api/discussions/' + encodeURIComponent(id),
      account = window.HodgeAccount;
    const q = (s) => panel.querySelector(s),
      feed = q('.discussion-feed'),
      notice = q('.discussion-notice'),
      form = q('form'),
      draft = q('textarea'),
      preview = q('.discussion-preview'),
      submit = q('.discussion-submit'),
      refresh = q('.discussion-refresh');
    const requests = new AbortController(),
      comments = new Map(),
      expandedComments = new Map();
    let data = null,
      loaded = false,
      loading = false,
      posting = false,
      replyTo = null,
      previewing = false,
      version = 0,
      commentSequence = 0,
      loadPending = null,
      navigation = 0;
    const pendingKey = 'hodge-discussion-draft:' + id;
    let saved = drafts.get(id);
    try {
      saved ||= JSON.parse(sessionStorage.getItem(pendingKey));
    } catch {}
    if (saved) {
      draft.value = saved.body || '';
      replyTo = saved.replyTo || null;
    }
    const active = () => panel.isConnected && !requests.signal.aborted;
    function save() {
      const value = { body: draft.value, replyTo };
      drafts.set(id, value);
      try {
        if (value.body) sessionStorage.setItem(pendingKey, JSON.stringify(value));
        else sessionStorage.removeItem(pendingKey);
      } catch {}
    }
    function rememberForSignIn() {
      save();
      try {
        sessionStorage.setItem('hodge-discussion-open', id);
        sessionStorage.setItem(pendingKey, JSON.stringify(drafts.get(id)));
      } catch {}
      account.signIn();
    }
    function setPreview(value) {
      previewing = value;
      preview.hidden = !value;
      draft.hidden = value;
      q('.discussion-preview-toggle').textContent = value ? 'Write' : 'Preview';
      q('.discussion-preview-toggle').setAttribute('aria-pressed', String(value));
      if (value)
        HodgeDiscussionMarkdown.render(
          preview,
          draft.value || '*Nothing to preview yet.*',
          data?.url
        );
    }
    function updateComposer() {
      form.hidden = !data?.viewerCanComment || !account.user;
      const access = q('.discussion-access');
      access.replaceChildren();
      if (data?.locked) access.textContent = 'This conversation is locked on GitHub.';
      else if (!account.user) {
        access.append(
          element('span', '', 'Join the conversation with your GitHub account.'),
          button('Sign in with GitHub ↗', rememberForSignIn)
        );
      } else if (data) {
        access.textContent = 'Posting as @' + account.user.login;
      }
      q('.discussion-reply-target').hidden = !replyTo;
      q('.discussion-reply-target span').textContent = replyTo
        ? 'Replying to @' + replyTo.login
        : '';
      q('label').textContent = replyTo ? 'Your reply' : 'Add to the discussion';
      submit.textContent = posting ? 'Posting…' : replyTo ? 'Post reply ↗' : 'Post comment ↗';
      submit.disabled = posting || !draft.value.trim();
      draft.disabled = posting;
      q('.discussion-cancel').disabled = posting;
    }
    function message(text) {
      notice.textContent = text;
      notice.hidden = !text;
    }
    function showPostStatus(text, url) {
      const n = q('.discussion-post-status');
      n.textContent = text;
      if (url) n.append(' ', link('View on GitHub ↗', url, true));
    }
    function commentNode(comment, parent = null) {
      const article = element(
        'article',
        'discussion-comment' + (parent ? ' discussion-reply' : '')
      );
      article.dataset.comment = comment.id;
      const number = commentNumber(comment);
      if (number) article.id = 'discussioncomment-' + number;
      article.tabIndex = -1;
      const header = element('header', 'discussion-comment-header'),
        author = comment.author;
      const authorName = author ? '@' + author.login : 'Deleted account',
        identity = link('', author?.url);
      identity.append(element('span', 'discussion-author-name', authorName));
      identity.title = authorName;
      if (author?.avatarUrl) {
        try {
          const u = new URL(author.avatarUrl);
          if (u.protocol === 'https:' && u.hostname === 'avatars.githubusercontent.com') {
            const img = element('img', 'discussion-avatar');
            img.src = u.href;
            img.alt = '';
            img.width = 30;
            img.height = 30;
            img.loading = 'lazy';
            img.referrerPolicy = 'no-referrer';
            identity.prepend(img);
          }
        } catch {}
      }
      const date = new Date(comment.createdAt),
        dateLink = link(
          Number.isNaN(+date)
            ? 'View comment'
            : date.toLocaleDateString(undefined, {
                month: 'short',
                day: 'numeric',
                year: 'numeric'
              }),
          comment.url
        );
      dateLink.classList.add('discussion-comment-date');
      if (!Number.isNaN(+date)) dateLink.title = date.toLocaleString();
      header.append(identity, dateLink);
      if (comment.updatedAt !== comment.createdAt)
        header.append(element('span', 'discussion-edited', 'edited'));
      const content = element('div', 'discussion-comment-content');
      content.id = 'discussion-comment-content-' + ++commentSequence;
      const toggle = button('', () => {
        expandedComments.set(comment.id, content.hidden);
        updateExpansion();
        if (number)
          history.replaceState(
            history.state,
            '',
            `#case/${encodeURIComponent(id)}/discussion/${number}`
          );
      });
      toggle.classList.add('discussion-comment-toggle');
      toggle.setAttribute('aria-controls', content.id);
      toggle.insertAdjacentHTML(
        'beforeend',
        '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg>'
      );
      const replyCount = comment.replies?.totalCount || 0;
      if (replyCount)
        header.append(
          element(
            'span',
            'discussion-reply-count',
            `${replyCount} ${replyCount === 1 ? 'reply' : 'replies'}`
          )
        );
      header.append(toggle);
      article.append(header, content);
      if (!expandedComments.has(comment.id))
        expandedComments.set(
          comment.id,
          comment.isMinimized ||
            ((comment.body || '').length <= 1200 && (comment.body || '').split('\n').length <= 14)
        );
      let rendered = false;
      function updateExpansion() {
        const expanded = expandedComments.get(comment.id);
        content.hidden = !expanded;
        article.classList.toggle('discussion-collapsed', !expanded);
        toggle.setAttribute('aria-expanded', String(expanded));
        toggle.setAttribute(
          'aria-label',
          `${expanded ? 'Collapse' : 'Expand'} comment by ${author ? '@' + author.login : 'deleted account'}`
        );
        if (expanded && !rendered) {
          rendered = true;
          renderContent();
        }
      }
      function renderContent() {
        const body = element('div', 'discussion-markdown');
        if (comment.isMinimized)
          body.textContent = 'This comment was hidden by a GitHub moderator.';
        else HodgeDiscussionMarkdown.render(body, comment.body, data.url);
        content.append(body);
        if (data.viewerCanComment && !comment.isMinimized) {
          content.append(
            button('Reply', () => {
              if (posting) return;
              replyTo = {
                id: (parent || comment).id,
                login: (parent || comment).author?.login || 'deleted account'
              };
              save();
              setPreview(false);
              updateComposer();
              draft.focus();
            })
          );
        }
        if (!parent) {
          const replies = element('div', 'discussion-replies');
          content.append(replies);
          for (const reply of comment.replies?.nodes || [])
            replies.append(commentNode(reply, comment));
          if (comment.replies?.pageInfo?.hasNextPage) {
            const more = button('Load more replies', async () => {
              more.disabled = true;
              try {
                await loadReplies(comment);
                if (!active()) return;
                article.replaceWith(commentNode(comment));
              } catch (e) {
                if (active()) {
                  message(e.message);
                  more.disabled = false;
                }
              }
            });
            content.append(more);
          }
        }
      }
      updateExpansion();
      return article;
    }
    function renderFeed() {
      feed.replaceChildren();
      if (!comments.size) {
        const empty = element('div', 'discussion-empty');
        empty.append(
          element('h3', '', 'Start the conversation.'),
          element('p', '', 'Share a question, a partial calculation, or an independent check.')
        );
        feed.append(empty);
      } else for (const comment of comments.values()) feed.append(commentNode(comment));
      const count = q('.discussion-count'),
        total = data.totalCommentCount;
      count.hidden = !Number.isSafeInteger(total);
      count.textContent = count.hidden ? '' : String(total);
      count.title = 'Comments, including replies';
      countChanged(id, total);
      q('.discussion-more').hidden = !data.comments.pageInfo.hasNextPage;
      const github = q('.discussion-github');
      github.href = data.url;
      github.hidden = false;
      const intro = q('.discussion-intro');
      intro.hidden = !data.body;
      if (data.body)
        HodgeDiscussionMarkdown.render(intro.querySelector('div'), data.body, data.url);
      updateComposer();
    }
    function load(append = false) {
      if (loading) return loadPending;
      loadPending = loadPage(append);
      return loadPending;
    }
    async function loadPage(append = false) {
      if (loading) return;
      loading = true;
      const run = ++version;
      refresh.disabled = true;
      refresh.setAttribute('aria-busy', String(!append));
      refresh.setAttribute('aria-label', append ? 'Refresh discussion' : 'Refreshing discussion');
      q('.discussion-more').disabled = true;
      message(append ? 'Loading more comments…' : loaded ? '' : 'Loading discussion…');
      try {
        await account.ready;
        if (!active() || run !== version) return;
        const next = await account.request(
          endpoint +
            (append ? '?' + new URLSearchParams({ after: data.comments.pageInfo.endCursor }) : ''),
          { signal: requests.signal }
        );
        if (!active() || run !== version) return;
        data = next;
        loaded = true;
        if (!append) comments.clear();
        for (const c of next.comments.nodes) comments.set(c.id, c);
        renderFeed();
        message('');
        return true;
      } catch (e) {
        if (active() && run === version) {
          message(e.message);
          if (e.status === 401 || e.status === 403) {
            data = null;
            comments.clear();
            feed.replaceChildren();
            q('.discussion-intro').hidden = true;
            q('.discussion-count').hidden = true;
            q('.discussion-more').hidden = true;
          }
          updateComposer();
        }
        return false;
      } finally {
        if (run === version) {
          loading = false;
          refresh.disabled = false;
          refresh.setAttribute('aria-busy', 'false');
          refresh.setAttribute('aria-label', 'Refresh discussion');
          q('.discussion-more').disabled = false;
        }
      }
    }
    async function loadReplies(comment) {
      const run = version,
        page = await account.request(
          endpoint +
            '/replies?' +
            new URLSearchParams({
              commentId: comment.id,
              after: comment.replies.pageInfo.endCursor
            }),
          { signal: requests.signal }
        );
      if (!active() || run !== version) return;
      const seen = new Set(comment.replies.nodes.map((r) => r.id));
      comment.replies.nodes.push(...page.nodes.filter((r) => !seen.has(r.id)));
      comment.replies.pageInfo = page.pageInfo;
    }
    function findComment(number) {
      for (const comment of comments.values()) {
        if (commentNumber(comment) === number) return { comment };
        const reply = comment.replies?.nodes.find((reply) => commentNumber(reply) === number);
        if (reply) return { comment: reply, parent: comment };
      }
    }
    async function open(number) {
      const visit = ++navigation,
        valid = () => active() && visit === navigation && !panel.hidden;
      if (loading) await loadPending;
      else if (!loaded) await load();
      if (!number || !/^\d+$/.test(number) || !valid() || !data) return;
      let found = findComment(number);
      try {
        // Search already returned comments first, then request later pages only as needed.
        while (!found && data.comments.pageInfo.hasNextPage) {
          const cursor = data.comments.pageInfo.endCursor,
            ok = await load(true);
          if (!valid() || !data || !ok) return;
          found = findComment(number);
          if (data.comments.pageInfo.endCursor === cursor) break;
        }
        if (!found)
          for (const parent of comments.values()) {
            while (!found && parent.replies?.pageInfo.hasNextPage) {
              const cursor = parent.replies.pageInfo.endCursor;
              await loadReplies(parent);
              if (!valid()) return;
              found = findComment(number);
              if (parent.replies.pageInfo.endCursor === cursor) break;
            }
            if (found) break;
          }
        if (!valid()) return;
        if (found) {
          expandedComments.set(found.comment.id, true);
          if (found.parent) expandedComments.set(found.parent.id, true);
          renderFeed();
          message('');
          const article = document.getElementById('discussioncomment-' + number);
          article.classList.add('discussion-comment-linked');
          article.focus({ preventScroll: true });
          article.scrollIntoView({
            block: 'start',
            behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth'
          });
          setTimeout(() => article.classList.remove('discussion-comment-linked'), 3200);
        } else {
          message('This comment is no longer available in the conversation. ');
          notice.append(
            link('Check on GitHub ↗', data.url + '#discussioncomment-' + number, true)
          );
          notice.scrollIntoView({ block: 'center' });
        }
      } catch (error) {
        if (valid()) {
          message(error.message + ' ');
          notice.append(
            link('View comment on GitHub ↗', data.url + '#discussioncomment-' + number, true)
          );
          notice.scrollIntoView({ block: 'center' });
        }
      }
    }
    draft.addEventListener('input', () => {
      save();
      updateComposer();
    });
    q('.discussion-preview-toggle').addEventListener('click', () => setPreview(!previewing));
    q('.discussion-cancel').addEventListener('click', () => {
      replyTo = null;
      save();
      updateComposer();
    });
    q('.discussion-refresh').addEventListener('click', () => load());
    q('.discussion-more').addEventListener('click', () => load(true));
    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      if (posting || !draft.value.trim() || !data?.viewerCanComment) return;
      posting = true;
      updateComposer();
      showPostStatus('');
      const parent = replyTo?.id,
        body = draft.value,
        postingUser = account.user?.login;
      try {
        const posted = await account.request(endpoint, {
          method: 'POST',
          body: JSON.stringify({ body, ...(parent ? { replyToId: parent } : {}) })
        });
        drafts.delete(id);
        try {
          sessionStorage.removeItem(pendingKey);
        } catch {}
        if (!active() || account.user?.login !== postingUser) return;
        draft.value = '';
        replyTo = null;
        setPreview(false);
        showPostStatus(parent ? 'Reply posted.' : 'Comment posted.', posted.url);
        expandedComments.set(posted.id, true);
        if (parent) expandedComments.set(parent, true);
        if (parent && comments.has(parent)) {
          const c = comments.get(parent);
          c.replies ||= { nodes: [], totalCount: 0, pageInfo: { hasNextPage: false } };
          c.replies.nodes.push(posted);
          c.replies.totalCount++;
        } else if (!parent) {
          comments.set(posted.id, {
            ...posted,
            replies: { nodes: [], totalCount: 0, pageInfo: { hasNextPage: false } }
          });
          data.comments.totalCount++;
        }
        if (Number.isSafeInteger(data.totalCommentCount)) data.totalCommentCount++;
        renderFeed();
      } catch (e) {
        if (active()) {
          showPostStatus(
            e.status && e.status < 500
              ? e.message
              : 'Posting could not be confirmed. Your draft is saved; check the GitHub thread before trying again.',
            e.status && e.status < 500 ? null : data.url
          );
          if (e.status === 401) await account.refresh();
        }
      } finally {
        posting = false;
        if (active()) updateComposer();
      }
    });
    function sessionChanged() {
      if (!active()) return;
      navigation++;
      version++;
      loading = false;
      data = null;
      loaded = false;
      comments.clear();
      feed.replaceChildren();
      q('.discussion-intro').hidden = true;
      q('.discussion-intro div').replaceChildren();
      q('.discussion-github').hidden = true;
      q('.discussion-count').hidden = true;
      q('.discussion-more').hidden = true;
      updateComposer();
      if (!panel.hidden) open(location.hash.split('/')[3]);
    }
    document.addEventListener('hodge-session-change', sessionChanged);
    const controller = {
      open,
      destroy() {
        save();
        requests.abort();
        document.removeEventListener('hodge-session-change', sessionChanged);
      }
    };
    try {
      controller.resume = sessionStorage.getItem('hodge-discussion-open') === id;
      if (controller.resume) sessionStorage.removeItem('hodge-discussion-open');
    } catch {}
    current = controller;
    updateComposer();
    return controller;
  }
  window.HodgeDiscussion = {
    markup,
    mount,
    startLinks,
    internalLink,
    localizeLinks,
    open: (number) => current?.open(number),
    unmount() {
      current?.destroy();
      current = null;
    },
    startCounts,
    refreshCounts,
    count: (id) => counts.get(id)
  };
})();
