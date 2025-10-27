from pydantic import BaseModel, Field


class MessagingProperty(BaseModel):
    name: str = Field(..., description="JMS property name")
    value: str = Field(..., description="JMS property value")
    type: str = Field(...,
                      description="JMS property type. Supported types are 'BOOLEAN', 'BYTE', 'SHORT',"
                                  " 'INT', 'LONG', 'FLOAT', 'DOUBLE' and 'STRING'.")

    class Config:
        extra = "allow"  # allows additional unexpected fields
