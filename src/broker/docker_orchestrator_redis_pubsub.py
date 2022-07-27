import json
import os

from redis.client import Redis

from src.broker.base_consumer_messages import BaseConsumerMessages


class DockerOrchestratorRedisPubsub(BaseConsumerMessages):

    def __init__(self):
        super().__init__()

        self.redis_client = Redis(
            host=os.environ['REDIS_ADDRESS'] if 'REDIS_ADDRESS' in os.environ else 'localhost',
            port=int(os.environ['REDIS_PORT'] if 'REDIS_PORT' in os.environ else 6379),
            db=int(os.environ['REDIS_DB'] if 'REDIS_DB' in os.environ else 1)
        )

        self.redis_pubsub = self.redis_client.pubsub()

    def _subscribe(self):
        self.redis_pubsub.psubscribe(
            'start_container.*',
            'start_containers_not_running',
            'close_container',
            'monitor_container_status'
        )

    def __register_channel(self, channel):

        if 'channel' in self.redis_client.pubsub_channels():
            self.redis_pubsub.psubscribe(
                channel
            )
            print(f'The new channel {channel} was subscribed', flush=True)
        else:
            print(f'Don\'t was subscribe to {channel} because is already listen it', flush=True)

    def _publish(self, channel, message):
        self.redis_client.publish(
            channel,
            message
        )

    @staticmethod
    def format_message(message: dict):
        """
        Format the message to a readable message json.
        Here is filter the message type 'pmessage' but is possible
        to use ".pubsub(ignore_subscribe_messages=True)" to ignore
        subscribe messages.
        :param message: The raw message received from channel
        :return: bool -> has a valid message, str -> channel that message is from,
        dict -> the message received from channel
        """

        if isinstance(message, dict):
            if message.get('type', '') == 'pmessage':
                return True, message.get('channel', '').decode('UTF-8'), \
                       json.loads(message.get('data', '').decode('UTF-8'))

        return False, None, None

    def _request_message(self):
        is_valid, channel, message = DockerOrchestratorRedisPubsub.format_message(
            self.redis_pubsub.get_message()
        )

        # Just messages from type pmessage
        if not is_valid:
            return

        # When was received a channel to response the container (log, status, state)
        # is need register the channel/or register to the channel
        # to be possible publish on to it
        if BaseConsumerMessages._check_key_exists(message, 'response_channel'):
            self.__register_channel(message['response_channel'])

        self._receive_message(channel, message)

    def _close_connection(self) -> None:
        self.redis_client.close()
