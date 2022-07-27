import pytest
from unittest import mock
from datetime import datetime

class ContainerObjectMock:

    def __init__(self, name, status='running', environment={}) -> None:
        self.name = name
        self.status = status
        self.environment = environment

    def stop(self):
        return True

    def start(self):
        self.status = 'running'
        return True

    def logs(self, since=datetime.now()):
        return 'Mock log container ' + datetime.strftime(since, '%Y-%m-%d')

DEFAULT_MOCK_IMAGE_LIST = [
    mock.Mock(name="Image Mock Item", **{
        'tags': ['nginx_image']
    }),
    mock.Mock(name="Image Mock Item", **{
        'tags': ['python_image']
    }),
    mock.Mock(name="Image Mock Item", **{
        'tags': ['ubuntu_image']
    }),
    mock.Mock(name="Image Mock Item", **{
        'tags': ['rabbitmq:latest']
    })
]

DEFAULT_MOCK_CONTAINERS_LIST = [
    ContainerObjectMock('nginx'),
    ContainerObjectMock('nginx-all-sites'),
    ContainerObjectMock('redis', 'error'),
    ContainerObjectMock('postgresql'),
]


def side_effect_list_images(*args, **kwargs):
    DEFAULT_MOCK_IMAGE_LIST.append(
        mock.Mock(name="Image Mock Item", **{
            'tags': [kwargs['tag']]
        })
    )
    return DEFAULT_MOCK_IMAGE_LIST

def side_effect_list_containers(*args, **kwargs):
    DEFAULT_MOCK_CONTAINERS_LIST.append(
        ContainerObjectMock(kwargs['name'], environment=kwargs['environment'])
    )
    return DEFAULT_MOCK_CONTAINERS_LIST

def side_effect_check_container_status(name, status):
    return len(list(
        filter(lambda x: x.name == name and x.status == status, DEFAULT_MOCK_CONTAINERS_LIST)
    )) > 0

@pytest.fixture(autouse=True)
def docker_fixture():

    with mock.patch('src.orchestrator.orchestration_containers.docker') as _fixture:

        _fixture.from_env.return_value = mock.Mock(name="Docker from env", **{
            'images': mock.Mock(name="mock Docker images list", **{
                'list.return_value': DEFAULT_MOCK_IMAGE_LIST,
                'build.return_value': None,
                'build.side_effect': side_effect_list_images
            }),
            'containers': mock.Mock(name="mock Docker Container list", **{
                'list.return_value': DEFAULT_MOCK_CONTAINERS_LIST,
                'run.return_value': None,
                'run.side_effect': side_effect_list_containers
            })
        })

        yield _fixture

