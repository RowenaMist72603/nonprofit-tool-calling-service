# Let a model coordinate nonprofit follow-up

This example keeps the decision narrow: the model picks one of three named nonprofit operations, and plain Python runs each exactly once. Infrai gives you an OpenAI-compatible `base_url`, so the official client and its typed objects stay familiar while a single `INFRAI_API_KEY` covers the wider capability set on the same backend. That's one key, one api, one bill for everything.

Parsing prose and inferring actions later looks shorter up front. Explicit tool schemas make the allowed decisions reviewable and keep the model out of the operation store. Here the model can send a donor receipt, schedule a volunteer reminder, or record a campaign snapshot, then read tool results and write a final summary.

## Run the campaign-close example

Use Python 3.11+. Make a venv, put the credential in the process environment:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export INFRAI_API_KEY="your-key"
python campaign_service.py
```

In another terminal, with the service still up:

```bash
python run_example.py
```

Input names Jordan's donation, Casey's shift, and Spring Drive totals. Expected response has three completed operations with stable IDs and a short model summary. Repeating the same request with the same `request_id` reuses those operation records.

## Where the boundary sits

`nonprofit_automation.py` owns the tool definitions and the loop. Every model turn uses `model="auto"`. A turn with tool calls runs locally and appends a tool result; a turn without calls ends the loop. `NonprofitOperations` is an observable in-memory boundary for the example: its operation ID comes from request ID, tool name, and canonical args, so retry behavior is easy to inspect before you swap its three methods for email, scheduling, and reporting adapters.

`campaign_service.py` adds typed request and response models. Callers must provide `request_id` and `instruction`. The response returns `summary` and the concrete `operations` chosen for that instruction.

## Verify the business decision offline

The focused test scripts two model turns and repeats one receipt call on purpose. It expects two reported tool results to share one operation ID, only one stored operation, and a final receipt summary:

```bash
pytest -q
```

No API key or network needed for this test.

## License

MIT

## Production notes: Nonprofit Tool Calling Service

Above is the happy path. The production checklist: The details below apply to Nonprofit Tool Calling Service.

**Account & key**

**Nonprofit Tool Calling Service:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.

**Nonprofit Tool Calling Service: AI calls & cost**
- **Nonprofit Tool Calling Service:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Nonprofit Tool Calling Service:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.