import uuid
from contextvars import ContextVar
from typing import Optional

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    SimpleSpanProcessor,
    SpanExporter,
    SpanExportResult,
)
from opentelemetry.sdk.trace.export import ConsoleSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
import os

from app.config import settings

# Context variables to store correlation and transaction IDs
correlation_id: ContextVar[Optional[str]] = ContextVar("correlation_id", default=None)
transaction_id: ContextVar[Optional[str]] = ContextVar("transaction_id", default=None)


def get_correlation_id() -> str:
    """Get the current correlation ID or generate a new one if none exists."""
    current_id = correlation_id.get()
    if current_id is None and settings.TRACING_GENERATE_IF_MISSING:
        current_id = str(uuid.uuid4())
        correlation_id.set(current_id)
    return current_id or ""


def get_transaction_id() -> str:
    """Get the current transaction ID if it exists."""
    return transaction_id.get() or ""


class NoopSpanExporter(SpanExporter):
    def export(self, spans):
        return SpanExportResult.SUCCESS

    def shutdown(self):
        pass


def configure_tracer(app):
    provider = TracerProvider()

    if settings.ENV in ["prod"]:
        processor = BatchSpanProcessor(ConsoleSpanExporter())
    else:
        processor = SimpleSpanProcessor(NoopSpanExporter())

    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)
    FastAPIInstrumentor.instrument_app(app, tracer_provider=provider)


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """Middleware to handle correlation IDs and transaction IDs in requests and responses."""

    async def dispatch(self, request: Request, call_next):
        # Get correlation ID from header or generate new one
        header_name = settings.TRACING_HEADER.lower()
        correlation_id_value = request.headers.get(header_name)

        if correlation_id_value is None and settings.TRACING_GENERATE_IF_MISSING:
            correlation_id_value = str(uuid.uuid4())

        # Set correlation ID in context
        if correlation_id_value:
            correlation_id.set(correlation_id_value)

        # Get transaction ID from header if present
        transaction_header = settings.TRANSACTION_HEADER.lower()
        transaction_id_value = request.headers.get(transaction_header)
        if transaction_id_value:
            transaction_id.set(transaction_id_value)

        # Process the request
        response = await call_next(request)

        # Add correlation ID to response headers
        if correlation_id_value:
            response.headers[settings.TRACING_HEADER] = correlation_id_value

        # Add transaction ID to response headers if present
        if transaction_id_value:
            response.headers[settings.TRANSACTION_HEADER] = transaction_id_value

        return response
