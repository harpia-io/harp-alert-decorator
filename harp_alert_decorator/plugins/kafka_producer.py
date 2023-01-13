from logger.logging import service_logger
import traceback
from prometheus_client import Summary
from confluent_kafka import Producer
import json
import datetime
import harp_alert_decorator.settings as settings
from harp_alert_decorator.plugins.tracer import get_tracer
from opentelemetry.instrumentation.confluent_kafka import ConfluentKafkaInstrumentor

log = service_logger()
tracer_get = get_tracer()
tracer = tracer_get.get_tracer(__name__)
instrumentation = ConfluentKafkaInstrumentor()


class KafkaProduceMessages(object):
    KAFKA_PRODUCER_START = Summary('kafka_confluent_producer_start_latency_seconds', 'Time spent starting Kafka producer')
    KAFKA_PRODUCE_MESSAGES = Summary('kafka_confluent_produce_messages_latency_seconds', 'Time spent processing produce to Kafka')

    def __init__(self):
        self.producer = self.init_producer()

    @staticmethod
    @KAFKA_PRODUCER_START.time()
    def init_producer():
        try:
            producer_config = {
                'bootstrap.servers': settings.KafkaConfig.KAFKA_SERVERS
            }

            producer = Producer(**producer_config)
            producer = instrumentation.instrument_producer(producer)

            return producer
        except Exception as err:
            log.error(
                msg=f"Can`t connect to Kafka cluster - {settings.KafkaConfig.KAFKA_SERVERS}\nError: {err}\nTrace: {traceback.format_exc()}"
            )
            return None

    @staticmethod
    def default_converter(o):
        if isinstance(o, (datetime.date, datetime.datetime)):
            return o.isoformat()

    @staticmethod
    def delivery_report(err, msg):
        """ Called once for each message produced to indicate delivery result.
            Triggered by poll() or flush(). """
        if err is not None:
            log.error('Message delivery failed: {}'.format(err))

    @KAFKA_PRODUCE_MESSAGES.time()
    @tracer.start_as_current_span("Kafka: produce_message")
    def produce_message(self, topic, message):
        try:
            self.producer.produce(
                topic,
                json.dumps(message, default=self.default_converter).encode(),
                callback=self.delivery_report
            )

            self.producer.flush()
        except Exception as err:
            log.error(
                msg=f"Can`t push message to - {topic}\nBody: {message}\nError: {err}\nTrace: {traceback.format_exc()}"
            )
