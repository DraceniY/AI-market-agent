import json
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import webbrowser
from pathlib import Path
from typing import Dict, Any

# Adidas brand colors
ADIDAS_COLORS = {
    "black": "#000000",
    "white": "#FFFFFF",
    "gray": "#767677",
    "blue": "#004CFF",
    "green": "#00A651",
    "orange": "#FF6900",
    "red": "#E31E24",
}


def create_executive_dashboard(analysis_data: Dict[str, Any]) -> str:
    """Create executive dashboard from multi-agent analysis results"""

    # Extract data
    product_name = analysis_data.get("query", "Product")
    timestamp = analysis_data.get("timestamp", "")

    # Agent results
    product_data = analysis_data.get("specialist_agents", {}).get("product", {})
    competitor_data = analysis_data.get("specialist_agents", {}).get("competitor", {})
    sentiment_data = analysis_data.get("specialist_agents", {}).get("sentiment", {})
    orchestrated = analysis_data.get("orchestrated_analysis", {})

    # Create visualizations
    fig = make_subplots(
        rows=3,
        cols=3,
        subplot_titles=(
            "Market Position Score",
            "Competitive Landscape",
            "Customer Sentiment",
            "Price Analysis",
            "Market Trends",
            "Satisfaction Breakdown",
            "Strategic Priorities",
            "Risk Assessment",
            "Growth Opportunities",
        ),
        specs=[
            [{"type": "indicator"}, {"type": "bar"}, {"type": "pie"}],
            [{"type": "scatter"}, {"type": "bar"}, {"type": "bar"}],
            [{"type": "bar"}, {"type": "bar"}, {"type": "scatter"}],
        ],
        vertical_spacing=0.12,
    )

    # 1. Market Position Score (KPI Gauge)
    kpis = orchestrated.get("kpi_dashboard", {})
    overall_score = kpis.get("overall_market_score", 75)

    fig.add_trace(
        go.Indicator(
            mode="gauge+number",
            value=overall_score,
            title={"text": f"{product_name}<br>Market Score"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": ADIDAS_COLORS["black"]},
                "steps": [
                    {"range": [0, 50], "color": "lightgray"},
                    {"range": [50, 80], "color": ADIDAS_COLORS["gray"]},
                    {"range": [80, 100], "color": ADIDAS_COLORS["green"]},
                ],
                "threshold": {
                    "line": {"color": ADIDAS_COLORS["red"], "width": 4},
                    "thickness": 0.75,
                    "value": 85,
                },
            },
        ),
        row=1,
        col=1,
    )

    # 2. Competitive Landscape
    competitors = competitor_data.get("competitor_landscape", {}).get(
        "primary_competitors", []
    )[:5]
    competitor_strength = [85, 70, 60, 55, 45][: len(competitors)]  # Stan Smith leads

    fig.add_trace(
        go.Bar(
            x=competitors,
            y=competitor_strength,
            marker_color=[
                ADIDAS_COLORS["black"]
                if "Stan Smith" in str(comp)
                else ADIDAS_COLORS["gray"]
                for comp in competitors
            ],
            name="Market Strength",
        ),
        row=1,
        col=2,
    )

    # 3. Customer Sentiment Distribution
    positive_themes = sentiment_data.get("positive_sentiment", {}).get("key_themes", [])
    sentiment_values = [25, 20, 18, 15][: len(positive_themes)]

    fig.add_trace(
        go.Pie(
            labels=positive_themes[:4],
            values=sentiment_values,
            marker_colors=[
                ADIDAS_COLORS["green"],
                ADIDAS_COLORS["blue"],
                ADIDAS_COLORS["gray"],
                ADIDAS_COLORS["orange"],
            ],
            hole=0.3,
        ),
        row=1,
        col=3,
    )

    # 4. Price Analysis
    price_range = product_data.get("price_analysis", {}).get("current_price", "$100")
    price_trend = product_data.get("price_analysis", {}).get("price_trend", "stable")

    # Extract numeric price for visualization
    import re

    price_match = re.search(r"\$(\d+)", price_range)
    current_price = int(price_match.group(1)) if price_match else 100

    price_history = [
        95,
        98,
        current_price,
        current_price + 2,
        current_price + 1,
    ]  # Simulated trend
    months = ["Q1", "Q2", "Q3", "Q4", "Current"]

    fig.add_trace(
        go.Scatter(
            x=months,
            y=price_history,
            mode="lines+markers",
            line={"color": ADIDAS_COLORS["blue"], "width": 3},
            marker={"size": 8, "color": ADIDAS_COLORS["black"]},
            name="Price Trend",
        ),
        row=2,
        col=1,
    )

    # 5. Market Trends
    trends = competitor_data.get("market_trends", {}).get("current_trends", [])[:4]
    trend_impact = [8, 7, 6, 5][: len(trends)]

    fig.add_trace(
        go.Bar(
            x=trend_impact,
            y=trends,
            orientation="h",
            marker_color=ADIDAS_COLORS["orange"],
            name="Trend Impact",
        ),
        row=2,
        col=2,
    )

    # 6. Satisfaction Breakdown
    overall_sentiment = sentiment_data.get("sentiment_overview", {}).get(
        "overall_sentiment", 7
    )
    positive_score = sentiment_data.get("positive_sentiment", {}).get("score", 8)
    negative_score = sentiment_data.get("negative_sentiment", {}).get("score", 5)

    satisfaction_categories = ["Overall", "Positive Aspects", "Negative Aspects"]
    scores = [overall_sentiment, positive_score, negative_score]
    colors = [ADIDAS_COLORS["blue"], ADIDAS_COLORS["green"], ADIDAS_COLORS["red"]]

    fig.add_trace(
        go.Bar(
            x=satisfaction_categories,
            y=scores,
            marker_color=colors,
            name="Satisfaction Scores",
        ),
        row=2,
        col=3,
    )

    # 7. Strategic Priorities
    recommendations = orchestrated.get("strategic_recommendations", [])
    priorities = {}
    for rec in recommendations:
        if isinstance(rec, dict):
            priority = rec.get("priority", "Medium")
            priorities[priority] = priorities.get(priority, 0) + 1

    priority_labels = list(priorities.keys()) or ["High", "Medium", "Low"]
    priority_counts = list(priorities.values()) or [2, 2, 1]
    priority_colors = [
        ADIDAS_COLORS["red"],
        ADIDAS_COLORS["orange"],
        ADIDAS_COLORS["gray"],
    ]

    fig.add_trace(
        go.Bar(
            x=priority_labels,
            y=priority_counts,
            marker_color=priority_colors[: len(priority_labels)],
            name="Priority Actions",
        ),
        row=3,
        col=1,
    )

    # 8. Risk Assessment
    risks = orchestrated.get("risk_assessment", [])[:4]
    risk_severity = [9, 7, 6, 4][: len(risks)]

    fig.add_trace(
        go.Bar(
            x=risks,
            y=risk_severity,
            marker_color=ADIDAS_COLORS["red"],
            name="Risk Level",
        ),
        row=3,
        col=2,
    )

    # 9. Growth Opportunities
    opportunities = (
        orchestrated.get("consolidated_insights", {})
        .get("competitive_position", {})
        .get("competitive_advantages", [])[:4]
    )
    opportunity_scores = [8.5, 7.8, 7.2, 6.9][: len(opportunities)]

    fig.add_trace(
        go.Scatter(
            x=opportunity_scores,
            y=opportunities,
            mode="markers",
            marker={
                "size": [score * 5 for score in opportunity_scores],
                "color": ADIDAS_COLORS["green"],
                "opacity": 0.7,
            },
            name="Growth Potential",
        ),
        row=3,
        col=3,
    )

    # Update layout
    fig.update_layout(
        height=1200,
        title={
            "text": f"Intelligent e-commerce Dashboard: {product_name} Strategic Analysis",
            "x": 0.5,
            "font": {
                "size": 24,
                "color": ADIDAS_COLORS["black"],
                "family": "Arial Black",
            },
        },
        font={"family": "Arial", "size": 11},
        showlegend=False,
        plot_bgcolor="white",
        paper_bgcolor="#f8f9fa",
    )

    # Generate HTML
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Intelligent e-commerce Dashboard - {product_name}</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            body {{ 
                font-family: Arial, sans-serif; 
                margin: 0; 
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                color: #333;
            }}
            .header {{ 
                background: linear-gradient(90deg, #000000 0%, #767677 100%);
                color: white; 
                padding: 20px; 
                text-align: center;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            .container {{ 
                max-width: 1400px; 
                margin: 20px auto; 
                padding: 20px; 
            }}
            .insights {{ 
                background: white; 
                padding: 30px; 
                margin: 20px 0; 
                border-radius: 12px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }}
            .insight-grid {{ 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
                gap: 20px; 
            }}
            .insight-box {{ 
                background: #f8f9fa; 
                padding: 20px; 
                border-radius: 8px;
                border-left: 4px solid #000000;
            }}
            .kpi-summary {{ 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
                gap: 20px; 
                margin: 20px 0; 
            }}
            .kpi-card {{ 
                background: linear-gradient(135deg, #000000, #767677);
                color: white; 
                padding: 20px; 
                border-radius: 8px; 
                text-align: center;
            }}
            .kpi-value {{ 
                font-size: 2rem; 
                font-weight: bold; 
                margin-bottom: 5px; 
            }}
            .kpi-label {{ 
                font-size: 0.9rem; 
                opacity: 0.9; 
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>ADIDAS EXECUTIVE DASHBOARD</h1>
            <p>Strategic Intelligence Report: {product_name} | Generated: Yasmine Draceni - {timestamp[:10]}</p>
        </div>
        
        <div class="container">
            <div class="kpi-summary">
                <div class="kpi-card">
                    <div class="kpi-value">{overall_score}/100</div>
                    <div class="kpi-label">Market Position</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-value">{price_range}</div>
                    <div class="kpi-label">Price Range</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-value">{overall_sentiment}/10</div>
                    <div class="kpi-label">Customer Sentiment</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-value">{len(recommendations)}</div>
                    <div class="kpi-label">Strategic Actions</div>
                </div>
            </div>
            
            <div id="dashboard" style="width:100%;height:1200px;"></div>
            
            <div class="insights">
                <h2>Executive Summary</h2>
                <p>{orchestrated.get('executive_summary', 'Analysis completed successfully.')}</p>
                
                <div class="insight-grid">
                    <div class="insight-box">
                        <h4>Key Strengths</h4>
                        <ul>
                            {"".join([f"<li>{adv}</li>" for adv in competitor_data.get('competitor_landscape', {}).get('competitive_advantages', [])[:4]])}
                        </ul>
                    </div>
                    <div class="insight-box">
                        <h4>Customer Concerns</h4>
                        <ul>
                            {"".join([f"<li>{issue}</li>" for issue in sentiment_data.get('negative_sentiment', {}).get('key_issues', [])[:4]])}
                        </ul>
                    </div>
                    <div class="insight-box">
                        <h4>Market Opportunities</h4>
                        <ul>
                            {"".join([f"<li>{opp}</li>" for opp in competitor_data.get('market_share_analysis', {}).get('growth_opportunities', [])[:4]])}
                        </ul>
                    </div>
                    <div class="insight-box">
                        <h4>Next Actions</h4>
                        <ul>
                            {"".join([f"<li>{action}</li>" for action in orchestrated.get('next_actions', [])[:4]])}
                        </ul>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            var plotlyData = {fig.to_json()};
            Plotly.newPlot('dashboard', plotlyData.data, plotlyData.layout, {{responsive: true}});
        </script>
    </body>
    </html>
    """

    # Save dashboard
    current_dir = Path.cwd()
    results_dir = current_dir.parent / "results"
    results_dir.mkdir(exist_ok=True)

    dashboard_file = (
        results_dir
        / f"executive_dashboard_{product_name.replace(' ', '_')}_{timestamp[:10].replace('-', '')}.html"
    )

    with open(dashboard_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    return str(dashboard_file)


def generate_dashboard_from_json(json_file_path: str) -> str:
    """Generate dashboard from saved JSON analysis file"""

    with open(json_file_path, "r", encoding="utf-8") as f:
        analysis_data = json.load(f)

    return create_executive_dashboard(analysis_data)


def open_dashboard(dashboard_path: str):
    """Open dashboard in browser"""
    webbrowser.open(f"file://{Path(dashboard_path).absolute()}")


# Main execution
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        # Generate dashboard from JSON file
        json_path = sys.argv[1]
        dashboard_path = generate_dashboard_from_json(json_path)
        print(f"Dashboard created: {dashboard_path}")
        open_dashboard(dashboard_path)
    else:
        print("Usage: python dashboard.py <path_to_analysis_json>")
        print(
            "Example: python dashboard.py ../results/analysis_result_Adidas_Stan_Smith_20250829_090526.json"
        )
