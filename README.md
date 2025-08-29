# AI E-commerce Intelligence System 
## Project Overview

Multi-agent system for e-commerce for any product.

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Product Agent  │    │Competitor Agent │    │ Sentiment Agent │
│  (Price/Avail.) │    │ (Market/Trends) │    │ (Reviews/Mood)  │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────▼──────────────┐
                    │    Orchestrator Agent      │
                    │   (Strategic Synthesis)    │
                    └─────────────┬──────────────┘
                                 │
                    ┌─────────────▼──────────────┐
                    │    Executive Dashboard     │
                    │   (Reporting)              │
                    └────────────────────────────┘
```

## Key Features

**Multi-Agent Intelligence:**
- Product Intelligence Agent (pricing, availability, popularity)
- Competitive Analysis Agent (market positioning, trends)
- Customer Sentiment Agent (reviews, satisfaction, pain points)
- Orchestrator Agent (strategic synthesis)

**Executive Dashboard:**
- BI visualization
- Adidas brand-compliant design
- Interactive Plotly charts
- Automated insights generation

**Enterprise Features:**
- Docker containerization
- OpenTelemetry observability
- Parallel agent execution
- Session tracking
- Comprehensive monitoring stack

## Quick Start

### Method 1: Make Commands
Before to start, you need to have AWS account otherwise you will not be able to run strands package.
```bash
#You must run the requirements to get the environment locally :
```bash
pip install -r requirements.txt

# Then run run.sh script
bash run.sh

#You can also run in docker using any name of product
# Analyze specific product with dashboard
make analyze-dashboard QUERY="Nike Air Jordan 1"

# View results
ls results/
```

### Method 2: Docker Compose
```bash
# The environment is not set with AWS credentials here is only use as prototype
# Setup environment
docker-compose run --rm ecommerce-agent python main.py --help

# Run analysis with dashboard
docker-compose run --rm ecommerce-agent python main.py "iPhone 15 Pro" --no-browser

```

## File Structure

```
├── data # Search results (auto-generated)
├── logs # logs of each run
├── results # Analysis results & dashboards
│   ├── analysis_result_*.json    # Raw analysis data
│   └── executive_dashboard_*.html # BI dashboards
├── sessions # Agent history session data
│   ├── session_competitor-agent
│   │   └── agents
│   │       └── agent_default
│   │           └── messages
│   ├── session_product-agent
│   │   └── agents
│   │       └── agent_default
│   │           └── messages
│   ├── session_sentiment-agent
│   │   └── agents
│   │       └── agent_default
│   │           └── messages
│   └── session_strategy-agent
│       └── agents
│           └── agent_default
│               └── messages
├── src/     # source
│   ├── main.py                   # Main orchestrator with dashboard integration
│   ├── agents.py                 # Multi-agent system with telemetry
│   ├── dashboard.py              # Executive BI dashboard generator
│   ├── web_search.py             # Web search
│   ├── settings.py               # Configuration management
│   └── config.ini                # Application settings
|
├── Dockerfile                    # Container definition
├── docker-compose.yml           # Complete stack
├── Makefile                     # Build automation
├── run.sh                       # Bash alternative
└── requirements.txt             # Python dependencies
└── tests
```

## Usage Examples

### Standard Analysis
```bash
bash run.sh

```

### Dashboard Only
```bash
# Generate dashboard from existing analysis
python src/main.py --dashboard-only "results/analysis_result_Tesla_Model_3_20250829_120530.json"
```

### Docker Usage
```bash
# Single analysis
make analyze QUERY="Nike Air Max"

# Batch analysis
make analyze-batch

# Dashboard from JSON
make generate-dashboard JSON_FILE="results/analysis_result_iPhone_15_20250829_120530.json"
```

## Dashboard Features

**Executive KPIs:**
- Market Position Score (/100)
- Customer Satisfaction (/10) 
- Competitive Strength (/100)
- Growth Potential (/100)

**Strategic Visualizations:**
- Competitive landscape analysis
- Price trend analysis
- Customer sentiment breakdown
- Market opportunity mapping
- Risk assessment matrix
- Strategic priority ranking

**Business Intelligence:**
- Automated insight extraction
- Priority-based recommendations
- Risk identification
- Growth opportunity analysis

## Configuration

### Environment Variables


```bash
# AWS Configuration (Required)
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=us-west-2
BEDROCK_MODEL_ID=us.anthropic.claude-3-7-sonnet-20250219-v1:0


```

### Model Configuration (config.ini)
```ini
[MODEL_PARAM]
BEDROCK_MODEL_ID = us.anthropic.claude-3-7-sonnet-20250219-v1:0
MODEL_REGION = us-west-2
MODEL_TEMPERATURE = 0.1
MAXIMUM_TOKENS = 3000
SUMMARY_RATIO = 0.2

[PROMPT]
PRODUCT_DATA_PROMPT = You are a PRODUCT INTELLIGENCE SPECIALIST...
COMPETITOR_ANALYST_PROMPT = You are a COMPETITIVE INTELLIGENCE SPECIALIST...
SENTIMENT_ANALYST_PROMPT = You are a CUSTOMER SENTIMENT ANALYST...
ORCHESTRATOR_PROMPT = You are the ORCHESTRATOR AGENT...
```

## Performance Optimization

**Parallel Execution:**
- 3 agents run simultaneously
- ThreadPoolExecutor/AsyncIO support
- Optimal resource utilization

**Caching:**
- Search results cached to ../data/
- Session data persisted

**Resource Management:**
- Container resource limits
- Memory optimization
- Efficient data processing

## Security Considerations and AI responsible

**Agent prompt Security:**
- Non-root user execution
- Minimal attack surface
- Security scanning ready

**Data Protection:**
- No sensitive data in logs
- Environment-based secrets
- Audit trail maintenance


## Business Value

**Executive Benefits:**
- Real-time market intelligence
- Data-driven decision making
- Competitive advantage insights
- Risk mitigation strategies

**Operational Benefits:**
- Automated analysis workflows
- Scalable processing capability
- Comprehensive audit trails
- Integration-ready APIs

## Copyright
For any questions or suggestions, contact me at yasmine.draceni[AT]gmail.com

##### Yasmine Draceni, 2025