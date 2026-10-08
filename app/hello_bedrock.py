import os
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()
region = os.getenv("AWS_REGION")
model_id = os.getenv("BEDROCK_MODEL_ID")

client = boto3.client("bedrock-runtime", region_name=region)

messages = [
    {"role": "user", "content": [
        {"text": "Explain what an API is in one sentence."}]}
]

try:
    response = client.converse(
        modelId=model_id,
        messages=messages,
        inferenceConfig={"maxTokens":100},
    )
except ClientError as error:
    print(f"Bedrock call failed with error: {error}")
    raise

answer = response["output"]["message"]["content"][0]["text"]
print(answer)

print(response["usage"])