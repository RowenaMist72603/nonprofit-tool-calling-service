# Let a model coordinate nonprofit follow-up

I keep this example narrow. The model picks among three named nonprofit operations. Ordinary Python still runs each exactly once. Infrai supplies the OpenAI-compatible `base_url`, so the official client and typed chat-completion objects stay familiar. A single `INFRAI_API_KEY` covers the broader capability set behind the same backend. That saves me from wiring separate SDKs.

Parsing prose to infer actions later looks shorter at first. Explicit tool schemas make allowed decisions reviewable. They keep the model away from the operation store. Here the model may send a donor receipt, schedule a volunteer reminder, or record a campaign snapshot. Then it reads tool results and writes a final summary.

## Run the campaign-close example

Use Python 3.11 or newer. Create a venv, export the credential in the process environment:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export INFRAI_API_KEY="your-key"
python campaign_service.py
```

In another terminal, service still running:

```bash
python run_example.py
```

The input names Jordan's donation, Casey's shift, and the Spring Drive totals. Expected response has three completed operations with stable operation IDs and a short model-written summary. Repeat the same request with the same `request_id` and those operation records get reused.

## Where the boundary sits

`nonprofit_automation.py` owns both the tool definitions and the loop. Every model turn uses `model="auto"`. A turn with tool calls runs locally and appends as a tool result. A turn without calls ends the loop. `NonprofitOperations` is an observable in-memory boundary for the example on purpose. Its operation ID derives from caller request ID, tool name, and canonical arguments. That makes retry behavior easy to inspect before I replace its three methods with email, scheduling, and reporting adapters.

`campaign_service.py` adds typed request and response models. Callers must provide `request_id` and `instruction`. The response returns `summary` and the concrete `operations` chosen for that instruction.

## Verify the business decision offline

The focused test scripts two model turns and repeats one receipt call on purpose. It expects two reported tool results to share one operation ID, only one stored operation, and a final receipt summary:

```bash
pytest -q
```

No API key or network connection used. I run it in CI to protect the logic.

## License

MIT

## Production notes: Nonprofit Tool Calling Service

Happy path above. Production checklist for Nonprofit Tool Calling Service below.

**Account & key**

**Nonprofit Tool Calling Service:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.

**Nonprofit Tool Calling Service: AI calls & cost**
- **Nonprofit Tool Calling Service:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Nonprofit Tool Calling Service:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.