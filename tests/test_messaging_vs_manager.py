import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from sv_mcp.models.result import BaseResult
from sv_mcp.tools.vs.messaging_virtual_service_manager import MessagingVirtualServiceManager

pytestmark = pytest.mark.asyncio


@pytest.fixture
def manager():
    return MessagingVirtualServiceManager(token=MagicMock(), ctx=MagicMock())


async def test_create_generic_activemq(manager):
    with patch("sv_mcp.tools.vs.messaging_virtual_service_manager.vs_api_request") as mock_req:
        mock_req.return_value = BaseResult(result=[])
        await manager.create(
            workspace_id=1,
            name="my-vs",
            service_id=2,
            harborId="h1",
            shipId="s1",
            messaging_protocol="ACTIVE_MQ_CLASSIC",
            broker_config={"hostname": "localhost", "port": "61616", "embeddedBroker": False},
        )
    call_json = mock_req.call_args.kwargs["json"]
    assert call_json["messagingProtocol"] == "ACTIVE_MQ_CLASSIC"
    assert call_json["brokerConfig"]["hostname"] == "localhost"
    assert call_json["messagingRunnerEnabled"] is True


async def test_create_generic_kafka(manager):
    with patch("sv_mcp.tools.vs.messaging_virtual_service_manager.vs_api_request") as mock_req:
        mock_req.return_value = BaseResult(result=[])
        await manager.create(
            workspace_id=1,
            name="kafka-vs",
            service_id=3,
            harborId="h1",
            shipId="s1",
            messaging_protocol="KAFKA",
            broker_config={"hostname": "broker1", "port": "broker1:9092", "autoOffsetReset": "earliest"},
            priority_mode="ROUND_ROBIN",
        )
    call_json = mock_req.call_args.kwargs["json"]
    assert call_json["messagingProtocol"] == "KAFKA"
    assert call_json["priorityMode"] == "ROUND_ROBIN"


async def test_create_mq9_alias_delegates(manager):
    manager.create = AsyncMock(return_value=BaseResult(result=[]))
    await manager.create_mq9(
        workspace_id=1, vs_name="vs", service_id=2, harborId="h", shipId="s",
        mock_service_transactions=[],
        mq9_broker_hostname="mq.host", mq9_broker_port=1414,
        mq9_broker_channel="SYSTEM.DEF.SVRCONN",
        mq9_queue_manager="QM1", mq9_queue_username="admin", mq9_queue_password="pass",
    )
    manager.create.assert_awaited_once()
    kwargs = manager.create.call_args.kwargs
    assert kwargs["messaging_protocol"] == "IBM_MQ9_JMS"
    assert kwargs["broker_config"]["channel"] == "SYSTEM.DEF.SVRCONN"


async def test_update_generic(manager):
    with patch("sv_mcp.tools.vs.messaging_virtual_service_manager.vs_api_request") as mock_req:
        mock_req.return_value = BaseResult(result=[])
        await manager.update(
            workspace_id=1,
            vs_id=10,
            name="updated-vs",
            messaging_protocol="ACTIVE_MQ_ARTEMIS",
            broker_config={"hostname": "artemis.host", "port": "61616"},
        )
    call = mock_req.call_args
    assert call.args[1] == "PATCH"
    body = call.kwargs["json"]
    assert body["name"] == "updated-vs"
    assert body["messagingProtocol"] == "ACTIVE_MQ_ARTEMIS"
    # Unset optional fields must NOT appear in the body
    assert "priorityMode" not in body
    assert "recorderConfig" not in body


async def test_update_mq9_alias_delegates(manager):
    manager.update = AsyncMock(return_value=BaseResult(result=[]))
    await manager.update_mq9(
        workspace_id=1, vs_id=10,
        vs_name="vs", service_id=None, harborId=None, shipId=None,
        mock_service_transactions=None,
        mq9_broker_hostname="mq.host", mq9_broker_port=1414,
        mq9_broker_channel="SYSTEM.DEF.SVRCONN",
        mq9_queue_manager="QM1", mq9_queue_username="admin", mq9_queue_password="pass",
    )
    manager.update.assert_awaited_once()
    kwargs = manager.update.call_args.kwargs
    assert kwargs["messaging_protocol"] == "IBM_MQ9_JMS"
    assert kwargs["broker_config"]["queueManager"] == "QM1"
