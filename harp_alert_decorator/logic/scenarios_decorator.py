from logger.logging import service_logger
import harp_alert_decorator.settings as settings
import requests
import requests_cache
import traceback
from harp_alert_decorator.plugins.tracer import get_tracer

logger = service_logger()
tracer_get = get_tracer()
tracer = tracer_get.get_tracer(__name__)

requests_cache.install_cache(cache_name='cache_environments_decorator', backend='memory', expire_after=settings.ServiceConfig.REQUESTS_CACHE_EXPIRE_SECONDS, allowable_methods='GET')


class ScenariosDecorator(object):
    def __init__(self, notification):
        self.notification = notification
        self.unassigned_scenario_id = settings.ServiceConfig.UNASSIGNED_SCENARIO_ID

    @tracer.start_as_current_span("get_scenario_by_name")
    def get_scenario_by_name(self, scenario_name):
        url = f"{settings.ServiceConfig.SCENARIOS_HOST}/{scenario_name}"
        try:
            req = requests.get(
                url=url,
                headers={"Accept": "application/json", "Content-Type": "application/json"},
                timeout=10
            )
            if req.status_code == 200:
                return req.json()['msg']
            elif req.status_code == 404:
                return None
            else:
                logger.error(
                    msg=f"Can`t connect to Scenario service to get Scenario by Name",
                    extra={'tags': {}}
                )
                exit()
        except Exception as err:
            logger.error(
                msg=f"Error: {err}, stack: {traceback.format_exc()}",
                extra={'tags': {}}
            )
            exit()

    @tracer.start_as_current_span("get_scenario_by_id")
    def get_scenario_by_id(self, scenario_id):
        url = f"{settings.ServiceConfig.SCENARIOS_HOST}/{int(scenario_id)}"
        try:
            req = requests.get(
                url=url,
                headers={"Accept": "application/json", "Content-Type": "application/json"},
                timeout=10
            )
            if req.status_code == 200:
                logger.debug(
                    msg=f"Requested Scenario by ID - {scenario_id}\nReceived response: {req.json()}",
                    extra={'tags': {}}
                )
                return req.json()['msg']
            elif req.status_code == 404:
                logger.debug(
                    msg=f"Requested Scenario by ID is not found - {scenario_id}\nReceived response: {req.json()}",
                    extra={'tags': {}}
                )
                return None
            else:
                logger.error(
                    msg=f"Can`t connect to Scenario service to get Scenario by ID - {int(scenario_id)}\nStatus code: {req.status_code}\nJSON: {req.json()}",
                    extra={'tags': {}}
                )
                return None
        except Exception as err:
            logger.error(
                msg=f"Error: {err}, stack: {traceback.format_exc()}",
                extra={'tags': {}}
            )
            return None

    @tracer.start_as_current_span("main")
    def main(self):
        if 'procedure_id' in self.notification:
            if self.notification['procedure_id'] is None:
                logger.debug(
                    msg=f"Scenario is present in notification but it`s {self.notification['procedure_id']}. Logic to apply default scenario will be applied",
                    extra={'tags': {}}
                )
                self.notification['procedure'] = self.get_scenario_by_id(scenario_id=self.unassigned_scenario_id)
                self.notification['procedure_id'] = self.unassigned_scenario_id
            elif isinstance(self.notification['procedure_id'], str):
                logger.debug(
                    msg=f"Scenario field contain name of the scenario - {self.notification['procedure_id']}",
                    extra={'tags': {}}
                )
                scenario_body = self.get_scenario_by_name(scenario_name=self.notification['procedure_id'])
                if scenario_body:
                    self.notification['procedure'] = scenario_body
                    self.notification['procedure_id'] = self.notification['scenario_id']
                else:
                    self.notification['procedure'] = self.get_scenario_by_id(scenario_id=self.unassigned_scenario_id)
                    self.notification['procedure_id'] = self.unassigned_scenario_id
            else:
                logger.debug(
                    msg=f"Scenario field already contain identifier - {self.notification['procedure_id']}",
                    extra={'tags': {}}
                )
                scenario_body = self.get_scenario_by_id(scenario_id=self.notification['procedure_id'])
                if scenario_body:
                    self.notification['procedure'] = scenario_body
                else:
                    logger.error(
                        msg=f"Scenario with ID - {self.notification['procedure_id']} not found. Default scenario will be applied",
                        extra={'tags': {
                            'event_id': self.notification['event_id']
                        }}
                    )
                    self.notification['procedure'] = self.get_scenario_by_id(scenario_id=self.unassigned_scenario_id)
                    self.notification['procedure_id'] = self.unassigned_scenario_id
        else:
            logger.warning(
                msg=f"Scenario field was not detected in message from collector.\nJSON: {self.notification}",
                extra={'tags': {
                    'event_id': self.notification['event_id']
                }}
            )
            self.notification['procedure'] = self.get_scenario_by_id(scenario_id=self.unassigned_scenario_id)
            self.notification['procedure_id'] = self.unassigned_scenario_id

        return self.notification
