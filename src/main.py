import json
import logging
from pathlib import Path
from typing import Dict, Any
import pandas as pd
import argparse
import sys 

from agents import (
    run_orchestrated_analysis,
    run_analysis_simple,
    configure_telemetry_environment,
)
from dashboard import create_executive_dashboard, open_dashboard
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def save_analysis_results(result: Dict[str, Any], query: str) -> str:
    """Save analysis results to ../results/ directory"""

    try:
        # Get current working directory and create results path
        current_dir = Path.cwd()
        results_dir = current_dir.parent / "results"

        # Create results directory if it doesn't exist
        results_dir.mkdir(parents=True, exist_ok=True)

        # Create timestamped filename
        timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
        # Clean query for filename (remove spaces and special characters)
        clean_query = "".join(
            c for c in query if c.isalnum() or c in (" ", "-", "_")
        ).rstrip()
        clean_query = clean_query.replace(" ", "_")[:50]  # Max 50 chars

        filename = f"analysis_result_{clean_query}_{timestamp}.json"
        filepath = results_dir / filename

        # Add save metadata to result
        result_with_metadata = result.copy()
        result_with_metadata["save_metadata"] = {
            "saved_at": pd.Timestamp.now().isoformat(),
            "saved_to": str(filepath),
            "pwd": str(current_dir),
            "filename": filename,
        }

        # Save to file
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(
                result_with_metadata, f, indent=2, ensure_ascii=False, default=str
            )

        logger.info(f"Analysis results saved to: {filepath}")
        return str(filepath)

    except Exception as e:
        logger.error(f"Error saving analysis results: {str(e)}")
        return None


def generate_and_save_dashboard(result: Dict[str, Any], query: str) -> str:
    """Generate and save executive dashboard"""

    try:
        logger.info("Generating executive dashboard...")
        dashboard_path = create_executive_dashboard(result)
        logger.info(f"Executive dashboard saved to: {dashboard_path}")
        return dashboard_path

    except Exception as e:
        logger.error(f"Error generating dashboard: {str(e)}")
        return None


def print_analysis_summary(result: Dict[str, Any]) -> None:
    """Print a formatted summary of the analysis results"""

    print("\n" + "=" * 80)
    print("MULTI-AGENT E-COMMERCE ANALYSIS SUMMARY")
    print("=" * 80)

    # Basic info
    print(f"Product Analyzed: {result.get('query', 'Unknown')}")
    print(f"Analysis Date: {result.get('timestamp', 'Unknown')}")

    # Session info if available
    if "session_id" in result:
        print(f"Session ID: {result['session_id']}")

    # Execution summary
    exec_summary = result.get("execution_summary", {})
    agents_completed = exec_summary.get("agents_completed", 0)
    total_agents = exec_summary.get("total_agents", 3)
    orchestration_success = exec_summary.get("orchestration_success", False)

    print(f"\nExecution Status:")
    print(f"  Agents Completed: {agents_completed}/{total_agents}")
    print(f"  Orchestration: {'Success' if orchestration_success else 'Failed'}")

    # Telemetry info if available
    if "telemetry_enabled" in exec_summary:
        telemetry_status = (
            "Enabled" if exec_summary["telemetry_enabled"] else "Disabled"
        )
        context_status = (
            "Set" if exec_summary.get("telemetry_context_set", False) else "Not Set"
        )
        print(f"  Telemetry: {telemetry_status} (Context: {context_status})")

    # Key business metrics
    orchestrated = result.get("orchestrated_analysis", {})
    if orchestrated and not orchestrated.get("error"):
        kpis = orchestrated.get("kpi_dashboard", {})
        if kpis:
            print(f"\nBusiness Metrics:")
            print(
                f"  Overall Market Score: {kpis.get('overall_market_score', 'N/A')}/100"
            )
            print(
                f"  Customer Satisfaction: {kpis.get('customer_satisfaction', 'N/A')}/100"
            )
            print(
                f"  Competitive Strength: {kpis.get('competitive_strength', 'N/A')}/100"
            )
            print(f"  Growth Potential: {kpis.get('growth_potential', 'N/A')}/100")

    # Individual agent results
    specialist_agents = result.get("specialist_agents", {})
    print(f"\nAgent Results:")

    for agent_name, agent_result in specialist_agents.items():
        if agent_result.get("error"):
            print(
                f"  {agent_name.capitalize()}: Failed - {agent_result.get('error', 'Unknown error')}"
            )
        else:
            print(f"  {agent_name.capitalize()}: Success")

            # Show key insights if available
            if agent_name == "product" and "price_analysis" in agent_result:
                price = agent_result.get("price_analysis", {}).get(
                    "current_price", "Unknown"
                )
                popularity = agent_result.get("popularity_metrics", {}).get(
                    "popularity_score", "Unknown"
                )
                print(f"    - Price: {price} | Popularity: {popularity}/100")

            elif agent_name == "competitor" and "competitor_landscape" in agent_result:
                competitors = agent_result.get("competitor_landscape", {}).get(
                    "primary_competitors", []
                )
                if competitors:
                    print(f"    - Top Competitors: {', '.join(competitors[:3])}")

            elif agent_name == "sentiment" and "sentiment_overview" in agent_result:
                sentiment = agent_result.get("sentiment_overview", {}).get(
                    "overall_sentiment", "Unknown"
                )
                print(f"    - Customer Sentiment: {sentiment}/10")

    # Strategic insights
    if orchestrated and not orchestrated.get("error"):
        recommendations = orchestrated.get("strategic_recommendations", [])
        if recommendations:
            print(f"\nTop Strategic Recommendations:")
            for i, rec in enumerate(recommendations[:3], 1):
                if isinstance(rec, dict):
                    priority = rec.get("priority", "Medium")
                    rec_text = rec.get("recommendation", str(rec))
                    print(f"    {i}. [{priority}] {rec_text[:80]}...")
                else:
                    print(f"    {i}. {str(rec)[:80]}...")

    print("\n" + "=" * 80)


