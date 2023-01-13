from logger.logging import service_logger
import harp_alert_decorator.settings as settings
from harp_alert_decorator.logic.environments_decorator import EnvironmentsDecorator
from harp_alert_decorator.logic.scenarios_decorator import ScenariosDecorator
import requests
import traceback
import requests_cache
from harp_alert_decorator.plugins.kafka_producer import KafkaProduceMessages
from harp_alert_decorator.plugins.tracer import get_tracer

logger = service_logger()
tracer_get = get_tracer()
tracer = tracer_get.get_tracer(__name__)

producer = KafkaProduceMessages()
requests_cache.install_cache(cache_name='cache_environments_decorator', backend='memory', expire_after=settings.ServiceConfig.REQUESTS_CACHE_EXPIRE_SECONDS, allowable_methods='GET')


class ConsumeMessages(object):
    def __init__(self):
        pass

    @staticmethod
    @tracer.start_as_current_span("get_env_and_scenario_by_key")
    def get_env_and_scenario_by_key(parsed_json):
        url = f"{settings.ServiceConfig.INTEGRATIONS_HOST}/configured/integration_key/{parsed_json['integration_key']}"
        try:
            req = requests.get(
                url=url,
                headers={"Accept": "application/json", "Content-Type": "application/json"},
                timeout=10
            )
            if req.status_code == 200:
                return req.json()['config']
            else:
                logger.error(
                    msg=f"Can`t collect info from Integrations service - {url} to get Env ID and Scenario ID by Integration key\n"
                        f"Response: {req.json()}"
                )
        except Exception as err:
            logger.error(
                msg=f"Error: {err}, stack: {traceback.format_exc()}",
                extra={'tags': {
                    'event_id': parsed_json['event_id']
                }}
            )
            return None

    @tracer.start_as_current_span("decorate_integrations")
    def decorate_integrations(self, parsed_json):
        config = self.get_env_and_scenario_by_key(parsed_json)
        parsed_json['studio'] = config['environment_id']
        parsed_json['procedure_id'] = config['scenario_id']

        return parsed_json

    @staticmethod
    @tracer.start_as_current_span("environments_decorator")
    def environments_decorator(parsed_json):
        event = EnvironmentsDecorator(notification=parsed_json)
        return event.main()

    @staticmethod
    @tracer.start_as_current_span("scenarios_decorator")
    def scenarios_decorator(parsed_json):
        event = ScenariosDecorator(notification=parsed_json)
        return event.main()

    @tracer.start_as_current_span("general_decorator")
    def general_decorator(self, parsed_json):
        environments_message = self.environments_decorator(parsed_json)
        scenarios_message = self.scenarios_decorator(environments_message)

        producer.produce_message(
            topic=settings.KafkaConfig.NOTIFICATIONS_DECORATED_TOPIC,
            message=scenarios_message
        )

    @tracer.start_as_current_span("start_consumer")
    def start_consumer(self, parsed_json):
        """
        Start metrics consumer
        """

        if parsed_json['integration_key']:
            parsed_json = self.decorate_integrations(parsed_json)

        self.general_decorator(parsed_json)


