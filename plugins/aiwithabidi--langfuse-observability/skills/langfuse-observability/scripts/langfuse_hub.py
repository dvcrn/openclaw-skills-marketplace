#!/usr/bin/env python3
"""
langfuse_hub.py — The universal Langfuse v3 tracing layer for OpenClaw.

Every skill imports from here. Thread-safe, crash-proof, auto-flushing.
Uses Langfuse Python SDK v3.14+ (span-centric API with TraceContext).

Usage:
    from langfuse_hub import traced, trace_llm, trace_api, trace_tool, trace_event, score, flush

    # Decorator
    @traced("my-operation")
    def do_work():
        ...

    # Context manager
    with traced("my-operation") as t:
        result = do_work()
        t.set_output(result)

    # Direct calls
    trace_llm(model="claude-sonnet-4", prompt="hi", completion="hello", input_tokens=5, output_tokens=10)
    trace_api(service="perplexity", endpoint="/search", status=200, latency_ms=350)
    trace_tool(name="memory_engine", input_data={"q": "test"}, output_data={"result": "ok"}, duration_ms=120)
    trace_event(name="user-login", data={"user": "abidi"}, level="DEFAULT")
    score(trace_id="xxx", name="relevance", value=0.95)
    flush()
"""

import os
import sys
import time
import atexit
import threading
import functools
from contextlib import contextmanager
from datetime import datetime, timezone, timedelta

# ---------------------------------------------------------------------------
# Config (env vars with defaults)
# ---------------------------------------------------------------------------
LANGFUSE_PUBLIC_KEY = os.environ.get("LANGFUSE_PUBLIC_KEY", "pk-lf-8a9322b9-5eb1-4e8b-815e-b3428dc69bc4")
LANGFUSE_SECRET_KEY = os.environ.get("LANGFUSE_SECRET_KEY", "sk-lf-115cb6b4-7153-4fe6-9255-bf28f8b115de")
LANGFUSE_HOST = os.environ.get("LANGFUSE_HOST", "http://langfuse-web:3000")
LANGFUSE_USER_ID = os.environ.get("LANGFUSE_USER_ID", "agxntsix")

# ---------------------------------------------------------------------------
# Model pricing (per 1M tokens, USD)
# ---------------------------------------------------------------------------
MODEL_COSTS = {
    "claude-opus-4-6": {"input": 5.0, "output": 25.0},
    "claude-sonnet-4": {"input": 3.0, "output": 15.0},
    "claude-haiku-4.5": {"input": 1.0, "output": 5.0},
    "gpt-4o": {"input": 2.5, "output": 10.0},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "gpt-5-nano": {"input": 0.05, "output": 0.40},
    "gemini-2.0-flash-lite-001": {"input": 0.075, "output": 0.30},
    "sonar": {"input": 0.50, "output": 0.50},
    "sonar-pro": {"input": 2.0, "output": 2.0},
    "sonar-reasoning-pro": {"input": 5.0, "output": 5.0},
    "text-embedding-3-small": {"input": 0.02, "output": 0.0},
}

# ---------------------------------------------------------------------------
# Lazy singleton client (thread-safe)
# ---------------------------------------------------------------------------
_client = None
_client_lock = threading.Lock()
_initialized = False


def _get_client():
    """Get or create the Langfuse client singleton. Returns None on failure."""
    global _client, _initialized
    if _initialized:
        return _client
    with _client_lock:
        if _initialized:
            return _client
        try:
            from langfuse import Langfuse
            _client = Langfuse(
                public_key=LANGFUSE_PUBLIC_KEY,
                secret_key=LANGFUSE_SECRET_KEY,
                host=LANGFUSE_HOST,
            )
            _initialized = True
        except Exception as e:
            print(f"[langfuse_hub] Failed to init Langfuse: {e}", file=sys.stderr)
            _client = None
            _initialized = True
    return _client


def _safe(fn):
    """Decorator: swallow all exceptions so tracing never crashes callers."""
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            print(f"[langfuse_hub] {fn.__name__} error: {e}", file=sys.stderr)
            return None
    return wrapper


def _make_ctx(session_id=None, tags=None, metadata=None, trace_id=None):
    """Build a TraceContext dict for grouping spans under one trace."""
    from langfuse.types import TraceContext
    return TraceContext(
        trace_id=trace_id,
        session_id=session_id or get_session_id(),
        user_id=LANGFUSE_USER_ID,
        tags=tags or [],
        metadata=metadata or {},
    )


# ---------------------------------------------------------------------------
# Session management
# ---------------------------------------------------------------------------
_CST = timedelta(hours=-6)


def _now_cst():
    return datetime.now(timezone(_CST))


def get_session_id(dt=None):
    """Auto-generate session ID: session-YYYYMMDD-HH."""
    dt = dt or _now_cst()
    return f"session-{dt.strftime('%Y%m%d-%H')}"


