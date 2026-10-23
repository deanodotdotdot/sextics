/* Drafts outlive mounted panels. Completion can clear only the submitted version. */
((root) => {
  function create(storage) {
    const drafts = new Map(),
      listeners = new Set();
    const key = (id) => 'hodge-discussion-draft:' + id;
    function read(id) {
      if (!drafts.has(id)) {
        try {
          const value = JSON.parse(storage.getItem(key(id)));
          if (typeof value?.body === 'string') drafts.set(id, value);
        } catch {
          /* Storage can be disabled. The in-memory draft remains usable. */
        }
      }
      return drafts.get(id);
    }
    function save(id, body, replyTo) {
      const previous = read(id);
      if (previous?.body === body && JSON.stringify(previous.replyTo) === JSON.stringify(replyTo))
        return previous;
      const value = { body, replyTo };
      drafts.set(id, value);
      try {
        if (body) storage.setItem(key(id), JSON.stringify(value));
        else storage.removeItem(key(id));
      } catch {}
      return value;
    }
    function clear(id, submitted) {
      if (read(id) !== submitted) return false;
      drafts.delete(id);
      try {
        storage.removeItem(key(id));
      } catch {}
      for (const listener of listeners) listener(id, submitted);
      return true;
    }
    return {
      read,
      save,
      clear,
      onClear(listener) {
        listeners.add(listener);
        return () => listeners.delete(listener);
      }
    };
  }
  root.HodgeDrafts = { create };
})(globalThis);
