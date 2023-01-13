from prometheus_client import Gauge, Counter, Summary, Histogram


class Prom:
    ENVIRONMENT_DECORATOR = Summary('environment_decorator_latency_seconds', 'Time spent processing environment events')
    SCENARIO_DECORATOR = Summary('scenario_decorator_latency_seconds', 'Time spent processing scenario events')
    INTEGRATION_DECORATOR = Summary('integration_decorator_latency_seconds', 'Time spent processing integration events')
    TOTAL_DECORATOR = Summary('total_decorator_latency_seconds', 'Time spent processing total events')
