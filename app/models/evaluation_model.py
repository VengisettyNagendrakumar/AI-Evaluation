from datetime import datetime
from uuid import uuid4

from pydantic import BaseModel


class EvaluationModel(
    BaseModel
):

    evaluation_id: str

    timestamp: datetime

    request_data: dict

    result_data: dict

    @classmethod
    def create(
        cls,
        request_data: dict,
        result_data: dict
    ):

        return cls(
            evaluation_id=str(
                uuid4()
            ),

            timestamp=datetime.utcnow(),

            request_data=request_data,

            result_data=result_data
        )