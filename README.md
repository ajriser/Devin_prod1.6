# Multimodal Data Analyzer

A Flask-based web application that connects to databases, analyzes data, and generates visualizations and reports.

## Features

- **Data Sources**: Upload CSV, Excel, or JSON files, or connect to Snowflake and SQL Server databases
- **PDF Context**: Upload PDF documents to provide context and definitions for analysis
- **EDA Analysis**: Exploratory data analysis including statistics, correlations, data quality reports, and outlier detection
- **Visualizations**: Generate interactive charts (bar, line, scatter, histogram, box, pie, heatmap) using Plotly
- **Reports**: Export analysis results to PDF, Excel, CSV, or JSON formats

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd multimodal-llm-analyzer
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

## Configuration

Edit the `.env` file with your credentials:

```
# Snowflake Configuration (optional)
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_WAREHOUSE=your_warehouse
SNOWFLAKE_DATABASE=your_database
SNOWFLAKE_SCHEMA=your_schema

# SQL Server Configuration (optional)
SQLSERVER_HOST=your_host
SQLSERVER_PORT=1433
SQLSERVER_DATABASE=your_database
SQLSERVER_USER=your_username
SQLSERVER_PASSWORD=your_password
```

## Running the Application

```bash
python run.py
```

The application will be available at `http://localhost:5000`

## Usage

1. **Load Data**: Upload a file (CSV, Excel, JSON) or connect to a database
2. **Add Context** (Optional): Upload PDF documents to provide context for analysis
3. **Analyze**: Use EDA tools to explore your data
4. **Visualize**: Create charts and graphs
5. **Export**: Download reports in various formats

## Project Structure

```
multimodal-llm-analyzer/
├── app/
│   ├── __init__.py      # Flask app factory
│   └── routes.py        # API routes
├── tools/
│   ├── snowflake_tool.py    # Snowflake connector
│   ├── sqlserver_tool.py    # SQL Server connector
│   ├── pdf_loader_tool.py   # PDF document loader
│   ├── eda_tool.py          # EDA analysis
│   ├── chart_tool.py        # Chart generation
│   └── report_tool.py       # Report generation
├── templates/
│   └── index.html       # Main UI template
├── static/
│   ├── css/style.css    # Styles
│   └── js/app.js        # Frontend JavaScript
├── uploads/             # Uploaded files
├── reports/             # Generated reports
├── requirements.txt     # Python dependencies
├── run.py              # Application entry point
└── .env.example        # Environment variables template
```

## Requirements

- Python 3.9+
- (Optional) Snowflake account for Snowflake connectivity
- (Optional) SQL Server for SQL Server connectivity

## License

MIT License
