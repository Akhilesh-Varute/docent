"""
Day 2 experiment, written by Akhilesh.

Sends one question to Bedrock together with the tool descriptions and prints
the toolUse request the model returns (tool name, input, toolUseId).
It does not run the tool or send a result back.

The complete, working version of this flow lives in:
  - tool_config.py : the tool descriptions (TOOL_CONFIG) sent to the model
  - tool_loop.py   : runs the tools and loops until the model gives a final answer
"""
import os
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
import json

TOOL_CONFIG = {
    "tools": [
        {
            "toolSpec": {
                "name": "search_docs",
                "description": "Search the documents for a word or phrase. "
                "Returns matching document names with a short snippet. "
                "Use this first to find which document to read.",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The word or phrase to search for in the documents.",
                            }
                        },
                        "required": ["query"],
                    }
                },
            }
        },
        {
            "toolSpec": {
                "name": "get_document",
                "description": "Get the full text of a document by name. "
                "Use search_docs first to find a valid document name.",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "The name of the document to retrieve.",
                            }
                        },
                        "required": ["name"],
                    }
                },
            }
        },
    ]
}

load_dotenv()
region = os.getenv("AWS_REGION")
model_id = os.getenv("BEDROCK_MODEL_ID")

client = boto3.client("bedrock-runtime", region_name=region)

messages = [
    {
        "role": "user",
        "content": [{"text": "What does my EcoScheduler doc say about AssumeRole?"}],
    }
]

try:
    response = client.converse(
        modelId=model_id,
        messages=messages,
        toolConfig=TOOL_CONFIG,
        inferenceConfig={"maxTokens": 100},
    )
except ClientError as error:
    print(f"Bedrock call failes with error:{error}")
    raise

for block in response["output"]["message"]["content"]:
    if "toolUse" in block:
        tool_use = block["toolUse"]
        print(json.dumps(tool_use["name"], indent=2, default=str))
        print(json.dumps(tool_use["input"], indent=2, default=str))
        print(json.dumps(tool_use["toolUseId"], indent=2, default=str))
        
           
# print(json.dumps(response["output"]["message"], indent=2, default=str))
# print(response["stopReason"])
