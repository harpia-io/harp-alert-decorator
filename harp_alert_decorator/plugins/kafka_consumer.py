from logger.logging import service_logger
from harp_alert_decorator.settings import KafkaConfig, SERVICE_NAME
from confluent_kafka import Consumer
import ujson as json
from opentelemetry.instrumentation.confluent_kafka import ConfluentKafkaInstrumentor
from harp_alert_decorator.logic.notification_processor import ConsumeMessages

log = service_logger()


class KafkaConsumeMessages(object):
    def __init__(self, kafka_topic):
        self.kafka_topic = kafka_topic

    def start_consumer(self):
        """
        Start consumer
        """
        instrumentation = ConfluentKafkaInstrumentor()

        consumer = Consumer(
            {
                'bootstrap.servers': KafkaConfig.KAFKA_SERVERS,
                'group.id': SERVICE_NAME,
                'auto.offset.reset': 'latest',
            }
        )
        consumer = instrumentation.instrument_consumer(consumer)

        consumer.subscribe([self.kafka_topic])

        while True:
            msg = consumer.poll(5.0)

            if msg is None:
                continue
            if msg.error():
                log.error(msg=f"Failed to consume message from Kafka: {msg.error()}")
                continue

            parsed_json = json.loads(msg.value().decode('utf-8'))

            log.info(
                msg=f"Consumed message from Kafka\nparsed_json: {parsed_json}",
                extra={"tags": {}}
            )

            ConsumeMessages().start_consumer(parsed_json=parsed_json)

        return consumer
