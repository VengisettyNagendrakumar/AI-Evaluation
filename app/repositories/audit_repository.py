from app.models.audit_model import (
    AuditModel
)


class AuditRepository:

    audit_logs = []

    @classmethod
    async def log_event(
        cls,
        event_type: str,
        details: dict
    ) -> AuditModel:

        audit_record = (
            AuditModel.create(
                event_type=event_type,
                details=details
            )
        )

        cls.audit_logs.append(
            audit_record
        )

        return audit_record

    @classmethod
    async def get_audit_logs(
        cls
    ):

        return cls.audit_logs