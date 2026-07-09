from sv_mcp.models.vs.broker_configuration import (
    BrokerConfiguration, BrokerTopic, BrokerSubscription, FlowConfiguration
)
from sv_mcp.models.vs.response_delay import ResponseDelay


def test_broker_topic_durable_fields():
    t = BrokerTopic(name="orders", isDurable=True, durableSubscriptionName="sub1")
    assert t.isDurable is True
    assert t.durableSubscriptionName == "sub1"


def test_broker_subscription_model():
    s = BrokerSubscription(name="my-sub")
    assert s.name == "my-sub"


def test_broker_configuration_ssl_fields():
    cfg = BrokerConfiguration(
        hostname="mq.example.com",
        port="1414",
        sslAuthentication=True,
        sslCipherSuite="TLS_RSA_WITH_AES_256_CBC_SHA256",
    )
    assert cfg.sslAuthentication is True
    assert cfg.sslCipherSuite == "TLS_RSA_WITH_AES_256_CBC_SHA256"


def test_broker_configuration_kafka_fields():
    cfg = BrokerConfiguration(
        hostname="broker1",
        port="broker1:9092,broker2:9092",
        autoOffsetReset="earliest",
        numPartitions=3,
    )
    assert cfg.autoOffsetReset == "earliest"
    assert cfg.numPartitions == 3


def test_broker_configuration_embedded_broker():
    cfg = BrokerConfiguration(hostname="localhost", port="61616", embeddedBroker=True)
    assert cfg.embeddedBroker is True


def test_broker_configuration_subscriptions():
    cfg = BrokerConfiguration(
        hostname="localhost",
        port="61616",
        subscriptions=[{"name": "my-sub"}],
    )
    assert len(cfg.subscriptions) == 1
    assert cfg.subscriptions[0].name == "my-sub"


def test_flow_configuration_parsed():
    cfg = BrokerConfiguration(
        hostname="localhost",
        port="1414",
        flowConfigurations=[{
            "name": "order-flow",
            "transactionMapping": {
                "sourceName": "ORDER.IN",
                "sourceType": "QUEUE",
                "destinations": [{"destinationName": "ORDER.OUT", "destinationType": "QUEUE"}]
            }
        }]
    )
    fc = cfg.flowConfigurations[0]
    assert fc.name == "order-flow"
    assert fc.transactionMapping.sourceName == "ORDER.IN"
    assert fc.transactionMapping.destinations[0].destinationName == "ORDER.OUT"


def test_response_delay_fixed():
    d = ResponseDelay(type="FIXED", fixedDelay=200)
    assert d.fixedDelay == 200


def test_response_delay_lognormal():
    d = ResponseDelay(type="LOGNORMAL", median=100.0, sigma=0.5)
    assert d.median == 100.0
    assert d.sigma == 0.5
