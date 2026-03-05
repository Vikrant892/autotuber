# AutoTuber — Complete Setup Guide
## History Unveiled | Fully Automated | Runs on GitHub Actions (Free)

---

## STEP 1 — Create GitHub repo (5 min)
1. github.com → New repository → name: `autotuber` → Private → Create
2. Upload everything from this zip into the repo

---

## STEP 2 — YouTube API (10 min, ONE TIME)

### Enable API
1. console.cloud.google.com → log in with **your-email@gmail.com**
2. New Project → name: `autotuber` → Create
3. APIs & Services → Library → search "YouTube Data API v3" → Enable

### Create OAuth credentials
1. APIs & Services → Credentials → + Create Credentials → OAuth client ID
2. Configure consent screen if asked: External, add your-email@gmail.com as test user
3. Application type: Desktop app → Name: autotuber → Create
4. Note your Client ID and Client Secret

### Get refresh token (browser terminal, no install needed)
1. Go to shell.cloud.google.com (free)
2. Upload `setup/setup_youtube.py`
3. Run: `pip install google-auth-oauthlib google-api-python-client && python setup_youtube.py`
4. Follow prompts → log in with your-email@gmail.com → copy the 4 secret values shown

---

## STEP 3 — Add GitHub Secrets
Settings → Secrets → Actions → New repository secret

| Secret Name | Value |
|-------------|-------|
| ANTHROPIC_API_KEY | REDACTED_ANTHROPIC_KEY |
| PEXELS_API_KEY | REDACTED_PEXELS_KEY |
| YOUTUBE_CLIENT_ID | (from Step 2) |
| YOUTUBE_CLIENT_SECRET | (from Step 2) |
| YOUTUBE_TOKEN_JSON | (from setup_youtube.py output) |
| YOUTUBE_CLIENT_SECRETS | (from setup_youtube.py output) |

---

## STEP 4 — Deploy dashboard to Cloudflare Pages
1. dash.cloudflare.com → Workers & Pages → Create → Pages → Upload assets
2. Upload the `autotuber-dashboard/` folder
3. Project name: `autotuber-dashboard` → Deploy
4. Your dashboard: https://autotuber-dashboard.pages.dev

---

## STEP 5 — Done
GitHub repo → Actions → "AutoTuber Pipeline" → Run workflow (first test)
After that: runs automatically 5x per day, every day, forever.

Schedule (Adelaide time): 9:30am · 12:30pm · 4:30pm · 9:30pm · 4:30am