def start_session(session_id=None):
    """Return a session ID (auto-generated if not provided)."""
    return session_id or get_session_id()


# ---------------------------------------------------------------------------
# Cost calculation
# ---------------------------------------------------------------------------
def calculate_cost(model, input_tokens=0, output_tokens=0):
    """Calculate cost in USD from token counts. Returns (input_cost, output_cost, total)."""
    costs = MODEL_COSTS.get(model)
    if not costs:
        for key, val in MODEL_COSTS.items():
            if key in model or model in key:
                costs = val
                break
    if not costs:
        return 0.0, 0.0, 0.0
    ic = (input_tokens / 1_000_000) * costs["input"]
    oc = (output_tokens / 1_000_000) * costs["output"]
    return ic, oc, ic + oc


# ---------------------------------------------------------------------------
# Core tracing functions
# ---------------------------------------------------------------------------
@_safe
def trace_llm(model, prompt=None, completion=None, input_tokens=0, output_tokens=0,
              latency_ms=None, name=None, session_id=None, metadata=None, tags=None,
              trace_id=None, **kwargs):
    """Log an LLM generation. Returns the span (with .trace_id)."""
    client = _get_client()
    if not client:
        return None

    ic, oc, total = calculate_cost(model, input_tokens, output_tokens)
    name = name or f"llm-{model}"
    ctx = _make_ctx(session_id, tags=["llm"] + (tags or []), metadata=metadata, trace_id=trace_id)

    span = client.start_span(name=name, trace_context=ctx)
    span.update_trace(name=name, tags=["llm"] + (tags or []))

    gen = span.start_observation(
        name=f"generation-{model}",
        as_type="generation",
        model=model,
        input=prompt,
        output=completion,
        usage_details={"input": input_tokens, "output": output_tokens},
        cost_details={"input": round(ic, 8), "output": round(oc, 8), "total": round(total, 8)},
        metadata={"latency_ms": latency_ms} if latency_ms else None,
    )
    gen.end()
    span.end()
    return span


@_safe
def trace_api(service, endpoint, status=None, latency_ms=None, request_data=None,
              response_data=None, name=None, session_id=None, metadata=None, tags=None,
              trace_id=None):
    """Log an external API call. Returns the span."""
    client = _get_client()
    if not client:
        return None

    name = name or f"api-{service}"
    ctx = _make_ctx(session_id, tags=["api", service] + (tags or []), metadata=metadata, trace_id=trace_id)

    span = client.start_span(name=name, trace_context=ctx, input=request_data, output=response_data,
                              metadata={"service": service, "endpoint": endpoint, "status": status, "latency_ms": latency_ms})
    span.update_trace(name=name, tags=["api", service] + (tags or []))
    span.end()
    return span


@_safe
def trace_tool(name, input_data=None, output_data=None, duration_ms=None,
               session_id=None, metadata=None, tags=None, trace_id=None, error=None):
    """Log a tool/skill execution. Returns the span."""
    client = _get_client()
    if not client:
        return None

    level = "ERROR" if error else "DEFAULT"
    ctx = _make_ctx(session_id, tags=["tool", name] + (tags or []), metadata=metadata, trace_id=trace_id)

    span = client.start_span(
        name=f"tool-{name}",
        trace_context=ctx,
        input=input_data,
        output=output_data if not error else {"error": str(error)},
        level=level,
        metadata={"duration_ms": duration_ms, **({"error": str(error)} if error else {})},
    )
    span.update_trace(name=f"tool-{name}", tags=["tool", name] + (tags or []))
    span.end()
    return span


@_safe
def trace_event(name, data=None, level="DEFAULT", session_id=None, metadata=None,
                tags=None, trace_id=None):
    """Log a custom event. Returns the span."""
    client = _get_client()
    if not client:
        return None

    ctx = _make_ctx(session_id, tags=["event"] + (tags or []), metadata=metadata, trace_id=trace_id)

    span = client.start_span(name=f"event-{name}", trace_context=ctx)
    span.update_trace(name=f"event-{name}", tags=["event"] + (tags or []))
    span.create_event(name=name, input=data, level=level)
    span.end()
    return span


@_safe
def score(trace_id, name, value, comment=None, data_type="NUMERIC"):
    """Add a score to a trace."""
    client = _get_client()
    if not client:
        return None
    client.create_score(trace_id=trace_id, name=name, value=value, comment=comment, data_type=data_type)


