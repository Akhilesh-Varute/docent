"""The tool descriptions we send to Bedrock (the toolConfig parameter)."""

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

