# Checkpoint evidence

## CP0

- Existing Python 3.14 virtual environment loads pytest and all lab dependencies.
- Baseline: `python -m pytest tests/ -q -m "not docker"`: 7 passed,
  66 failed, 16 errors, 5 skipped, 2 deselected. Failures are unfinished lab
  implementations, missing workflow and deployment URL; no missing modules.
- Docker Engine 29.1.2 is available.
- `.env` and both local virtual environments are excluded from Git.
- Implementation and documentation were prepared with AI assistance; the
  student must review and be able to explain the submitted work.

## CP1

- Config, JSON logging and liveness: 13/13 tests passed.
- Startup validates required settings before accepting traffic.

## CP2

- Dockerfile, Compose and ignore rules: 14 static tests passed.
- Real build started; base-image download is slow. Build/size evidence will be recorded after completion.

## CP3

- API authentication, sliding-window limiter and monthly cost guard: 22/22 tests passed.
- Rate limiting uses Redis WATCH/MULTI to prevent concurrent quota races.
- Lab budget guard checks accrued spending before a call; it is not a strict reservation system for concurrent LLM billing.
- X-User-Id is supplied by the trusted caller of the shared API key; production multi-tenant identity must come from verified credentials.

## CP4

- Redis history, readiness and signal forwarding: 19/19 tests passed.
- Combined CP1/CP3/CP4 regression: 54 passed.
- Added docker-compose.scale.yml to avoid host-port conflicts when scaling three agents.
- History writes/trim/TTL are transactional; Redis connections have bounded timeouts.

## Bonus and extra checks

- GitHub Actions run 36517229712 completed successfully (test + Docker build); deploy was disabled pending Render setup.
- Four additional checks passed: concurrent quota enforcement, budget short-circuit before LLM, blank secret rejection, monthly bucket isolation.
- Local Uvicorn smoke: health/ready 200, authenticated asks saw history lengths 0 and 2.
- Cloud CP5 public URL: https://day12-agent-gu55.onrender.com.
- CP5 rerun: 8 passed, 5 skipped (4 local fallback + optional authenticated request).
- Initial readiness request had a TCP ConnectTimeout; rerun recovered without code changes.
- health.png captures the actual public endpoint; dashboard screenshot is still pending.
- Bonus tests including the live GitHub badge: 13 passed.
- CI run 36517699543 measured single-stage 1,188,388,097 bytes; multi-stage 208,822,946 bytes.

## Final verification (2026-09-29)

- Full suite, including real Docker builds, public Render and live CI badge:
  **95 passed, 5 skipped** in 35.95 seconds. The skips are the four local
  fallback tests and optional cloud-key test; no required test was skipped.
- Unmodified `grade.py`: required checkpoints and exercises total **100/100**.
  Its badge request temporarily failed; the subsequent full suite passed it.
  Automated exercise completion does not replace manual review.
- Local Compose agent and Redis are healthy; runtime UID is 10001.
- Real HTTP smoke: health/ready 200; missing key 401; authenticated requests
  200 with history lengths 0 and 2.
- Three-container experiment: history lengths 0,2,4,6,8,10 across different
  agents. See benchmarks/scale-evidence.txt. Stack restored to one agent.
- Real SIGTERM stop exited 0 and logged service_stopped / Application shutdown
  complete; agent restarted successfully, Redis data retained.
- Source-only rebuild reused dependency layers; benchmarks/cache-build.txt.
- First local CP2 build exceeded 900 seconds downloading dependencies; later
  original CP2 tests passed 16/16. Use PYTHONUTF8=1 on Windows to avoid Docker
  log decoding errors with the default cp1252 subprocess encoding.
- Original grading tests and grade.py unchanged. No .env, virtualenv or
  configured secret value is tracked in Git.
- Remaining manual evidence: screenshots/dashboard.png from the signed-in
  Render dashboard. The cloud authenticated test is optional; set
  DEPLOY_API_KEY locally to enable it.
