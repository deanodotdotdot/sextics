# AWS hosting

The static website is served from a private S3 bucket through CloudFront. Only
`/auth/*` and `/api/*` reach API Gateway and the Node 24 Lambda function. GitHub
remains the discussion store; DynamoDB holds short-lived login sessions and
one-use OAuth flows. Secrets Manager holds the existing Sextics GitHub App
credentials. No Lean builds run in AWS.

GitHub's `main` branch is the source of truth for the website. Make content and
code changes through reviewed commits; the static publishing workflow builds
from that branch and uploads its public artifact. Do not edit the hosted
files independently of the repository.

`template.json` describes the website infrastructure. `artifacts.json` creates
the separate private bucket used for Lambda deployment packages. The
CloudFormation service role is named `sextics`; the Lambda runtime role has only
the permissions needed for its session table, app secret, and log stream.
These roles are administered by the repository maintainers.

## Build a release

Build releases from current `main`, including its accepted records.

```sh
python3 scripts/build-content.py
python3 scripts/validate-records.py
python3 scripts/check-content.py
npm ci --prefix server --ignore-scripts
python3 infra/aws/package.py --site . --output /tmp/sextics-release
```

The packager uses the public roots and file types in
`public-files.json`; content link checks use the same boundary. Top-level and nested
symlinks are refused. The public package includes only meshes selected by the atlas
and saved homepage, plus their referenced buffers. Unused mesh files fail packaging
and must be removed from the checkout; earlier versions remain in Git history.
It never copies the whole
repository, `.git`, credentials, server sources, dependencies, or local caches
into the public website. The Lambda archive contains only the runtime modules,
pinned dependencies, instance catalogue, discussion mapping, contributor IDs, and
the shared route parser. Its SHA-256
and the exact public file list and counts are recorded in `build.json`. Do not put credentials
in either package.

## Deploy

Create the artifacts stack first, then upload `lambda.zip` to its private bucket
under `lambda/<sha256>.zip`. Create or update the `hodge-sextics` stack with:

- `ArtifactBucket`: the artifacts-stack bucket;
- `ArtifactKey`: the uploaded package key;
- `SiteOrigin`: `https://hodge.computer`;
- `DomainName` and `CertificateArn`: the domain and its validated ACM certificate
  in `us-east-1`, or empty strings while preparing the CloudFront preview.

Use the `sextics` service role and acknowledge `CAPABILITY_NAMED_IAM`. Preserve
existing parameter values on updates. Inspect CloudFormation events and require
`CREATE_COMPLETE` or `UPDATE_COMPLETE`; submitting a deployment is not evidence
that it succeeded.

The outputs identify the website bucket, CloudFront distribution, API, session
table, and app secret. Upload the public package to the website bucket with
`Cache-Control: public,max-age=60`; use a CloudFront invalidation for immediate
rollout. Upload assets and content before `index.html`.
After uploading the new public files, run `retire.py --bucket <bucket> --manifest
<release>/build.json`. It removes files absent from the new release that were
recorded by `deployment/public-files.json`. It also lists the `assets/meshes/`
prefix and deletes every unselected mesh, including versions published before
release manifests existed. It never deletes notification state or inventories
unrelated storage prefixes. Other public files require the prior manifest as
ownership evidence. Open tabs still requesting an old mesh may need a reload.

Apply the updated `publisher.json` IAM policy before deploying the workflow with
retirement; it grants deletion within public roots, including obsolete meshes.

Copy the existing GitHub App configuration directly from its private local
file into the named Secrets Manager secret, without printing it or writing it
to the checkout. There is no production registration endpoint or setup token.
When rotating this configuration, restart the Lambda execution environments
with a configuration/code update, because each environment caches the secret.

Infrastructure and backend releases are owner-operated. To activate
`.github/workflows/deploy-website.yml`, install the
`publisher.json` stack and set the repository variable `AWS_WEBSITE_ROLE` to its
role output. This separate role can upload static
files and invalidate this distribution; it cannot read app secrets, sessions,
or change Lambda or IAM. It trusts only this repository's `main` identity,
including the immutable organization and repository IDs in the current GitHub
OIDC subject format. Recheck that identity when changing the publishing repository.

