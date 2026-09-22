# Production worker trigger

The processing worker (`app.worker` poll loop) cannot run on Vercel's serverless
runtime, so the queue is drained by an **external periodic caller** hitting the
bounded, idempotent trigger endpoint:

```
Upload → processing_jobs (queued) → external trigger → POST /internal/process → process_one()
```

`POST /internal/process` claims and runs up to `max_jobs` queued jobs per call
(`FOR UPDATE SKIP LOCKED`, so overlapping calls are safe), stops after a 25s time
budget, and returns `{processed, remaining, budget_exhausted}`. It is authenticated
by the `X-Internal-Secret` header (constant-time compared against
`DOCURA_WORKER_TRIGGER_SECRET`). Nothing about OCR, `process_one`, `processing_jobs`,
the endpoint, or the upload flow changes here — only *what calls the endpoint on a
schedule*.

## Why not GitHub Actions `schedule`

The `.github/workflows/docura-worker.yml` `*/5` cron is **best-effort and unreliable**:
across every run to date, not one was a `schedule` event — only `workflow_dispatch`
and `push` ever fired. GitHub's shared scheduler delays and silently drops scheduled
runs under load, and `*/5` (the shortest, most-contended expression) is dropped first.
No YAML change makes it reliable. The workflow is therefore kept only as a **manual /
best-effort backup** trigger (`workflow_dispatch`), not the primary scheduler.

## Primary trigger: external cron pinger

Any reliable HTTP scheduler that can send a **POST with a custom header** works.
**cron-job.org** (free, 1-minute resolution, supports POST + custom headers) is the
reference setup:

| Setting        | Value                                                        |
| -------------- | ----------------------------------------------------------- |
| Title          | `DOCURA worker`                                              |
| URL            | `https://docura-nine.vercel.app/internal/process`           |
| Request method | `POST`                                                       |
| Schedule       | Every 2 minutes (`*/2 * * * *`) — or every 5 to match the old cadence |
| Header         | `X-Internal-Secret: <DOCURA_WORKER_TRIGGER_SECRET>`         |
| Expected       | HTTP `2xx` (a `200` with `{processed, remaining, ...}`)      |
| Timeout        | ≥ 30s (the endpoint's time budget is 25s)                   |

The secret is the **same value** already stored in the Vercel production env
(`DOCURA_WORKER_TRIGGER_SECRET`) and the GitHub Actions secret. Read it from the
Vercel dashboard (Project → Settings → Environment Variables) or `vercel env pull`;
paste it into the pinger's header. **Never commit it or paste it into logs.**

UptimeRobot's free tier is *not* sufficient (GET-only, no custom headers). Cronitor
and EasyCron also work (both support POST + headers).

## Expected execution frequency

Every 2 minutes (recommended) → the queue drains within ≤2 min of upload; each call
processes up to 10 jobs, so a burst drains across consecutive calls
(`budget_exhausted: true` / `remaining > 0` signals more work remains and the next
tick continues it).

## Verify

1. **Endpoint ready** (no secret needed):
   - `curl -X POST https://docura-nine.vercel.app/internal/process` → `401`
   - `curl https://docura-nine.vercel.app/internal/process` (GET) → `405`
   A correctly-authenticated POST returns `200` and drains (proven by the demo E2E).
2. **Live:** after adding the cron job, upload a document, then within ~2 min confirm
   the document reaches `ready`. The pinger's execution history should show `200`s.
