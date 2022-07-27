import pytest

from src.broker.base_consumer_messages import BaseConsumerMessages
from src.broker.docker_orchestrator_redis_pubsub import DockerOrchestratorRedisPubsub
from tests.fixtures.docker_fixture import docker_fixture, side_effect_check_container_status


def test_format_message():

    assert (DockerOrchestratorRedisPubsub().format_message({
        'type': 'pmessage',
        'channel': 'channel_message'.encode('utf-8'),
        'data': '{"message": "infos"}'.encode('utf-8')
    })) == (True, 'channel_message', {'message': 'infos'})
