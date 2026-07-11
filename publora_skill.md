---
name: publora-social
description: Schedule and publish social media posts across 10 platforms (X/Twitter, LinkedIn, Instagram, Threads, TikTok, YouTube, Facebook, Bluesky, Mastodon, Telegram) using the Publora REST API. Use when Shima needs to post, schedule, draft, or manage social content for SparkSphear. Requires PUBLORA_API_KEY in the agent environment.
---

# Publora Social Media Manager

Shima uses this to schedule and publish SparkSphear's social content across all
major platforms through the Publora API. The API key lives in the environment
as `PUBLORA_API_KEY` (already set in /home/shima/.hermes/.env).

## Base
All calls: `https://api.publora.com/api/v1`
Auth header: `x-publora-key: $PUBLORA_API_KEY`

## Core endpoints
- `GET  /platform-connections`                  → list connected accounts (ids like `twitter-123456789`)
- `POST /create-post`                            → schedule/publish a post
- `GET  /list-posts`                             → list all posts (paginated)
- `GET  /get-post/:postGroupId`                 → post status
- `PUT  /update-post/:postGroupId`               → change timing/status
- `DELETE /delete-post/:postGroupId`             → cancel a scheduled post
- `POST /get-upload-url`                         → get pre-signed URL for media upload
- `POST /upload-instagram-cover`                → custom IG Reel cover

## create-post payload
```json
{
  "content": "Your post copy here. #hashtags",
  "platforms": ["twitter-123456789", "linkedin-ABC123"],
  "scheduledTime": "2026-07-10T14:00:00.000Z",   // omit/empty = publish now
  "mediaUrls": []                                 // optional public URLs
}
```
- `scheduledTime` empty or omitted → publishes immediately.
- To post to ALL connected accounts, pass every id from /platform-connections.

## Python helper (run via execute_code)
```python
import os, json, urllib.request

KEY = os.environ.get("PUBLORA_API_KEY")
BASE = "https://api.publora.com/api/v1"

def _req(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method)
    req.add_header("x-publora-key", KEY)
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())

def list_accounts():
    return _req("GET", "/platform-connections")

def schedule_post(content, platforms, scheduled_time=None, media=None):
    body = {"content": content, "platforms": platforms}
    if scheduled_time:
        body["scheduledTime"] = scheduled_time
    if media:
        body["mediaUrls"] = media
    return _req("POST", "/create-post", body)

def list_posts():
    return _req("GET", "/list-posts")
```

## Workflow Shima should follow
1. Call `list_accounts()` to see which platforms are connected and get their ids.
2. Draft the post copy (can use the content engine to generate accompanying media first).
3. `schedule_post(content, [ids], scheduled_time)` — pass a future ISO time, or omit to post now.
4. Confirm success via the returned `postGroupId`; use `list_posts()` to audit.

## Notes
- Free tier available; paid from $2.99/account. Connecting accounts is done by the human
  in the Publora dashboard (app.publora.com) — the agent cannot connect OAuth accounts itself.
- Always confirm the post copy and target platforms with the human before scheduling, unless
  explicitly told to auto-post.