A GitHub-token push from the acceptance publisher does not itself start another
push workflow. The deployment workflow therefore handles successful
`workflow_run` events for `Publish accepted solve`, as well as reviewed content
pushes to `main`. It always checks out current `main`, never the submitted proof
branch or its artifacts. It does not run Lean again. Lambda code and new
discussion mappings require an owner-operated backend deployment separately.

## Discord announcements

Create an incoming webhook in the announcement channel and store its full URL as
the repository Actions secret `DISCORD_SOLVE_WEBHOOK_URL`. The website deployment
workflow announces newly published atlas entries and accepted solves automatically.
Solve messages credit the PR author and link to the accepted PR and instance.
There is no separate bot process, Discord bot account, or polling service.

`discussion-alerts.yml` also handles GitHub's `discussion_comment: created` event,
including replies and comments posted through the website. Each alert identifies
the commenter and links directly to the comment on hodge.computer; discussions
outside the atlas link to GitHub. Comment bodies are not copied into the feed.
Edits and deletions do not send alerts, and enabling this workflow does not replay
old comments. The webhook's configured name and avatar are used for all messages.
This workflow does not rebuild the website.

Comment delivery records live separately at
`notifications/discussion-comments/<comment-id>.json` in the website bucket.
They retain the Discord message ID and prevent a successful workflow rerun from
posting the same comment twice. Each comment has its own concurrency group and
storage key, so a burst of comments does not cancel pending alerts or overwrite
another comment's record. The workflow reuses the existing publishing identity;
no new secret, AWS permission, GitHub App webhook, or backend deployment is needed.
Retry failed comment deliveries through their original workflow run, subject
to the delivery caveat below.

Before the first deployment with this secret, the workflow initializes its baseline
from the existing hosted atlas. It does not announce historical results. After upload,
it waits for the published atlas to match the new build, then sends any pending announcements.
The website bucket's `notifications/discord-state.json` records announced instance
and solve IDs, using the publisher's existing S3 permissions; it contains no secrets.
Keep this state when redeploying or rolling back to avoid duplicate announcements.

The sender confirms each message with Discord and saves progress after each one.
Retries skip recorded announcements; rate limits are retried automatically. A failed
notification step is visible in Actions and does not undo the website upload. Rerun
deployment to deliver pending messages. If a request times out or the run stops after
Discord saved a message but before S3 recorded it, inspect the channel before retrying:
Discord and S3 cannot commit atomically, so that narrow interruption can duplicate a
message. Removing the secret disables announcements. Never commit or log the webhook URL.

## Domain and email

The domain is registered at Hover and uses a Route 53 hosted zone. The apex A
and AAAA alias records point to CloudFront, with its ACM certificate in
`us-east-1`. Titan handles email; preserve its MX, SPF, and DKIM records when
changing DNS. Website infrastructure changes must not alter email routing.

## Verification and operations

Check the homepage, a rendered surface, technical content, and an instance's
discussion panel. Check `/api/session`, disabled `/auth/setup`, and inaccessible
`/.git/config` and `/server/` paths. API responses and redirects must remain
uncached, and cookies must be Secure, HttpOnly, and SameSite=Lax. Verify sign-in and sign-out. Posting a comment creates public activity and may
notify subscribers.
Private GitHub discussions must remain unavailable to anonymous visitors.

DynamoDB TTL is eventual cleanup, not the authorization boundary. Application
checks reject expired sessions immediately. Conditional operations prevent
OAuth replay and enforce the shared posting throttle. Revoking a session must
take effect across Lambda environments.

The initial API limit is five requests/second with a burst of ten, Lambda
reserved concurrency is five, and DynamoDB on-demand throughput is capped at
25 read and 25 write units/second. Lambda logs are retained for seven days;
application logs must not contain OAuth URLs, cookies, tokens, or comment bodies.
These limits reduce exposure to excessive use but are not a billing cap.

CloudFormation retains the public-file bucket and GitHub App secret on stack
deletion. Any shutdown or cleanup must deliberately review those retained
resources and the domain's mail records. Deleting hosting must not delete or
invalidate Titan email configuration.
