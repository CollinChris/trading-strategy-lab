# External cron via cron-job.org

GitHub's own `schedule:` triggers are best-effort: during Actions incidents
(2026-08-26/27) runs fired hours late or were dropped outright. The fix is to
trigger workflows from an external scheduler through the `workflow_dispatch`
API, which starts runs immediately. The GitHub `schedule:` blocks stay in the
workflows as a free fallback — every job here is idempotent, so a duplicate
run is harmless (scans dedup on `client_order_id`, flatten/journal are no-ops
when there's nothing to do).

[cron-job.org](https://cron-job.org) is free and supports full cron
expressions, **timezone-aware schedules** (no more DST comment gymnastics —
schedule directly in America/New_York), custom headers, POST bodies, and
email alerts when a job's HTTP call fails.

## One-time setup

1. **Create a fine-grained GitHub PAT** at
   <https://github.com/settings/personal-access-tokens/new>:
   - Repository access: *Only select repositories* → `trading-strategy-lab`
     and `systemdesign`.
   - Permissions → Repository permissions → **Actions: Read and write**
     (nothing else).
   - Expiration: 1 year (put a reminder in your calendar; cron-job.org will
     also start emailing failures when it expires).
2. **Create a cron-job.org account** and add the jobs below.

## Job template

Every job is the same HTTP call, differing only in the workflow filename,
repo, and schedule:

- **URL**: `https://api.github.com/repos/CollinChris/<REPO>/actions/workflows/<FILE>/dispatches`
- **Method**: `POST`
- **Headers**:
  - `Authorization: Bearer <YOUR_PAT>`
  - `Accept: application/vnd.github+json`
- **Body**: `{"ref":"main"}`
- **Settings**: enable *"Save responses"* and failure notifications. A
  successful dispatch returns HTTP 204.

Test any job's values from a terminal first:

```bash
curl -i -X POST \
  -H "Authorization: Bearer $PAT" \
  -H "Accept: application/vnd.github+json" \
  https://api.github.com/repos/CollinChris/trading-strategy-lab/actions/workflows/paper-scan.yml/dispatches \
  -d '{"ref":"main"}'          # expect: HTTP/2 204
```

## Jobs

### trading-strategy-lab — timezone **America/New_York**

| Job | Workflow file | Schedule (ET) | Notes |
|---|---|---|---|
| Paper scan | `paper-scan.yml` | `*/10 9-15 * * 1-5` | 09:00–15:50; scans before 09:35 exit without trading |
| Paper flatten | `paper-flatten.yml` | `40 15 * * 1-5` | 15:40 — timezone-aware, so no EST/EDT second slot needed |
| Paper journal | `paper-journal.yml` | `30 17 * * 1-5` | nightly journal |
| Journal retry | `paper-journal.yml` | `30 19 * * 1-5` | idempotent retry |
| Journal back-fill | `paper-journal.yml` | `30 10 * * 1-5` | next morning, catches exits filled at the open |

### systemdesign — timezone **Asia/Singapore**

| Job | Workflow file | Schedule (SGT) | Notes |
|---|---|---|---|
| Daily notification | `daily-notification.yml` | `0 13 * * *` | 1pm SGT, same intent as the old 05:00 UTC cron |

## Verifying

After the first scheduled firing, check the run shows `workflow_dispatch` as
its event and started on time:

```bash
gh run list --limit 5 --json name,event,createdAt,conclusion
```

Runs triggered externally show `workflow_dispatch`; stragglers from GitHub's
own fallback crons still show `schedule`.
