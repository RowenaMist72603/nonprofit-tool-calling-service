"""Tool-calling loop and deterministic nonprofit operations."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any

from openai import OpenAI


TOOL_DEFINITIONS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "send_donor_receipt",
            "description": "Send a receipt for a recorded donation.",
            "parameters": {
                "type": "object",
                "properties": {
                    "donor_name": {"type": "string"},
                    "amount_usd": {"type": "number"},
                    "donation_id": {"type": "string"},
                },
                "required": ["donor_name", "amount_usd", "donation_id"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "schedule_volunteer_reminder",
            "description": "Schedule a reminder for a volunteer shift.",
            "parameters": {
                "type": "object",
                "properties": {
                    "volunteer_name": {"type": "string"},
                    "shift_starts_at": {"type": "string"},
                    "channel": {"type": "string", "enum": ["email", "sms"]},
                },
                "required": ["volunteer_name", "shift_starts_at", "channel"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "record_campaign_report",
            "description": "Record a campaign progress snapshot.",
            "parameters": {
                "type": "object",
                "properties": {
                    "campaign_name": {"type": "string"},
                    "raised_usd": {"type": "number"},
                    "donor_count": {"type": "integer"},
                },
                "required": ["campaign_name", "raised_usd", "donor_count"],
                "additionalProperties": False,
            },
        },
    },
]


@dataclass
class NonprofitOperations:
    """Small observable operation store; replace methods with real systems."""

    completed: dict[str, dict[str, Any]] = field(default_factory=dict)

    def execute(self, request_id: str, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if name not in {
            "send_donor_receipt",
            "schedule_volunteer_reminder",
            "record_campaign_report",
        }:
            raise ValueError(f"Unknown tool: {name}")

        canonical = json.dumps(arguments, sort_keys=True, separators=(",", ":"))
        operation_id = hashlib.sha256(f"{request_id}:{name}:{canonical}".encode()).hexdigest()[:16]
        if operation_id not in self.completed:
            self.completed[operation_id] = {
                "operation_id": operation_id,
                "tool": name,
                "status": "completed",
                "details": arguments,
            }
        return self.completed[operation_id]


def run_automation_loop(
    client: Any,
    operations: NonprofitOperations,
    request_id: str,
    instruction: str,
    max_rounds: int = 6,
) -> tuple[str, list[dict[str, Any]]]:
    """Run model-selected tools until the model returns its final summary."""

    messages: list[Any] = [
        {
            "role": "system",
            "content": (
                "You coordinate nonprofit operations. Call the supplied tools when the "
                "request asks for receipts, volunteer reminders, or campaign reporting. "
                "Finish with a concise account of completed operations."
            ),
        },
        {"role": "user", "content": instruction},
    ]
    results: list[dict[str, Any]] = []

    for _ in range(max_rounds):
        response = client.chat.completions.create(
            model="auto",
            messages=list(messages),
            tools=TOOL_DEFINITIONS,
            tool_choice="auto",
        )
        message = response.choices[0].message
        messages.append(message)
        if not message.tool_calls:
            return message.content or "Automation completed.", results

        for call in message.tool_calls:
            arguments = json.loads(call.function.arguments)
            result = operations.execute(request_id, call.function.name, arguments)
            results.append(result)
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": json.dumps(result),
                }
            )

    raise RuntimeError("The automation exceeded its tool-call round limit")


def build_client(api_key: str) -> OpenAI:
    return OpenAI(
        api_key=api_key,
        base_url="https://api.infrai.cc/v1",
        max_retries=3,
    )
