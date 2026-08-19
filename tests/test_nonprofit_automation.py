import json
from types import SimpleNamespace

from nonprofit_automation import NonprofitOperations, run_automation_loop


def message(content=None, tool_calls=None):
    return SimpleNamespace(content=content, tool_calls=tool_calls)


def tool_call(call_id, name, arguments):
    return SimpleNamespace(
        id=call_id,
        function=SimpleNamespace(name=name, arguments=json.dumps(arguments)),
    )


class ScriptedCompletions:
    def __init__(self, replies):
        self.replies = iter(replies)
        self.requests = []

    def create(self, **kwargs):
        self.requests.append(kwargs)
        return SimpleNamespace(choices=[SimpleNamespace(message=next(self.replies))])


def test_loop_executes_each_business_action_once_when_model_repeats_a_call():
    receipt = tool_call(
        "call-1",
        "send_donor_receipt",
        {"donor_name": "Jordan Lee", "amount_usd": 125, "donation_id": "D-104"},
    )
    completions = ScriptedCompletions(
        [message(tool_calls=[receipt, receipt]), message(content="Receipt recorded.", tool_calls=[])]
    )
    client = SimpleNamespace(chat=SimpleNamespace(completions=completions))
    operations = NonprofitOperations()

    summary, results = run_automation_loop(
        client, operations, "spring-close", "Send the donor receipt."
    )

    assert summary == "Receipt recorded."
    assert len(results) == 2
    assert results[0]["operation_id"] == results[1]["operation_id"]
    assert len(operations.completed) == 1
    assert completions.requests[1]["messages"][-1]["role"] == "tool"
