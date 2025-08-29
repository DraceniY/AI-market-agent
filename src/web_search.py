import json
import datetime
from pathlib import Path
from ddgs import DDGS
from strands import tool


def save_search_data(
    search_type: str, query: str, results_data: dict, raw_results: str
):
    """Save search data to ../data/ directory relative to current working directory"""

    try:
        # Get current working directory and create data path
        current_dir = Path.cwd()
        data_dir = current_dir.parent / "data"
        data_dir.mkdir(parents=True, exist_ok=True)

        # Create timestamped filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{search_type}_{timestamp}.json"
        filepath = data_dir / filename

        save_data = {
            "metadata": {
                "search_type": search_type,
                "original_query": query,
                "timestamp": datetime.datetime.now().isoformat(),
                "pwd": str(current_dir),
                "saved_to": str(filepath),
            },
            "search_results": results_data,
            "formatted_output": raw_results,
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(save_data, f, indent=2, ensure_ascii=False, default=str)

        print(f"Search data saved to: {filepath}")
        return str(filepath)

    except Exception as e:
        print(f"Error saving search data: {str(e)}")
        return None


@tool
def advanced_product_search(query: str) -> str:
    """Advanced product data search with multiple sources"""
    try:
        ddgs = DDGS()
        search_queries = [
            f"{query} price retail cost MSRP",
            f"{query} availability stock inventory",
            f"{query} popularity trends demand 2025",
        ]

        all_results = []
        raw_search_data = {"queries": [], "total_results": 0}

        for search_query in search_queries:
            results = ddgs.text(search_query, max_results=10)
            query_data = {
                "search_query": search_query,
                "results_count": len(results),
                "results": [],
            }

            for i, result in enumerate(results, 1):
                result_data = {
                    "title": result.get("title", "No title"),
                    "content": result.get("body", "No content"),
                    "url": result.get("href", "No URL"),
                }
                query_data["results"].append(result_data)

                all_results.append(
                    f"SEARCH: {search_query}\n"
                    f"RESULT {i}:\n"
                    f"Title: {result_data['title']}\n"
                    f"Content: {result_data['content']}\n"
                    f"URL: {result_data['url']}\n"
                    f"---\n"
                )

            raw_search_data["queries"].append(query_data)
            raw_search_data["total_results"] += len(results)

        formatted_output = (
            "\n".join(all_results) if all_results else "No product data found."
        )
        save_search_data("product_search", query, raw_search_data, formatted_output)

        return formatted_output

    except Exception as e:
        error_msg = f"Product search error: {str(e)}"
        # Save error data too
        save_search_data("product_search_error", query, {"error": str(e)}, error_msg)
        return error_msg


@tool
def advanced_competitor_search(query: str) -> str:
    """Advanced competitor analysis search"""
    try:
        ddgs = DDGS()
        search_queries = [
            f"{query} vs competitors comparison",
            f"{query} market share analysis 2025",
            f"{query} competitive landscape sneaker market",
        ]

        all_results = []
        raw_search_data = {"queries": [], "total_results": 0}

        for search_query in search_queries:
            results = ddgs.text(search_query, max_results=10)
            query_data = {
                "search_query": search_query,
                "results_count": len(results),
                "results": [],
            }

            for i, result in enumerate(results, 1):
                result_data = {
                    "title": result.get("title", "No title"),
                    "content": result.get("body", "No content"),
                    "url": result.get("href", "No URL"),
                }
                query_data["results"].append(result_data)

                all_results.append(
                    f"COMPETITOR SEARCH: {search_query}\n"
                    f"RESULT {i}:\n"
                    f"Title: {result_data['title']}\n"
                    f"Content: {result_data['content']}\n"
                    f"URL: {result_data['url']}\n"
                    f"---\n"
                )

            raw_search_data["queries"].append(query_data)
            raw_search_data["total_results"] += len(results)

        formatted_output = (
            "\n".join(all_results) if all_results else "No competitor data found."
        )

        # Save search data
        save_search_data("competitor_search", query, raw_search_data, formatted_output)

        return formatted_output

    except Exception as e:
        error_msg = f"Competitor search error: {str(e)}"
        save_search_data("competitor_search_error", query, {"error": str(e)}, error_msg)
        return error_msg


@tool
def advanced_sentiment_search(query: str) -> str:
    """Advanced customer sentiment search"""
    try:
        ddgs = DDGS()
        search_queries = [
            f"{query} customer reviews ratings",
            f"{query} user experience feedback",
            f"{query} complaints issues problems",
        ]

        all_results = []
        raw_search_data = {"queries": [], "total_results": 0}

        for search_query in search_queries:
            results = ddgs.text(search_query, max_results=10)
            query_data = {
                "search_query": search_query,
                "results_count": len(results),
                "results": [],
            }

            for i, result in enumerate(results, 1):
                result_data = {
                    "title": result.get("title", "No title"),
                    "content": result.get("body", "No content"),
                    "url": result.get("href", "No URL"),
                }
                query_data["results"].append(result_data)

                all_results.append(
                    f"SENTIMENT SEARCH: {search_query}\n"
                    f"RESULT {i}:\n"
                    f"Title: {result_data['title']}\n"
                    f"Content: {result_data['content']}\n"
                    f"URL: {result_data['url']}\n"
                    f"---\n"
                )

            raw_search_data["queries"].append(query_data)
            raw_search_data["total_results"] += len(results)

        formatted_output = (
            "\n".join(all_results) if all_results else "No sentiment data found."
        )

        # Save search data
        save_search_data("sentiment_search", query, raw_search_data, formatted_output)

        return formatted_output

    except Exception as e:
        error_msg = f"Sentiment search error: {str(e)}"
        save_search_data("sentiment_search_error", query, {"error": str(e)}, error_msg)
        return error_msg


def list_saved_searches(search_type: str = None) -> list:
    """List all saved search files in ../data/ directory"""
    try:
        current_dir = Path.cwd()
        data_dir = current_dir.parent / "data"

        if not data_dir.exists():
            return []

        pattern = f"{search_type}_*.json" if search_type else "*.json"
        files = list(data_dir.glob(pattern))
        return [str(f) for f in sorted(files, reverse=True)]

    except Exception as e:
        print(f"Error listing saved searches: {str(e)}")
        return []


# Function to load saved search data
def load_saved_search(filepath: str) -> dict:
    """Load a saved search file"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading search file {filepath}: {str(e)}")
        return {}


# Example usage and testing
if __name__ == "__main__":
    # Test the search functions
    print("Testing search functions with data saving...")

    # Test product search
    _ = advanced_product_search("new balance 530")
    _ = advanced_competitor_search("new balance 530")
    _ = advanced_sentiment_search("new balance 530")
    print("Product search completed")

    # List saved files
    saved_files = list_saved_searches()
    print(f"Saved search files: {saved_files}")

    # Load and inspect a saved file
    if saved_files:
        data = load_saved_search(saved_files[0])
        print(f"Sample saved data keys: {list(data.keys())}")
