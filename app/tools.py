from pathlib import Path

# tools.py lives in docent/app/, so go up one level to docent/, then into data/
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# Only these file types count as documents
DOC_SUFFIXES = (".md", ".txt")

SNIPPET_CONTEXT = 80  # characters of context to show before and after the match

def get_document(name):
    """Return the full text of one document in data/, or an error message."""
    path = (DATA_DIR / name).resolve()

    # Safety: after resolving "..", the path must still be inside data/
    if not path.is_relative_to(DATA_DIR):
        return f"Error: '{name}' is not a valid document name."

    if not path.is_file():
        return f"Error: document '{name}' not found. Use search_docs to find valid names."

    return path.read_text(encoding="utf-8")


def search_docs(query, max_results=5):
    """Find documents containing the query (case-insensitive).

    Returns a list of {"name": ..., "snippet": ...}, one per matching document.
    """
    query_lower = query.lower()
    results = []

    for path in sorted(DATA_DIR.iterdir()):
        if path.suffix not in DOC_SUFFIXES:
            continue

        text = path.read_text(encoding="utf-8")
        position = text.lower().find(query_lower)
        if position == -1:  # find() returns -1 when there is no match
            continue

        start = max(0, position - SNIPPET_CONTEXT)
        end = position + len(query) + SNIPPET_CONTEXT
        snippet = text[start:end].replace("\n", " ")
        results.append({"name": path.name, "snippet": snippet})

        if len(results) >= max_results:
            break

    return results


if __name__ == "__main__":
    # Quick manual check: python app/tools.py
    # print(DATA_DIR, DATA_DIR.exists())
    print(search_docs("AssumeRole"))
    # print(get_document("nope.md"))
    # print(get_document("../.env"))
    # print(search_docs("Pizza"))
    # print(search_docs(""))