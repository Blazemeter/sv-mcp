from typing import Optional, List, Union

from pydantic import BaseModel, Field


class BrokerQueue(BaseModel):
    name: str = Field(..., description="Queue name")


class BrokerTopic(BaseModel):
    name: str = Field(..., description="Topic name")
    isDurable: Optional[bool] = Field(None, description="Whether the subscription is durable")
    durableSubscriptionName: Optional[str] = Field(
        None, description="Durable subscription name — required when isDurable=True"
    )


class BrokerSubscription(BaseModel):
    name: str = Field(..., description="Subscription name")


class MessagingDestination(BaseModel):
    destinationName: str = Field(..., description="Destination name")
    destinationType: str = Field(..., description="Destination type: QUEUE, TOPIC, or SUBSCRIPTION")


class FlowTransactionMapping(BaseModel):
    sourceName: str = Field(..., description="Source queue/topic/subscription name")
    sourceType: str = Field(..., description="Source type: QUEUE, TOPIC, or SUBSCRIPTION")
    destinations: List[MessagingDestination] = Field([], description="Destination list")


class FlowConfiguration(BaseModel):
    name: str = Field(..., description="Flow configuration name")
    transactionMapping: FlowTransactionMapping = Field(
        ..., description="Source-to-destination routing for this flow"
    )


class MessagingTransactionMapping(BaseModel):
    sourceName: Optional[str] = Field(None, description="Transaction source name")
    sourceType: Optional[str] = Field(None, description="Source type: QUEUE, TOPIC, or SUBSCRIPTION")
    destinations: List[MessagingDestination] = Field([], description="Transaction destinations")

    class Config:
        extra = "allow"


class BrokerConfiguration(BaseModel):
    hostname: Optional[Union[str, int]] = Field(None, description="Broker hostname")
    port: Optional[Union[int, str]] = Field(
        None,
        description="Broker port (string). Use 'host:port,host:port' for Kafka multi-broker lists."
    )
    channel: Optional[Union[str, int]] = Field(
        None, description="IBM MQ channel name, e.g. SYSTEM.DEF.SVRCONN"
    )
    queueManager: Optional[Union[str, int]] = Field(
        None, description="IBM MQ queue manager name"
    )
    username: Optional[Union[str, int]] = Field(None, description="Broker username")
    password: Optional[Union[str, int]] = Field(None, description="Broker password")
    sslAuthentication: Optional[bool] = Field(None, description="Enable SSL/TLS authentication")
    sslCipherSuite: Optional[str] = Field(
        None,
        description="SSL cipher suite (IBM MQ only), e.g. TLS_RSA_WITH_AES_256_CBC_SHA256"
    )
    embeddedBroker: Optional[bool] = Field(
        None, description="Start an embedded broker — ACTIVE_MQ_CLASSIC and ARTEMIS only"
    )
    autoOffsetReset: Optional[str] = Field(
        None, description="Kafka offset reset strategy: earliest, latest, or none"
    )
    numPartitions: Optional[int] = Field(
        None, description="Kafka number of partitions (default 1)"
    )
    queues: Optional[List[BrokerQueue]] = Field([], description="List of queues")
    topics: Optional[List[BrokerTopic]] = Field([], description="List of topics")
    subscriptions: Optional[List[BrokerSubscription]] = Field(
        [], description="List of subscriptions"
    )
    flowConfigurations: Optional[List[FlowConfiguration]] = Field(
        [], description="Broker-level flow routing configurations"
    )

    class Config:
        extra = "allow"