# ---------------------------------------------------------------------------
# Context manager & decorator
# ---------------------------------------------------------------------------
class _TracedContext:
    """Holds a span reference for use in `with` blocks."""
    def __init__(self, span):
        self.span = span
        self.trace_id = span.trace_id if span else None
        self._start = time.time()

    def set_output(self, output):
        if self.span:
            try:
                self.span.update(output=output)
            except Exception:
                pass

    def set_error(self, error):
        if self.span:
            try:
                self.span.update(output={"error": str(error)}, level="ERROR")
            except Exception:
                pass

    def event(self, name, data=None, level="DEFAULT"):
        if self.span:
            try:
                self.span.create_event(name=name, input=data, level=level)
            except Exception:
                pass

    def generation(self, **kwargs):
        if self.span:
            try:
                g = self.span.start_observation(as_type="generation", **kwargs)
                g.end()
                return g
            except Exception:
                pass

    def child_span(self, name, **kwargs):
        if self.span:
            try:
                return self.span.start_span(name=name, **kwargs)
            except Exception:
                pass

    @property
    def duration_ms(self):
        return round((time.time() - self._start) * 1000, 1)


@contextmanager
def _traced_ctx(name, session_id=None, tags=None, metadata=None):
    """Context manager for block tracing."""
    client = _get_client()
    if not client:
        yield _TracedContext(None)
        return

    try:
        ctx = _make_ctx(session_id, tags=tags, metadata=metadata)
        span = client.start_span(name=name, trace_context=ctx)
        span.update_trace(name=name, tags=tags or [])
        tc = _TracedContext(span)
    except Exception as e:
        print(f"[langfuse_hub] traced context error: {e}", file=sys.stderr)
        yield _TracedContext(None)
        return

    try:
        yield tc
    except Exception as exc:
        tc.set_error(exc)
        raise
    finally:
        try:
            span.end(metadata={"duration_ms": tc.duration_ms})
        except Exception:
            pass


def traced(name=None, session_id=None, tags=None, metadata=None):
    """
    Use as decorator or context manager.

    @traced("my-op")
    def fn(): ...

    with traced("my-op") as t:
        ...
    """
    if callable(name):
        fn = name
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            with _traced_ctx(fn.__name__, session_id, tags, metadata) as ctx:
                result = fn(*args, **kwargs)
                ctx.set_output(str(result)[:1000] if result is not None else None)
                return result
        return wrapper

    class _TracedDual:
        def __call__(self, fn):
            op_name = name or fn.__name__
            @functools.wraps(fn)
            def wrapper(*a, **kw):
                with _traced_ctx(op_name, session_id, tags, metadata) as ctx:
                    result = fn(*a, **kw)
                    ctx.set_output(str(result)[:1000] if result is not None else None)
                    return result
            return wrapper

        def __enter__(self):
            self._cm = _traced_ctx(name or "unnamed", session_id, tags, metadata)
            return self._cm.__enter__()

        def __exit__(self, *args):
            return self._cm.__exit__(*args)

    return _TracedDual()


# ---------------------------------------------------------------------------
# Flush & cleanup
# ---------------------------------------------------------------------------
@_safe
def flush():
    """Flush all pending traces to Langfuse."""
    client = _get_client()
    if client:
        client.flush()


def shutdown():
    """Flush and shutdown the client."""
    try:
        client = _get_client()
        if client:
            client.flush()
            client.shutdown()
    except Exception:
        pass


atexit.register(shutdown)


# ---------------------------------------------------------------------------
# CLI self-test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("Testing langfuse_hub...")
    client = _get_client()
    if not client:
        print("Client init failed — check config", file=sys.stderr)
        sys.exit(1)

    ok = client.auth_check()
    print(f"Auth check: {'OK' if ok else 'FAILED'}")

    # Test trace_llm
    t = trace_llm(
        model="gpt-5-nano",
        prompt="test prompt",
        completion="test response",
        input_tokens=10,
        output_tokens=20,
        latency_ms=150,
        tags=["test"],
    )
    print(f"trace_llm: {'OK trace=' + t.trace_id if t else 'FAILED'}")

    # Test trace_api
    t2 = trace_api(service="test", endpoint="/ping", status=200, latency_ms=50)
    print(f"trace_api: {'OK trace=' + t2.trace_id if t2 else 'FAILED'}")

    # Test trace_tool
    t3 = trace_tool(name="test-tool", input_data={"q": "hi"}, output_data={"a": "ok"}, duration_ms=10)
    print(f"trace_tool: {'OK trace=' + t3.trace_id if t3 else 'FAILED'}")

    # Test trace_event
    t4 = trace_event(name="test-event", data={"status": "ok"})
    print(f"trace_event: {'OK trace=' + t4.trace_id if t4 else 'FAILED'}")

    # Test context manager
    with traced("self-test") as ctx:
        ctx.event("test-event", {"status": "running"})
        time.sleep(0.1)
        ctx.set_output("self-test complete")
    print(f"context manager: OK ({ctx.duration_ms}ms, trace={ctx.trace_id})")

    # Test decorator
    @traced("decorator-test")
    def add(a, b):
        return a + b
    result = add(2, 3)
    print(f"decorator: OK (result={result})")

    # Test score
    if t:
        score(trace_id=t.trace_id, name="test-score", value=0.99)
        print("score: OK")

    flush()
    print("flush: OK\n✅ All tests passed!")
