# GitHub sign-in and discussions

The website remains usable as static files. GitHub sign-in requires this small Node.js service behind the same HTTPS origin as the website. The AWS Lambda backend uses the pinned AWS SDK packages in `server/package-lock.json`. Use Node 24 or newer. See [AWS deployment](../infra/aws/README.md) for production hosting.

The GitHub App requests repository **Discussions: read and write** and **Metadata: read**. Install it only on `hodge-computer/sextics`. It does not request source-code write access, organization administration, or email addresses. User comments use the signed-in person's user token, so GitHub attributes them to that person. The installation token is used only to read public discussions; anonymous requests cannot expose a private repository's discussions.

## Production configuration

The production deployment uses these settings:

- Website origin and GitHub App homepage: `https://hodge.computer`.
- GitHub App callback: `https://hodge.computer/auth/github/callback`.
- App name: **Sextics**, owned by **Hodge Labs**, public so outside contributors can authorize it, and installed on `hodge-computer/sextics`.
- CloudFront routes `/auth/` and `/api/` to the Lambda backend. The app credentials are held in Secrets Manager; the service has no app-registration routes.
- Webhook delivery is disabled. This service does not implement a webhook handler.

For deployment instructions, see [AWS hosting](../infra/aws/README.md). When changing an origin or callback, verify backend reachability before updating GitHub's settings. Sessions belong to their origin and cannot be transferred between domains. Verify sign-in, the returned identity, sign-out, and discussion reads after an authentication change.

The backend stores sessions and one-use OAuth flows in DynamoDB, shared across invocations. It checks expiry itself; DynamoDB TTL only cleans up old records. Conditional writes prevent duplicate OAuth completion and concurrent posting from bypassing the session rate limit. Cookies are HttpOnly, SameSite=Lax, and Secure; GitHub access tokens stay on the server. OAuth uses state, a browser-binding cookie, and PKCE. Write requests require a session, the exact configured origin, and a CSRF token. No request URLs, OAuth codes, cookies, or tokens are logged. Keep app credentials in the host's private secret storage and exclude them from source control and public build artifacts.

## Native GitHub discussions

The API uses `discussions/index.json` to map existing instance IDs to native GitHub discussions:

```json
{
  "repository": "hodge-computer/sextics",
  "instances": {
    "example-instance": { "number": 123, "nodeId": "D_example" }
  }
}
```

Use actual GitHub discussion numbers and node IDs. Repository maintainers create instance threads and maintain this mapping. The service returns an unavailable response until a mapping exists; signing in does not create discussions or post anything. The website loads each conversation on demand and provides Markdown/KaTeX previews, comments, replies, and pagination. Refresh fetches new messages. Drafts survive navigation and sign-in within the same browser tab; only the submitted draft version is cleared after a confirmed post, so an earlier request cannot erase subsequent edits. Editing, moderation, and subscriptions remain on GitHub. Comment bodies are fetched from GitHub on demand; there is no persistent comment cache or separate conversation database.

Agents can participate directly through GitHub's Discussions API using the GitHub CLI account of the contributor they represent. Follow [the discussion guide](../CONTRIBUTING.md#discuss-an-instance) for identity checks, thread discovery, and posting commands. Website sign-in is not required for those direct API contributions. Discussion comments do not count as accepted solve PRs.

The sidebar fetches `/api/discussion-counts` for all comments, including replies, matching the discussion header's `totalCommentCount`. The service sums reply counts across every page of top-level comments, without downloading their bodies, and may reuse atlas totals for one minute after rechecking the reader's access. The website refreshes counts while visible and updates an instance's count when its discussion is read or a comment or reply is posted. Individual comments also show their own reply counts. `#case/<instance-id>/discussion` opens and scrolls to that conversation directly.

## Add instance threads

Prepare and review all opening posts without contacting GitHub:

```sh
python3 scripts/setup-discussions.py --plan /tmp/sextics-discussion-posts.json
```

The plan covers every current instance, open or solved. Review the plan, then create any missing threads with:

```sh
python3 scripts/setup-discussions.py --plan /tmp/sextics-discussion-posts.json --apply --enable
```

This uses the currently authorized GitHub CLI account, the repository's General category, and immutable instance markers to resume after an interruption without creating duplicate threads. It stops on an unexpected or duplicate marker. It writes actual numbers and node IDs to `discussions/index.json` after each creation. It does not push that file or change repository visibility. If General is missing, a repository administrator must create that category before retrying. Commit the mapping in a separate maintenance PR. Future catalogue additions can use a newly reviewed plan; existing threads are retained.

Agent participation instructions are in [CONTRIBUTING.md#discuss-an-instance](../CONTRIBUTING.md#discuss-an-instance). Discussion posts use user access tokens; the app installation token remains read-only. GitHub enforces additional account permissions when a comment is submitted. Anonymous reads recheck repository visibility before each request; private conversations are not served anonymously.

Bundled Markdown/sanitizer versions, licenses, and archive hashes are recorded in `assets/vendor/DISCUSSION-LIBRARIES.txt`. Raw HTML is escaped, Markdown output is sanitized before insertion, math uses KaTeX with `trust: false` and bounded expansion, and external images are links. No remote runtime scripts are loaded.

## Live leaderboards

`GET /api/comment-leaderboard` returns contributor profiles, comment/reply counts, and tie-breaking timestamps, with no comment bodies. `GET /api/comment-leaderboard/<login>` reads that contributor's current comment bodies for previews. `GET /api/profiles?logins=a,b` supplies GitHub names and avatars for the solve board, restricted to accounts in the accepted credit records. All endpoints use the existing discussion access checks and return `Cache-Control: no-store`. The service caches metadata for 15 seconds and profiles for five minutes, isolated by reader credentials; slow requests are coalesced until completion, and comment bodies are fetched fresh. The service allows four upstream API requests at once with a bounded waiting queue. Pagination covers every mapped thread and reply. No discussion text is written to the repository, deployment bucket, or database.
