import json
import os
from datetime import datetime

import docker
import uuid

from src.monitor.manager_monitors import ManagerMonitors


class OrchestrationContainers:

    def __init__(self) -> None:

        self.docker_client = docker.from_env()
        self.managerMonitor = ManagerMonitors()

    def __images_exists(self, image) -> bool:
        return image in [item.tags[0] if len(item.tags) > 0 \
                             else '' for item in self.docker_client.images.list()]

    def build_image(self, context: str, tag: str = 'latest'):
        """
        Build the context/path with a tag.
        When an image with the same tag/name exists,
        nothing is done
        :param str context: The path where is found the Dockerfile
        :param str tag: The final name that the image should have
        """

        print(f'Building {tag} docker image...', flush=True)

        if self.__images_exists(tag):
            print(f'The image {tag} already exists..!!', flush=True)
        else:
            print(context)
            self.docker_client.images.build(path=context, tag=tag)
            print(f'Completed build of {tag} docker image...', flush=True)

    def __container_name_already_exists(self, name: str) -> bool:
        """
        Check if the container name exists.
        Not is possible run a container with the
        same tag/name
        :param str name: The tag/name of the container that will be searched
        :return: True if the searched name is defined to some container
        """
        return name in [container.name for container in self.docker_client.containers.list(all=True)]

    def start_container(self, contains: str, exact_value: bool = True):
        """
        Start containers that already exists and is not running.
        The container names is filtered by contains parameter, then
        all names that has "contains value" and is not running, will
        be trying to start it.

        :param str contains: The string that will be filtered the container names. It can
        receive an exact name or an incomplete name, like: "send_email_", where this
        will start all containers that contains send_email_ ir your name

        :param bool exact_value: Start a container with the exactly same name pass
        through the function
        """

        list_container_is_not_running = \
            filter(lambda x: x.status != 'running', self.docker_client.containers.list(all=True))

        if exact_value:
            list_container_is_not_running = \
                list(filter(lambda x: contains == x.name, list_container_is_not_running))
        else:
            list_container_is_not_running = \
                list(filter(lambda x: contains in x.name, list_container_is_not_running))

        print(f'Was found {len(list_container_is_not_running)} containers that match ' +
              'with filter name and not is current running...', flush=True)

        for container in list_container_is_not_running:
            print(f'Will start container that already exists({container.name})', flush=True)
            container.start()
            print(f'Success start container that already exists({container.name})\n', flush=True)

    def __define_timezone_container(self, environment: list):
        """
        All containers need to have a timezone setting,
        or they will be set with the host's timezone
        :param environment: List with strings with the format VAR=VAL
        """
        if 'TZ' not in environment and os.path.exists('/etc/timezone'):
            environment.append(
                'TZ=%s' % open('/etc/timezone').read().replace("\n", "")
            )

    def run_container(self, image: str, name: str, command: str,
                      network: str, volumes: dict, environment: list,
                      build: bool = False, **kwargs):
        """
        Run a new container

        :param str image: The image of the container

        :param str name: The tag/name of the container. Not is allowed run
        a container without this tag/name

        :param str command: The command that container will run.
        This parameter is not required, because do you can just up something
        like a nginx container that already have a command to execute. Do you
        just should use this parameter when your container should receive
        some command to execute

        :param str network: The network your container belongs to
        (The network not is built for you, do you needs
        to inform a valid network or leave this parameter empty)
        :param dict volumes:
            The volumes that will be created to this container.
            e.g: If you want to map some path to container, this parameter should receive something
            like that:

            volumes={
                /home/local/code/path: {
                    'bind': '/usr/src/container_internal_path/',
                    'mode': 'rw'
                },
                /home/local/code/path2: {
                    'bind': '/home/container_internal_path2/',
                    'mode': 'rw'
                }
            }

            The dict property name is your local path while the values are part
            of the references inside the container
            Reference: https://docker-py.readthedocs.io/en/stable/containers.html

        :param list environment: Environment variables that should be defined in
        the container. It will receive a list with strings
        [
            ('SOME_VARIABLE=999'),
            (f'ANOTHER_VARIABLE={interpolation_variable}'),
            ('%s=%s' % (var_name, var_value)),
        ]

        :param bool build: If is True try to find a local Dockerfile
        to build image. When it is False, it will try to found the image
        in docker hub
        """

        if not self.__images_exists(image):

            tag = kwargs['tag'] if 'tag' in kwargs and kwargs['tag'] else 'latest'

            print('The image not is found in your list of images...')

            if build:
                self.build_image(
                    context=kwargs['context'] if 'context' in kwargs else './',
                    tag=f'{image}:{tag}',
                )
            elif 'pull' in kwargs and kwargs['pull'] is True:
                print('Was found the pull parameter, then will try download '
                      + 'the image from Docker Hub Container Image Library')

                print(self.docker_client.images.pull(repository=image, tag=tag))
                print(f'Image {image}:{tag} download was completed with success')

            else:
                print('No image has been reported or the image is not yet built')
                print('It is not possible to run a container without a valid image')
                return

        if self.__container_name_already_exists(name=name):
            print('The container tag/name is already in use. '
                  + 'It is not possible create a container with the same tag/name')

            print(f'Will execute the command start the container {name} ...', flush=True)

            time_container_start = datetime.now()
            self.start_container(name)

            print(f'Was successful start the container {name} ...', flush=True)

            if 'detach' not in kwargs or kwargs['detach'] is False:
                container = \
                    list(filter(lambda x: name == x.name, self.docker_client.containers.list(all=True)))[-1]

                # This just will return the logs that happen in this execution
                # that was defines for the datetime that container received the start()
                return container.logs(since=time_container_start)

            return

        if not environment:
            environment = []

        # The UUID should be used to identify that container
        # was being running from this orchestrator
        environment.append(
            f'UUID={uuid.uuid4().hex}'
        )

        # If the container does not have a timezone configuration,
        # put the host's timezone
        self.__define_timezone_container(environment=environment)

        # Attempt that a no-detach action is a blocking
        if 'detach' in kwargs and kwargs['detach'] is False:
            return self.docker_client.containers.run(
                image,
                name=name,
                environment=environment,
                command=command,
                restart_policy={
                    "Name": "on-failure",
                    "MaximumRetryCount": 5
                },
                network=network,
                volumes=volumes
            )
        else:
            self.docker_client.containers.run(
                image,
                name=name,
                environment=environment,
                command=command,
                restart_policy={
                    "Name": "on-failure",
                    "MaximumRetryCount": 5
                },
                network=network,
                volumes=volumes,
                detach=True
            )
            print(f'Was successful create/start the container {name} ...', flush=True)

    def __start_monitor(self, name, response_channel,
                        default_status='running', on_response=None):

        # The container current status is the expected(default_status) status
        is_default_status = False

        container_monitor = self.docker_client.containers.get(name)

        if container_monitor.status != default_status:
            if on_response:
                on_response(
                    response_channel,
                    json.dumps({
                        'container': name,
                        'timestamp': datetime.now().timestamp(),
                        'running': False,
                        'current_status': container_monitor.status
                    })
                )
                is_default_status = False
        else:
            is_default_status = True

        return is_default_status

    def check_status(self, container: str, response_channel: str,
                     default_status: str = 'running', interval=10, on_response=None):

        print(f'Starting thread to check status of the container({container})' +
              f'that will notify when status is not equals to {default_status}', flush=True)
        self.managerMonitor.create_monitor(
            routine=self.__start_monitor,
            routine_args={
                'name': container,
                'default_status': default_status,
                'response_channel': response_channel,
                'on_response': on_response
            },
            interval=interval
        )
