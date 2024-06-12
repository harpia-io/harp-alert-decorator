import os

# Flask settings
URL_PREFIX = os.getenv('URL_PREFIX', '/api/v1')
SERVICE_NAMESPACE = os.getenv('SERVICE_NAMESPACE', 'dev')
POD_NAME = os.getenv('POD_NAME', '')
RUNNING_ON = os.getenv('RUNNING_ON', 'kubernetes')

# Logging
SERVICE_NAME = os.getenv('SERVICE_NAME', 'harp-alert-decorator')
LOG_LEVEL = "DEBUG"
OPENSEARCH_SERVER = os.getenv('OPENSEARCH_SERVER', 'opensearch-ingest-hl.opensearch.svc.cluster.local')
OPENSEARCH_PORT = os.getenv('OPENSEARCH_PORT', 9200)
ENVIRONMENT = os.getenv('ENVIRONMENT', 'dev')


class KafkaConfig:
    NOTIFICATIONS_TOPIC = os.getenv('NOTIFICATIONS_TOPIC', 'dev_harp-notifications-v2')
    NOTIFICATIONS_DECORATED_TOPIC = os.getenv('NOTIFICATIONS_DECORATED_TOPIC', 'dev_harp-notifications-decorated-v2')
    KAFKA_SERVERS = os.getenv('KAFKA_SERVERS', '127.0.0.1:9092')


class VictoriaMetricsConfig:
    VM_URL_WRITE = os.getenv('VM_URL_WRITE', '')


class TracingConfig:
    TEMPO_URL = os.getenv('TEMPO_URL', '')


class ServiceConfig:
    ENVIRONMENTS_HOST = os.getenv('ENVIRONMENTS_HOST', '')
    SCENARIOS_HOST = os.getenv('SCENARIOS_HOST', '')
    INTEGRATIONS_HOST = os.getenv('INTEGRATIONS_HOST', '')
    UNASSIGNED_ENV_ID = int(os.getenv('UNASSIGNED_ENV_ID', 1))
    UNASSIGNED_SCENARIO_ID = int(os.getenv('UNASSIGNED_SCENARIO_ID', 1))
    REQUESTS_CACHE_EXPIRE_SECONDS = int(os.getenv('REQUESTS_CACHE_EXPIRE_SECONDS', 60))

