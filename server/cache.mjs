// A bounded cache of in-flight requests and completed values. A slow request does
// not expire while it is running; failed and invalidated requests cannot refill it.
export class RequestCache {
  constructor(ttl, limit = 32) {
    this.ttl = ttl;
    this.limit = limit;
    this.entries = new Map();
  }
  get(key, load) {
    const now = Date.now();
    for (const [id, entry] of this.entries) if (entry.expires <= now) this.entries.delete(id);
    const cached = this.entries.get(key);
    if (cached) return cached.pending;
    if (this.entries.size >= this.limit) {
      const oldest = [...this.entries].find(([, entry]) => entry.expires !== Infinity);
      if (!oldest) return Promise.reject(new Error('Too many pending upstream requests.'));
      this.entries.delete(oldest[0]);
    }
    const entry = { expires: Infinity };
    entry.pending = Promise.resolve()
      .then(load)
      .then(
        (value) => {
          entry.expires = Date.now() + this.ttl;
          return value;
        },
        (error) => {
          if (this.entries.get(key) === entry) this.entries.delete(key);
          throw error;
        }
      );
    this.entries.set(key, entry);
    return entry.pending;
  }
  clear() {
    this.entries.clear();
  }
}
