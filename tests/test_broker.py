import pytest

from src.broker.base_consumer_messages import BaseConsumerMessages
from tests.fixtures.docker_fixture import docker_fixture, side_effect_check_container_status


def test__receive_message_start_container_function_create_invalid():
    base_consumer = BaseConsumerMessages()

    with pytest.raises(TypeError):
        assert base_consumer._receive_message(
            channel='start_container.create',
            message='{}'
        )

def test__receive_message_start_container_function_create_valid():
    base_consumer = BaseConsumerMessages()
    base_consumer._receive_message(
        channel='start_container.create',
        message={'image': 'nginx_image', 'name': 'nginx_test_broker'}
    )

    assert side_effect_check_container_status(name='nginx_test_broker', status='running')


def test__receive_message_start_container_function_response_channel_invalid():
    base_consumer = BaseConsumerMessages()

    with pytest.raises(TypeError):
        assert base_consumer._receive_message(
            channel='start_container.response_channel',
            message='{}'
        )

def test__receive_message_start_container_function_response_channel_valid():
    base_consumer = BaseConsumerMessages()
    base_consumer._receive_message(
        channel='start_container.response_channel',
        message={
            'image': 'nginx_image',
            'name': 'nginx_test_broker',
            'response_channel': 'the_response_channel'
        }
    )

    assert side_effect_check_container_status(name='nginx_test_broker', status='running')

def test__receive_message_start_containers_not_running():
    base_consumer = BaseConsumerMessages()
    base_consumer._receive_message(
        channel='start_containers_not_running',
        message={
            'name': 'redis',
            'exact_value': True
        }
    )

    assert side_effect_check_container_status(name='redis', status='running')
