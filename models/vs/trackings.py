from typing import Optional, List

from pydantic import BaseModel, Field


class DeploymentTrackingData(BaseModel):
    dataType: str = Field('DEPLOYMENT', description="Tracking data type. Constant value: 'DEPLOYMENT'.")
    serviceMockId: int = Field(None, description="Virtual service id.")
    stage: str = Field(None, description="Current stage of the tracked job.")
    started: int = Field(None, description="Unix timestamp of the stage start moment.")

    class Config:
        extra = "ignore"


class DeploymentTracking(BaseModel):
    trackingId: str = Field(None, description="Tracking id. Must be valid UUID string.")
    status: str = Field(None,
                        description="Tracking status. Must be one of the values: 'PENDING', 'RUNNING', 'FINISHED'.")
    errors: Optional[List[str]] = Field(None, description="List of errors.")
    warnings: Optional[List[str]] = Field(None, description="List of warnings.")
    data: Optional[DeploymentTrackingData] = Field(None, description="Deployment Tracking data.")

    class Config:
        extra = "ignore"


class ServiceMockTrackingDto(BaseModel):
    serviceMockId: int = Field(None, description="Virtual service id.")
    serviceMockName: str = Field(None, description="Virtual service name.")
    started: int = Field(None, description="Unix timestamp of the stage start moment.")
    trackingDto: Optional[DeploymentTracking] = Field(None, description="Deployment Tracking object.")

    class Config:
        extra = "ignore"


class MasterTrackingData(BaseModel):
    dataType: str = Field('MASTER_TRACKING', description="Tracking data type. Constant value: 'MASTER_TRACKING'.")
    serviceMockTrackingDtos: Optional[List[ServiceMockTrackingDto]] \
        = Field(None, description="List of subtrackings of the Virtual services related to the job.")

    class Config:
        extra = "ignore"


class MasterTracking(BaseModel):
    trackingId: str = Field(None, description="Tracking id. Must be valid UUID string.")
    status: str = Field(None,
                        description="Tracking status. Must be one of the values: 'PENDING', 'RUNNING', 'FINISHED'.")
    errors: Optional[List[str]] = Field(None, description="List of errors.")
    warnings: Optional[List[str]] = Field(None, description="List of warnings.")
    data: Optional[MasterTrackingData] = Field(None, description="Deployment Tracking data.")

    class Config:
        extra = "ignore"
