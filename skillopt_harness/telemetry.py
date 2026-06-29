from __future__ import annotations

import os
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

_ENABLED_VALUES = {"1", "true", "yes"}
_CONFIGURED = False
_CONFIGURE_FAILED = False


class _NoopSpan:
    def set_attribute(self, _key: str, _value: Any) -> None:
        return None

    def add_event(self, _name: str, _attributes: dict[str, Any] | None = None) -> None:
        return None


def configure_telemetry() -> None:
    global _CONFIGURED, _CONFIGURE_FAILED
    if not is_enabled() or _CONFIGURED or _CONFIGURE_FAILED:
        return

    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
    except ImportError:
        _CONFIGURE_FAILED = True
        return

    try:
        service_name = os.getenv("OTEL_SERVICE_NAME", "skillopt-harness")
        provider = TracerProvider(resource=Resource.create({"service.name": service_name}))
        provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
        trace.set_tracer_provider(provider)
        _CONFIGURED = True
    except Exception:
        _CONFIGURE_FAILED = True


def is_enabled() -> bool:
    return os.getenv("SKILLOPT_OTEL_ENABLED", "").strip().lower() in _ENABLED_VALUES


def get_tracer(name: str = "skillopt_harness") -> Any:
    if not is_enabled():
        return _NoopTracer()
    configure_telemetry()
    try:
        from opentelemetry import trace
    except ImportError:
        return _NoopTracer()
    if _CONFIGURE_FAILED:
        return _NoopTracer()
    return trace.get_tracer(name)


@contextmanager
def start_span(name: str, attributes: dict[str, Any] | None = None) -> Iterator[Any]:
    if not is_enabled():
        yield _NoopSpan()
        return

    tracer = get_tracer()
    try:
        span_context = tracer.start_as_current_span(name)
        span = span_context.__enter__()
    except Exception:
        yield _NoopSpan()
        return

    try:
        if attributes:
            set_attributes(span, attributes)
        yield span
    finally:
        try:
            span_context.__exit__(*sys.exc_info())
        except Exception:
            pass


def set_attributes(span: Any, attributes: dict[str, Any]) -> None:
    for key, value in _sanitize_attributes(attributes).items():
        try:
            span.set_attribute(key, value)
        except Exception:
            continue


def add_event(span: Any, name: str, attributes: dict[str, Any] | None = None) -> None:
    try:
        span.add_event(name, _sanitize_attributes(attributes or {}))
    except Exception:
        return


class _NoopTracer:
    @contextmanager
    def start_as_current_span(self, _name: str) -> Iterator[_NoopSpan]:
        yield _NoopSpan()


def _sanitize_attributes(attributes: dict[str, Any]) -> dict[str, str | bool | int | float]:
    sanitized: dict[str, str | bool | int | float] = {}
    for key, value in attributes.items():
        if value is None:
            continue
        if isinstance(value, Path):
            sanitized[key] = str(value)
            continue
        if isinstance(value, str | bool | int | float):
            sanitized[key] = value
    return sanitized
