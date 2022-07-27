from src.orchestrator.orchestration_containers import OrchestrationContainers
from tests.fixtures.docker_fixture import docker_fixture, side_effect_check_container_status


def test__images_exists():
    orchestration_containers = OrchestrationContainers()
    assert orchestration_containers\
               ._OrchestrationContainers__images_exists('nginx_image')


def test__images_exists_no_exists():
    orchestration_containers = OrchestrationContainers()
    assert not orchestration_containers\
               ._OrchestrationContainers__images_exists('does_not_exists_this_image:latest')


def test__container_name_already_exists():
    orchestration_containers = OrchestrationContainers()
    orchestration_containers\
        ._OrchestrationContainers__container_name_already_exists('nginx')


def test_build_image():
    orchestration_containers = OrchestrationContainers()
    orchestration_containers \
        .build_image(context='./', tag='nginx_build_image:latest')
    assert orchestration_containers \
        ._OrchestrationContainers__images_exists('nginx_build_image:latest')


def test_start_container():
    orchestration_containers = OrchestrationContainers()
    orchestration_containers \
        .start_container(contains='redis')
    assert side_effect_check_container_status(name='redis', status='running')

def test_run_container():
    orchestration_containers = OrchestrationContainers()
    orchestration_containers.run_container(
        image='nginx_image', name='nginx_test',
        command='pytest -v', network='network_test',
        volumes={}, environment=[]
    )
    assert side_effect_check_container_status(name='nginx_test', status='running')
