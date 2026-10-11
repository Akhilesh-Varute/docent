import os
import sys
import json

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

from tool_config import TOOL_CONFIG
from tools import get_document, search_docs

load_dotenv()
region = os.getenv("AWS_REGION")
model_id = os.getenv("BEDROCK_MODEL_ID")

client = boto3.client("bedrock-runtime", region_name=region)

# Maps the tool name the model sends (a string) to the real Python function
TOOLS = {
    "search_docs": search_docs,
    "get_document": get_document,
}

# Safety stop: never loop forever, even if the model keeps asking for tools
MAX_TURNS = 5


def run_tool(tool_use):
    """Run the function the model asked for and wrap the result as a toolResult."""
    function = TOOLS[tool_use["name"]]
    result = function(**tool_use["input"])  # ** turns {"query": "x"} into query="x"

    return {
        "toolResult": {
            "toolUseId": tool_use["toolUseId"],  # must match the model's request
            "content": [{"text": json.dumps(result)}],
            "status": "success",
        }
    }


def get_text(message):
    """Join all text blocks of a message into one string."""
    return "".join(block["text"] for block in message["content"] if "text" in block)


def ask(question):
    """Ask a question; let the model use tools until it gives a final answer."""
    messages = [{"role": "user", "content": [{"text": question}]}]

    for turn in range(1, MAX_TURNS + 1):
        try:
            response = client.converse(
                modelId=model_id,
                messages=messages,
                toolConfig=TOOL_CONFIG,
                inferenceConfig={"maxTokens": 1000},
            )
        except ClientError as error:
            print(f"Bedrock call failed with error: {error}")
            raise

        assistant_message = response["output"]["message"]
        messages.append(assistant_message)  # the history must include the model's turn
        print(f"[turn {turn}] stopReason = {response['stopReason']}")

        if response["stopReason"] != "tool_use":
            return get_text(assistant_message)  # final answer, loop ends

        tool_results = []
        for block in assistant_message["content"]:
            if "toolUse" in block:
                tool_use = block["toolUse"]
                print(f"[turn {turn}] model called {tool_use['name']} with {tool_use['input']}")
                tool_results.append(run_tool(tool_use))

        # All results go back together in ONE user message
        messages.append({"role": "user", "content": tool_results})

    return "Stopped: reached the maximum number of turns without a final answer."


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    print(ask("What does my EcoScheduler doc say about AssumeRole?"))
