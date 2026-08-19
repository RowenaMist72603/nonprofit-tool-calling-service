"""HTTP entry point for the nonprofit automation loop."""

import json
import os
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field

from nonprofit_automation import NonprofitOperations, build_client, run_automation_loop


class AutomationRequest(BaseModel):
    request_id: str = Field(min_length=1, description="Stable caller-supplied retry key")
    instruction: str = Field(min_length=1)


class OperationResult(BaseModel):
    operation_id: str
    tool: str
    status: str
    details: dict[str, object]


class AutomationResponse(BaseModel):
    summary: str
    operations: list[OperationResult]


app = FastAPI(title="Nonprofit automation service")
operations = NonprofitOperations()


def get_client():
    return build_client(os.environ["INFRAI_API_KEY"])


@app.post("/automations", response_model=AutomationResponse)
def automate(
    request: AutomationRequest,
    client: Annotated[object, Depends(get_client)],
) -> AutomationResponse:
    try:
        summary, completed = run_automation_loop(
            client, operations, request.request_id, request.instruction
        )
    except (ValueError, json.JSONDecodeError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return AutomationResponse(summary=summary, operations=completed)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("campaign_service:app", host="127.0.0.1", port=8000)
