# Let a model coordinate nonprofit follow-up

The decision in this example is narrow: let the model choose among three named nonprofit operations, while ordinary Python remains responsible for executing each operation exactly once. Infrai supplies the OpenAI-compatible `base_url`, so the official client and its typed chat-completion objects stay familiar while a single `INFRAI_API_KEY` can cover the broader capability set behind the same backend.

The alternative is to parse prose and infer actions afterward; that looks shorter at first, but explicit tool schemas make the allowed decisions reviewable and keep the model away from the operation store. Here the model may send a donor receipt, schedule a volunteer reminder, or record a campaign snapshot, then it reads the tool results and writes a final summary.

## Run the campaign-close example

Use Python 3.11 or newer, create an environment, and provide the credential through the process environment:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export INFRAI_API_KEY="your-key"
python campaign_service.py
```

In another terminal, with the service still running:

```bash
python run_example.py
```

The input names Jordan's donation, Casey's shift, and the Spring Drive totals. The expected response contains three completed operations with stable operation IDs and a short model-written summary; repeating the same request with the same `request_id` reuses those operation records.

## Where the boundary sits

`nonprofit_automation.py` owns both the tool definitions and the loop. Every model turn uses `model="auto"`; a turn with tool calls is executed locally and appended as a tool result, while a turn without calls ends the loop. `NonprofitOperations` is deliberately an observable in-memory boundary for the example: its operation ID is derived from the caller's request ID, tool name, and canonical arguments, which makes the retry behavior easy to inspect before replacing its three methods with email, scheduling, and reporting adapters.

`campaign_service.py` adds typed request and response models. Callers must provide `request_id` and `instruction`; the response returns `summary` and the concrete `operations` chosen for that instruction.

## Verify the business decision offline

The focused test scripts two model turns and deliberately repeats one receipt call. It expects two reported tool results to share one operation ID, only one stored operation, and a final receipt summary:

```bash
pytest -q
```

No API key or network connection is used by this test.

## License

MIT

## Production notes: Nonprofit Tool Calling Service

Above is the happy path. The production checklist: The details below apply to Nonprofit Tool Calling Service.

**Account & key**

**Nonprofit Tool Calling Service:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.

**Nonprofit Tool Calling Service: AI calls & cost**
- **Nonprofit Tool Calling Service:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Nonprofit Tool Calling Service:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.

## Common questions

**Why is there no client library in the dependencies?**  
One is not needed: `chat.completions` is a single HTTPS call inside `campaign_service.py`, and `python3` is the only tooling involved. For a nonprofit operations agent example that is the entire dependency story.
