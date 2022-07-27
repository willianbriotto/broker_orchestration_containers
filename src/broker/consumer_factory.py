from src.broker.docker_orchestrator_redis_pubsub import DockerOrchestratorRedisPubsub


class ConsumerFactory:

    @staticmethod
    def get_instance(broker_name: str):

        if broker_name.lower() == 'redis':
            return DockerOrchestratorRedisPubsub()
        else:
            raise Exception('This broker is not implemented yet')
