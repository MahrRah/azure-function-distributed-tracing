import logging
from typing import Optional, Sequence
from opentelemetry.context import Context
from opentelemetry.trace import SpanContext
from opentelemetry.sdk.trace.sampling import (
    Decision,
    Sampler,
    SamplingResult,
    _get_parent_trace_state,
)
from opentelemetry.util.types import Attributes
from opentelemetry.trace import Link, SpanKind, format_trace_id
from opentelemetry.trace.span import TraceState

logger = logging.getLogger(__name__)


class CustomFilterSampler(Sampler):
    def should_sample(
        self,
        parent_context: Optional[Context],
        trace_id: int,
        name: str,
        kind: Optional[SpanKind] = None,
        attributes: Attributes = None,
        links: Optional[Sequence["Link"]] = None,
        trace_state: Optional["TraceState"] = None,
    ) -> "SamplingResult":

        foo = 8  # some custom logic
        logger.info(
            f"CustomFilterSampler: should_sample parent context: {parent_context}"
        )
        return SamplingResult(
            decision=Decision.RECORD_AND_SAMPLE,
            attributes=attributes,
            trace_state=_get_parent_trace_state(parent_context),  # type: ignore
        )

    def get_description(self) -> str:
        pass
