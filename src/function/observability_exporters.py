import logging
from typing import Optional

from azure.monitor.opentelemetry.exporter import (ApplicationInsightsSampler,
                                                  AzureMonitorLogExporter,
                                                  AzureMonitorMetricExporter,
                                                  AzureMonitorTraceExporter)
from opentelemetry import _logs, metrics, trace
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.semconv.resource import ResourceAttributes


def setup_telemetry_export(
    service_name: str,
    service_instance_id: str,
    service_version: str,
    logger: logging.Logger,
    application_insights_connection_string: Optional[str] = None,
) -> None:

    resource = Resource(
        attributes={
            ResourceAttributes.SERVICE_NAME: service_name,
            ResourceAttributes.SERVICE_INSTANCE_ID: service_instance_id,
            ResourceAttributes.SERVICE_VERSION: service_version,
        }
    )

    sampler = ApplicationInsightsSampler(sampling_ratio=1)

    # Tracing
    tracing_span_processor = BatchSpanProcessor(
        AzureMonitorTraceExporter(
            connection_string=application_insights_connection_string,
        )
    )
    trace_provider = TracerProvider(sampler=sampler, resource=resource)
    trace.set_tracer_provider(trace_provider)
    if tracing_span_processor:
        trace_provider.add_span_processor(tracing_span_processor)

    # Metrics
    metric_exporter = AzureMonitorMetricExporter(
        connection_string=application_insights_connection_string
    )
    metrics_reader = PeriodicExportingMetricReader(metric_exporter)
    meter_provider = MeterProvider(metric_readers=[metrics_reader], resource=resource)
    metrics.set_meter_provider(meter_provider)

    # Logging
    log_record_processor = BatchLogRecordProcessor(
        AzureMonitorLogExporter(
            connection_string=application_insights_connection_string
        )
    )

    if logger.hasHandlers():
        logger.warning("Clearing existing handlers from logger")
        logger.handlers.clear()

    logger_provider = LoggerProvider(resource=resource)
    _logs.set_logger_provider(logger_provider)

    # Get logger provider from opentelemetry sdk (required to configure logging handler)
    if log_record_processor:
        logger_provider.add_log_record_processor(log_record_processor)

    # Add the handler to the root logger
    # This will allow logs to be captured by the Azure Monitor Log Exporter
    handler = LoggingHandler(logger_provider=_logs.get_logger_provider())

    logger.addHandler(handler)
