import os

from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (BatchSpanProcessor,
                                            ConsoleSpanExporter,
                                            SimpleSpanProcessor, SpanExporter,
                                            SpanExportResult)

from app.core.config import settings


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
