from src.broker.consumer_factory import ConsumerFactory

if __name__ == '__main__':

    try:

        consumer = ConsumerFactory.get_instance('redis')
        consumer.start()

    except Exception as e:

        print('Not has been possible initiate the application')
        print(str(e))
