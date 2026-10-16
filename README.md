
# SQL & Power BI Portfolio

### Project 002 | SolSystemsDev
**Developer:** Jonathon McDonnell  
**Location:** San Antonio, Texas  
**Version:** 0.1  
**Status:** Module 1 — Financial Budget vs. Actual Analytics

---

## Project Overview

A professional data analytics and business intelligence portfolio demonstrating SQL development, Power BI modeling, Python ETL pipelines, financial analysis, automated reporting, and data governance.

This repository contains reproducible analytical projects inspired by practical business challenges encountered in finance, operations, logistics, and enterprise reporting.

### Technical Focus

- SQL Server and T-SQL
- SQL data extraction and transformation
- Power BI and DAX
- Power Query (M Language)
- Python data engineering
- ETL pipeline development
- Relational data modeling
- Financial variance analysis
- KPI development and executive reporting
- Data quality and reconciliation
- Automated testing
- Business intelligence architecture

**All datasets are synthetic. No employer-owned information, proprietary systems, confidential data, or source code are included.**

---

## Repository Development Roadmap

| Module | Project | Status |
|---|---|---|
| 01 | Financial Budget vs. Actual Analytics | v0.1 Developed |
| 02 | Sales & Commission Analytics | Planned |
| 03 | Supply Chain & Inventory Analytics | Planned |
| 04 | Data Engineering & Governance | Planned |

---

# Module 01 — Financial Budget vs. Actual Analytics

## Business Problem

Organizations require accurate, timely financial reporting to monitor departmental expenditures, identify budget variances, and support management decisions.

Traditional reporting processes often involve manual data extraction, inconsistent general ledger classifications, fragmented financial systems, and time-consuming reconciliation.

This project demonstrates how SQL, Python, and Power BI modeling techniques can create a standardized financial reporting framework.

## Project Objectives

1. Automate financial data preparation.
2. Standardize general ledger expense classifications.
3. Support an October–September fiscal calendar.
4. Compare budgeted and actual expenses.
5. Calculate monthly and fiscal year-to-date variances.
6. Identify unfavorable spending trends.
7. Provide departmental and GL-level financial reporting.
8. Implement automated validation and reconciliation.
9. Generate management-ready visual reports.
10. Establish reusable analytical components.

---

## Financial Reporting Methodology

### Fiscal Calendar

The financial model uses an October–September fiscal year.

| Fiscal Quarter | Months |
|---|---|
| Q1 | October – December |
| Q2 | January – March |
| Q3 | April – June |
| Q4 | July – September |

FY2026 represents October 1, 2025, through September 30, 2026.

Fiscal year labels refer to the calendar year in which the fiscal year ends.

### Expense Classifications

Financial expenses are classified into two primary categories:

**Labor Expenses**
- Salaries and wages
- Overtime
- Employee benefits
- Payroll-related expenses

**Non-Labor Expenses**
- Materials and supplies
- Repairs and maintenance
- Contracted services
- Utilities and operational expenses

These classifications allow management to analyze cost composition and spending trends.

---

## Financial KPI Definitions

### Budget

The approved spending allocation for a specified reporting period.

### Actual Expenses

Total expenses recorded during the reporting period.

### Expense Variance ($)

```text
Expense Variance = Actual Expenses - Budget
```

Positive values indicate unfavorable overspending.

Negative values indicate favorable underspending.

### Expense Variance (%)

```text
Expense Variance % = (Actual Expenses - Budget) / Budget
```

### Fiscal Year-to-Date Budget

Cumulative budget from October through the selected fiscal period.

### Fiscal Year-to-Date Actual

Cumulative actual expenses from October through the selected fiscal period.

### Fiscal Year-to-Date Variance

```text
FYTD Variance = FYTD Actual - FYTD Budget
```

### Labor Expense Percentage

```text
Labor Expense % = Labor Expenses / Total Expenses
```

### Budget Utilization

```text
Budget Utilization % = Actual Expenses / Budget
```

These indicators support financial performance monitoring across reporting periods, departments, and GL accounts.

---

## Synthetic Financial Dataset

The project generates fictional financial data using a deterministic Python generator.

The synthetic model includes:

- Departmental reference data
- General ledger accounts
- Labor and non-labor classifications
- Monthly budget allocations
- Transaction-level expenses
- Fiscal calendar attributes
- Department and GL reporting relationships

No actual employer financial records are used.

### FY2026 Example Results

| Metric | Synthetic Value |
|---|---:|
| Annual Budget | $31,109,140.29 |
| Actual Expenses | $31,352,851.47 |
| Unfavorable Variance | $243,711.18 |
| Expense Classifications | Labor / Non-Labor |
| Fiscal Year | October 2025 – September 2026 |
| Synthetic Budget Records | 1,152 across FY2025–FY2026 |
| Synthetic Transactions | 3,465 across FY2025–FY2026 |

