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
