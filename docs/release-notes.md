# Release Notes

## V0.1 Working Baseline

- Created the first local end-to-end payments fraud feature store and MLOps pipeline.
- Added synthetic data generation, quality validation, DuckDB feature store, model training, scoring, alerts, monitoring, API, dashboard, tests, Docker, and CI.

## V0.2 Evidence Hardening

- Added fraud pattern detection evidence against injected manifests.
- Added data quality detection evidence against injected quality issues.
- Added point-in-time feature validation outputs.
- Hardened feature store quality reporting.
- Expanded model scorecard, model registry, and model card.
- Added reason-code coverage and alert queue quality reports.
- Added monitoring scorecard with drift severity.
- Improved API and dashboard demo outputs.
- Expanded test coverage to 61 passing tests.

## V0.2 Warning Cleanup

- Replaced deprecated pandas lowercase day-frequency strings with uppercase `D` where used as time windows.
- Replaced `pd.Timestamp.utcnow()` with `pd.Timestamp.now("UTC")`.
- Removed pandas downcasting warnings from feature fallback calculations.
- Confirmed pipeline, pytest, and ruff still pass with no pytest warning summary.

## V0.3 Showcase Polish

- Reworked README for public portfolio review.
- Added recruiter-friendly evidence and MLOps lifecycle explanations.
- Added screenshot capture guidance for key dashboard sections.
- Strengthened the three-minute demo script.
- Added GitHub profile setup and fresh-clone validation docs.
- Refined recruiter summary, technical deep dive, and LinkedIn drafts.
- Preserved the working V0.2 code path and validation expectations.