These figures are generated strictly for demonstration and testing.

---

## Data Engineering Architecture

### ETL Pipeline

The analytical workflow follows a repeatable Extract, Transform, Load process.

```text
Synthetic Financial Data
          |
          v
Python Data Generation
          |
          v
Data Cleaning & Validation
          |
          v
SQLite Relational Database
          |
          v
SQL Transformations
          |
          v
Budget vs. Actual Reporting Views
          |
          v
Financial KPI Calculations
          |
          v
CSV / JSON Reporting Outputs
          |
          v
Executive HTML Dashboard
```

### Transformation Operations

- Fiscal calendar mapping
- Department normalization
- GL expense classification
- Monthly transaction aggregation
- Budget-to-actual matching
- Duplicate prevention
- Variance calculation
- Data reconciliation
- Exception identification

Financial amounts are maintained in integer cents during processing to reduce rounding discrepancies.

---

## SQL Development

Module 1 includes executable SQLite transformations and SQL Server/T-SQL implementation examples.

### SQL Techniques Demonstrated

- Relational table design
- Primary and foreign keys
- SQL joins
- Common table expressions
- Conditional aggregations
- Grouping and summarization
- Reporting views
- Data integrity constraints
- Query indexing
- Financial reconciliation

### SQL Server / T-SQL

Separate scripts illustrate enterprise SQL Server implementation patterns.

The primary executable pipeline uses SQLite to allow deployment without a dedicated database server.

The T-SQL examples are implementation references and have not yet been validated against a running SQL Server instance.

---

## Power BI Development

The repository includes Power BI modeling references designed to support reconstruction of the financial dashboard in Power BI Desktop.

### DAX Measures

Examples include:

- Total Budget
- Total Actual Expenses
- Expense Variance
- Expense Variance %
- Fiscal YTD Budget
- Fiscal YTD Actual
- Fiscal YTD Variance
- Labor Expenses
- Non-Labor Expenses
- Labor Expense Percentage

### Power Query

Power Query examples demonstrate financial data preparation and fiscal-calendar transformations.

### Proposed Dashboard Layout

**Executive Summary**
- Total Budget
- Total Actual
- Variance $
- Variance %
- Budget utilization

**Departmental Performance**
- Budget vs. Actual by department
- Department expense distribution
- Unfavorable variance rankings

**General Ledger Analysis**
- GL category breakdown
- Labor vs. Non-Labor
- Monthly expense trends

**Fiscal Analysis**
- Monthly budget variance
- Fiscal YTD comparison
- Quarterly expense trends

**Data Quality**
- Reconciliation results
- Missing classifications
- Validation exceptions

**Power BI Status:** DAX and Power Query examples are included. A working `.pbix` file has not yet been created or verified.

---

## Executive Reporting

The Python pipeline generates an HTML financial dashboard and SVG visualization.

### Available Reports

[Executive Financial Dashboard](reports/executive_dashboard.html)

[Monthly Expense Visualization](reports/charts/monthly_spend.svg)

### Reporting Capabilities

- Financial KPI summary
- Budget vs. Actual analysis
- Departmental expense reporting
- GL category analysis
- Monthly spending trends
- Financial exception reporting

These outputs can be viewed without installing Power BI Desktop.

---

## Repository Structure

```text
sql-powerbi-portfolio/
|
|-- README.md
|-- requirements.txt
|
|-- data/
|   |-- synthetic/
|   |-- processed/
|
|-- src/
|   |-- finance_portfolio/
|       |-- generator.py
|       |-- pipeline.py
|       |-- rendering.py
|
|-- scripts/
|   |-- build.py
|
|-- sql/
|   |-- sqlite/
|   |-- tsql/
|
|-- powerbi/
|   |-- dax/
|   |-- power_query/
|   |-- README.md
|
|-- docs/
|   |-- data_model.md
|   |-- validation.md
|
|-- reports/
|   |-- executive_dashboard.html
|   |-- charts/
|
|-- tests/
|   |-- test_portfolio.py
|
|-- .github/
    |-- workflows/
        |-- validate.yml
```

---

## Running the Project

### Requirements

- Python 3.11 or newer
- GitHub Codespaces or a local development environment
- No external Python packages required for v0.1

### Step 1 — Clone the Repository

```bash
git clone https://github.com/SolSystemsDev/sql-powerbi-portfolio.git
```

### Step 2 — Enter the Project Directory

```bash
cd sql-powerbi-portfolio
```

### Step 3 — Execute the ETL Pipeline

```bash
python3 scripts/build.py
```

The script generates synthetic financial data, processes the reporting model, validates reconciliations, and produces financial reports.

