from logger.logging import service_logger
import traceback
from fastapi import APIRouter, HTTPException
import harp_alert_decorator.settings as settings
from harp_alert_decorator.plugins.kafka_consumer import KafkaConsumeMessages
import threading

log = service_logger()

router = APIRouter(prefix=settings.URL_PREFIX)


def process_message():
    kafka_process_message = KafkaConsumeMessages(kafka_topic=settings.KafkaConfig.NOTIFICATIONS_TOPIC)
    kafka_process_message.start_consumer()


@router.on_event("startup")
def init_consumer():
    t1 = threading.Thread(target=process_message, name='process_message', daemon=True)
    t1.start()
