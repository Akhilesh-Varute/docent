# Bedrock Converse API: notes from Week 1

## Two clients, two jobs
- "bedrock" is the control plane: list foundation models, manage guardrails,
  create custom models.
- "bedrock-runtime" is the data plane: actually run a model (converse,
  converse_stream, invoke_model).
Docent uses bedrock-runtime.

## Region and model
The region is part of the endpoint and decides which models are reachable.
Model access is enabled per region in the Bedrock console. The region and
the model ID in .env must belong together. Some models need an inference
profile ID instead of a plain model ID.

## Request shape
messages is a list. Each message has a role ("user" or "assistant") and a
content list of blocks. A text block looks like {"text": "..."}. Other block
types include image, document, toolUse and toolResult, which is why content
is a list and not a string. The model has no memory between calls, so the
full history is sent every time.

## Response shape
The answer is at response["output"]["message"]["content"][0]["text"]:
response (dict) -> output (dict) -> message (dict) -> content (list) ->
first block (dict) -> text (string).
Other top-level fields: stopReason, usage (inputTokens, outputTokens,
totalTokens) and metrics.

## maxTokens and stopReason
maxTokens limits the output in tokens, not words. A token is roughly
three-quarters of a word. When the limit cuts the answer short, nothing
fails: the text just ends early and stopReason is "max_tokens" instead of
"end_turn". Code must check stopReason to know why the model stopped. When
the model wants to use a tool, stopReason is "tool_use".

## Errors
Errors returned by AWS arrive as botocore ClientError. The code is in
error.response["Error"]["Code"], for example ValidationException or
AccessDeniedException. Re-raising with a bare raise keeps the real error
visible. Without it the script would continue and fail later with a
confusing NameError. A badly formed local call, such as modelId=None, raises
ParamValidationError, which is not a ClientError.

## CountTokens
The API has a CountTokens operation, but not every model supports it. My
model returned "The provided model doesn't support counting tokens". The
usage field in a real response gives exact token counts after the call.
