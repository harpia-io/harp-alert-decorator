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


class EnvironmentsDecorator(object):
    def __init__(self, notification):
        self.notification = notification
        self.unassigned_env_id = settings.ServiceConfig.UNASSIGNED_ENV_ID

    @tracer.start_as_current_span("get_env_id_by_name")
    def get_env_id_by_name(self, env_name):
        url = f"{settings.ServiceConfig.ENVIRONMENTS_HOST}/{env_name}"
        try:
            req = requests.get(
                url=url,
                headers={"Accept": "application/json", "Content-Type": "application/json"},
                timeout=10
            )
            if req.status_code == 200:
                logger.debug(
                    msg=f"Requested Environment ID by name - {env_name}\nReceived response: {req.json()}",
                    extra={'tags': {}}
                )
                return req.json()['msg']['id']
            else:
                logger.error(
                    msg=f"Can`t connect to Env service to get Env ID by Name",
                    extra={'tags': {}}
                )
        except Exception as err:
            logger.error(
                msg=f"Error: {err}, stack: {traceback.format_exc()}",
                extra={'tags': {}}
            )
            return None

    @tracer.start_as_current_span("main")
    def main(self):
        logger.debug(
            msg=f"Start decorating input event\nJSON: {self.notification}",
            extra={'tags': {}}
        )
        if 'studio' in self.notification:
            if self.notification['studio'] is None:
                logger.debug(
                    msg=f"studio is present in notification but it`s {self.notification['studio']}. Logic to apply scenario id will be applied",
                    extra={'tags': {}}
                )
                self.notification['studio'] = self.unassigned_env_id
            elif isinstance(self.notification['studio'], str):
                logger.debug(
                    msg=f"studio field contain name of the studio and it will be transformed to ID - {self.notification['studio']}",
                    extra={'tags': {}}
                )
                env_id = self.get_env_id_by_name(env_name=self.notification['studio'])
                if env_id:
                    self.notification['studio'] = env_id
                else:
                    self.notification['studio'] = self.unassigned_env_id
            else:
                logger.debug(
                    msg=f"studio field already contain studio_id - {self.notification['studio']}. Nothing will be changed",
                    extra={'tags': {}}
                )
        else:
            logger.warning(
                msg=f"studio field was not detected in message from collector. It will be added to notification.\nJSON: {self.notification}",
                extra={'tags': {}}
            )

            self.notification['studio'] = self.unassigned_env_id

        return self.notification
