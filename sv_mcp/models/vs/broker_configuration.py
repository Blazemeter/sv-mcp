from typing import Optional, List, Union

from pydantic import BaseModel, Field


class BrokerQueue(BaseModel):
    name: str = Field(..., description="Queue name")


class BrokerTopic(BaseModel):
    name: str = Field(..., description="Topic name")


class MessagingDestination(BaseModel):
    destinationName: str = Field(..., description="Destination name")
    destinationType: str = Field(..., description="Destination type. QUEUE or TOPIC")


class MessagingTransactionMapping(BaseModel):
    sourceName: Optional[str] = Field(None, description="Transaction source name")
    sourceType: Optional[str] = Field(None, description="Transaction source type. QUEUE or TOPIC")
    destinations: List[MessagingDestination] = Field([], description="Transaction destinations")

    class Config:
        extra = "allow"


class BrokerConfiguration(BaseModel):
    hostname: Optional[Union[str, int]] = Field(None, description="Broker hostname")
    port: Optional[Union[int, str]] = Field(None, description="Broker port")
    channel: Optional[Union[str, int]] = Field(None, description="IBM MQ9 channel name")
    queueManager: Optional[Union[str, int]] = Field(None, description="IBM MQ9 queue manager name")
    username: Optional[Union[str, int]] = Field(None, description="Broker username")
    password: Optional[Union[str, int]] = Field(None, description="Broker password")
    queues: Optional[List[BrokerQueue]] = Field([], description="List of queues")
    topics: Optional[List[BrokerTopic]] = Field([], description="List of topics")
    flowConfigurations: Optional[List[MessagingTransactionMapping]] = Field(
        [], description="List of messaging transaction mappings"
    )

    class Config:
        extra = "allow"  # allows additional unexpected fields
