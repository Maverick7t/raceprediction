"""
app/core/sentry.py
 
Sentry initialisation — called once at process startup.
 
Rules:
  - Sentry is only active when SENTRY_DSN is set.
  - In dev (ENVIRONMENT=dev) or if DSN is absent, this is a no-op.
  - Call init_sentry() from main.py (API) and from each Prefect flow entrypoint.
  - Never import sentry_sdk directly outside this module — centralise all SDK
    calls here so disabling Sentry in tests is a single monkeypatch.
 
Usage:
    from app.core.sentry import init_sentry, capture_exception
    init_sentry()                     # at startup
    capture_exception(exc)            # in except blocks where you want manual capture
"""
 
from __future__ import annotations
 
import logging
 
logger = logging.getLogger(__name__)
 
_initialised = False
 
 
def init_sentry() -> None:
    """
    Initialise the Sentry SDK.
    Safe to call multiple times — subsequent calls are no-ops.
    """
    global _initialised
    if _initialised:
        return
 
    try:
        from app.core.config import config
    except Exception:
        return  # config not available — skip silently
 
    dsn = config.SENTRY_DSN
    if not dsn:
        logger.info("Sentry DSN not set — error tracking disabled")
        return
 
    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
        from sentry_sdk.integrations.logging import LoggingIntegration
 
        sentry_logging = LoggingIntegration(
            level=logging.WARNING,        # breadcrumbs from WARNING+
            event_level=logging.ERROR,    # send ERROR+ as Sentry events
        )
 
        sentry_sdk.init(
            dsn=dsn,
            environment=config.ENVIRONMENT,
            integrations=[
                FastApiIntegration(transaction_style="endpoint"),
                SqlalchemyIntegration(),
                sentry_logging,
            ],
            # Capture 100% of transactions in dev; tune down in prod if volume is high
            traces_sample_rate=1.0 if not config.is_production else 0.1,
            # Never send PII
            send_default_pii=False,
            # Attach request data to every event
            max_breadcrumbs=50,
        )
        _initialised = True
        logger.info(
            f"Sentry initialised environment={config.ENVIRONMENT} dsn_prefix={dsn[:20]}..."
        )
 
    except ImportError:
        logger.warning(
            "sentry-sdk not installed — install it with: pip install sentry-sdk[fastapi]"
        )
    except Exception as exc:
        # Sentry init failure must never crash the application
        logger.error(f"Sentry init failed (non-fatal): {exc}")

        def capture_exception(exc: Exception, **extra: object) -> None:
    """
    Manually capture an exception to Sentry with optional extra context.
    No-op if Sentry is not initialised.
 
    Usage:
        try:
            risky_operation()
        except SomeError as e:
            capture_exception(e, race_key=race_key, driver=driver_code)
            raise
    """
    if not _initialised:
        return
    try:
        import sentry_sdk
        with sentry_sdk.push_scope() as scope:
            for key, value in extra.items():
                scope.set_extra(key, value)
            sentry_sdk.capture_exception(exc)
    except Exception:
        pass  # Sentry capture must never propagate
 
 
def set_sentry_context(race_key: str | None = None, flow_name: str | None = None) -> None:
    """
    Tag the current Sentry scope with pipeline context.
    Call at the start of a Prefect flow or API request handler for richer error context.
    """
    if not _initialised:
        return
    try:
        import sentry_sdk
        if race_key:
            sentry_sdk.set_tag("race_key", race_key)
        if flow_name:
            sentry_sdk.set_tag("flow", flow_name)
    except Exception:
        pass