### Step 4 — Run Automated Tests

```bash
python3 -m unittest discover -s tests -v
```

The v0.1 project includes 11 automated tests covering fiscal logic, source determinism, financial reconciliation, classification, and data integrity.

Expected result:

```text
Ran 11 tests

OK
```

### Step 5 — Review Reports

After a successful build, open:

```text
reports/executive_dashboard.html
```

Additional generated datasets and reports are available in their respective directories.

---

## Data Quality & Governance

Financial reporting accuracy depends on consistent data structures and validation controls.

This project demonstrates several governance practices.

### Data Validation

- Required field checks
- Fiscal-period validation
- GL classification verification
- Relational integrity testing
- Source-to-report reconciliation
- Duplicate prevention

### Reconciliation

The ETL pipeline checks that financial transaction totals reconcile to reporting outputs.

### Exception Reporting

The reporting process identifies unfavorable expense variances for management review.

### Reproducibility

Synthetic data generation uses deterministic inputs so results can be recreated and compared across executions.

---

## Automated Testing

The project uses Python's built-in `unittest` framework.

Testing covers:

- Fiscal calendar calculations
- October–September year transitions
- Fiscal quarter assignments
- Deterministic data generation
- Financial aggregation
- Reconciliation accuracy
- Foreign-key enforcement
- Expense classification
- Variance sign conventions

GitHub Actions configuration is included to support automated validation after code changes.

---

# Module 02 — Sales & Commission Analytics

**Status: Planned**

This module will demonstrate financial and commercial reporting inspired by insurance commission and ERP reconciliation workflows.

### Planned Capabilities

- Producer performance reporting
- Agency commission analysis
- Expected vs. actual commission
- Accounts receivable aging
- Payment discrepancies
- Forecast comparisons
- Client record reconciliation
- SQL matching logic
- Commission KPI dashboards

---

# Module 03 — Supply Chain Analytics

**Status: Planned**

This module will focus on logistics, inventory, and operational reporting.

### Planned Capabilities

- Inventory accuracy
- On-time delivery
- Order fulfillment performance
- Asset utilization
- Logistics expense reporting
- Delivery performance trends
- Exception identification
- SQL-based operational KPIs

---

# Module 04 — Data Engineering & Governance

**Status: Planned**

This module will demonstrate enterprise data engineering principles through practical analytical workflows.

### Planned Capabilities

- ETL architecture
- SQL optimization
- Data validation frameworks
- Data lineage documentation
- Exception reporting
- Data governance controls
- Semantic model design
- Automated pipeline testing
- Reporting standardization

---

## Professional Background

This portfolio reflects technical skills developed through professional experience in business intelligence, finance, engineering, and operational analytics.

### VIA Metropolitan Transit

Experience developing executive financial dashboards, fiscal budget reporting, departmental expense analysis, and automated SQL/Power Query reporting workflows.

### Higginbotham

Experience with Power BI commission reporting, Snowflake SQL, enterprise data reconciliation, and semantic model usage analytics.

### Nexxis

Experience with supply chain reporting, operational dashboards, inventory management analytics, financial operations, and automated SQL reporting.

The repository uses independently developed examples with exclusively synthetic data.

---

## Professional Qualifications

**Education**
- Master of Business Administration — Finance & Process Improvement
- Bachelor of Science — Electrical Engineering

**Certification**
- Six Sigma Green Belt

**Technical Skills**
- SQL Server / T-SQL
- Snowflake SQL
- Power BI
- DAX
- Power Query / M
- Python
- ETL Development
- Data Modeling
- Financial Reporting
- Business Intelligence
- KPI Development
- Data Governance

---

## Project Development Principles

1. Reproducible analytical workflows
2. Clear business requirements
3. Financial calculation accuracy
4. Maintainable SQL and Python code
5. Automated testing and reconciliation
6. Documented data models
7. Practical executive reporting
8. Professional GitHub presentation
9. Transparent implementation status
10. Exclusive use of synthetic data

---

## Author

**Jonathon McDonnell**  
Data Analyst | Business Intelligence | Financial Analytics | Data Engineering

San Antonio, Texas

GitHub: [SolSystemsDev](https://github.com/SolSystemsDev)

LinkedIn: [Jonathon McDonnell](https://www.linkedin.com/in/jonathon-mcdonnell-a9265090/)

---

## Disclaimer

This repository is an independently developed educational and professional portfolio.

All financial figures, departments, general ledger records, and transaction datasets are synthetic.

No confidential information, proprietary code, employer-owned datasets, or actual employer financial records are included.

Any references to previous professional experience describe general skills and responsibilities rather than actual employer reporting systems.

---

**SolSystemsDev | Project 002 | SQL & Power BI Portfolio**