def analyze_product(
    product_query: str,
    session_id: str = None,
    save_results: bool = True,
    simple_mode: bool = False,
    generate_dashboard: bool = True,
    open_dashboard_browser: bool = True,
) -> Dict[str, Any]:
    """Main function to analyze a product using multi-agent system"""

    logger.info(f"Starting multi-agent analysis for: {product_query}")

    try:
        # Choose analysis mode
        if simple_mode:
            logger.info("Running in simple mode (no telemetry)")
            result = run_analysis_simple(product_query)
        else:
            logger.info("Running with optional telemetry support")
            result = run_orchestrated_analysis(product_query, session_id)

        # Save results if requested
        saved_path = None
        if save_results:
            saved_path = save_analysis_results(result, product_query)
            if saved_path:
                result["saved_to"] = saved_path

        # Generate dashboard if requested and analysis was successful
        dashboard_path = None
        if generate_dashboard and not result.get("error"):
            dashboard_path = generate_and_save_dashboard(result, product_query)
            if dashboard_path:
                result["dashboard_path"] = dashboard_path

                # Open in browser if requested
                if open_dashboard_browser:
                    logger.info("Opening executive dashboard in browser...")
                    open_dashboard(dashboard_path)

        # Print summary
        print_analysis_summary(result)

        # Final status
        if result.get("error"):
            print(f"Analysis failed: {result['error']}")
        else:
            success_rate = (
                result["execution_summary"]["agents_completed"]
                / result["execution_summary"]["total_agents"]
            )
            print(f"Analysis completed with {success_rate:.1%} agent success rate")

        if saved_path:
            print(f"Results saved to: {saved_path}")

        if dashboard_path:
            print(f"Executive dashboard: {dashboard_path}")

        return result

    except Exception as e:
        error_result = {
            "query": product_query,
            "timestamp": pd.Timestamp.now().isoformat(),
            "error": f"Main execution failed: {str(e)}",
            "execution_summary": {
                "agents_completed": 0,
                "total_agents": 3,
                "orchestration_success": False,
            },
        }

        if session_id:
            error_result["session_id"] = session_id

        if save_results:
            save_analysis_results(error_result, product_query)

        logger.error(f"Main execution failed: {str(e)}")
        print(f"Analysis failed: {str(e)}")
        return error_result


def main():
    """Main entry point with command line argument support"""

    parser = argparse.ArgumentParser(
        description="Multi-Agent E-commerce Analysis System with Executive Dashboard"
    )
    parser.add_argument(
        "query",
        nargs="?",
        default="Adidas Samba sneakers",
        help='Product to analyze (default: "Adidas Samba sneakers")',
    )
    parser.add_argument(
        "--no-save", action="store_true", help="Do not save results to file"
    )
    parser.add_argument(
        "--no-dashboard",
        action="store_true",
        help="Do not generate executive dashboard",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Do not open dashboard in browser automatically",
    )
    parser.add_argument(
        "--session-id",
        type=str,
        help="Session ID to associate with this agent run (optional)",
    )
    parser.add_argument(
        "--simple",
        action="store_true",
        help="Run in simple mode without telemetry features",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    # Dashboard-only mode
    parser.add_argument(
        "--dashboard-only",
        type=str,
        help="Generate dashboard from existing JSON analysis file",
    )

    args = parser.parse_args()

    # Dashboard-only mode
    if args.dashboard_only:
        try:
            from dashboard import generate_dashboard_from_json, open_dashboard

            dashboard_path = generate_dashboard_from_json(args.dashboard_only)
            print(f"Dashboard generated from: {args.dashboard_only}")
            print(f"Dashboard saved to: {dashboard_path}")
            if not args.no_browser:
                open_dashboard(dashboard_path)
        except Exception as e:
            print(f"Error generating dashboard: {str(e)}")
        return

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.getLogger("agents").setLevel(logging.DEBUG)

    # Configure telemetry environment if not in simple mode
    if not args.simple:
        configure_telemetry_environment()

    # Run analysis
    print("Multi-Agent E-commerce Analysis System with Executive Dashboard")
    print("=============================================================")
    print(f"Analyzing: {args.query}")

    if args.simple:
        print("Mode: Simple (no telemetry)")
    else:
        print(
            f"Mode: Full featured{' with session tracking' if args.session_id else ''}"
        )

    if args.no_dashboard:
        print("Dashboard: Disabled")
    else:
        print("Dashboard: Executive BI dashboard will be generated")

    result = analyze_product(
        product_query=args.query,
        save_results=not args.no_save,
        session_id=args.session_id,
        simple_mode=args.simple,
        generate_dashboard=not args.no_dashboard,
        open_dashboard_browser=not args.no_browser,
    )

    logfile = open("run.log", "w")
    sys.stdout = logfile
    sys.stderr = logfile
if __name__ == "__main__":
    # Example usage:
    # python main.py "Nike Air Jordan 1"
    # python main.py "iPhone 15" --verbose
    # python main.py "Tesla Model 3" --no-save --no-dashboard
    # python main.py "Adidas Stan Smith" --session-id "session-1234"
    # python main.py "Samsung Galaxy" --simple  # No telemetry, no dashboard
    # python main.py --dashboard-only "../results/analysis_result_Adidas_Stan_Smith_20250829_090526.json"

    final_result = main()
