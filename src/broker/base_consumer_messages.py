import asyncio
from time import sleep

from src.orchestrator.orchestration_containers import OrchestrationContainers


class BaseConsumerMessages:

    def __init__(self) -> None:
        self.container_orchestrator = OrchestrationContainers()

    def _subscribe(self):
        pass

    def _publish(self, channel, message):
        pass

    def _register_channel(self, channel):
        pass

    @staticmethod
    def _check_key_exists(message, key) -> bool:
        return (key in message) and (message[key])

    def _request_message(self):
        pass

    async def wait_message(self) -> None:
        """
        Pooling messages from broker

        It will listen start_container.*(create, wait_response)

        When it receives the message from start_container.create it
        will start a container but not
        wait for response

        When it receives the message from start_container.response_channel
        it should have in content
        has the value:
        {
            response_channel: 'topic_name'
        }
        The output of container that was run and wait response will send the output

        Message received in channel start_containers_not_running
        will start the container with the name passed by parameter

        monitor_container_status Starts a thread to monitor the status of a container.
        When this container is no longer running then it sends a message to the notification channel
        {
          "name": "container_name",
          "response_channel": "response_channel_when_status_is_wrong"
        }
        """

        self._subscribe()

        while True:
            try:
                
                self._request_message()

            except Exception as err:
                print('An error has been occur = ', str(err))

            sleep(.5)

    def _receive_message(self, channel, message):

        if channel == 'start_container.create':
            self.container_orchestrator.run_container(
                image=message['image'],
                name=message['name'],
                command=message.get('command', None),
                network=message.get('network', None),
                volumes=message.get('volumes', None),
                environment=message.get('environment', None),
                build=message.get('build', False),
                context=message.get('context', './'),
                pull=message.get('pull', False) and not message.get('build', False),
                detach=True
            )
        elif channel == 'start_container.response_channel':
            stdout_logs = self.container_orchestrator.run_container(
                image=message['image'],
                name=message['name'],
                command=message.get('command', None),
                network=message.get('network', None),
                volumes=message.get('volumes', None),
                environment=message.get('environment', None),
                build=message.get('build', False),
                context=message.get('context', './'),
                pull=message.get('pull', False) and not message.get('build', False),
                detach=False
            )

            print(f"Will notify the container logs in {message['response_channel']}", flush=True)
            self._publish(
                message['response_channel'],
                stdout_logs
            )
            print(f"The response channel {message['response_channel']} receive the logs", flush=True)
        elif channel == 'start_containers_not_running':
            self.container_orchestrator.start_container(
                contains=message['name'],
                exact_value=('exact_value' in message and message['exact_value']),
            )

        elif channel == 'monitor_container_status':
            self.container_orchestrator.check_status(
                container=message['name'],
                default_status='running',
                response_channel=message['response_channel'],
                interval=message['interval'] if 'interval' in message else 10,
                on_response=self._publish
            )

    def _close_connection(self) -> None:
        pass

    def start(self):
        """
        Start wait messages from broker
        """
        event_loop = asyncio.get_event_loop()
        event_loop.run_until_complete(self.wait_message())
        event_loop.close()

        self._close_connection()
