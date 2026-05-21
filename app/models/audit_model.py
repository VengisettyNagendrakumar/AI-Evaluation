from datetime import datetime
from uuid import uuid4

from pydantic import BaseModel


class AuditModel(
    BaseModel
):

    audit_id: str

    timestamp: datetime

    event_type: str

    details: dict

    @classmethod
    def create(
        cls,
        event_type: str,
        details: dict
    ):

        return cls(

            audit_id=str(
                uuid4()
            ),

            timestamp=datetime.utcnow(),

            event_type=event_type,

            details=details
        )