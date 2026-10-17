"""Self-contained HTML executive report and dependency-free SVG chart."""
from html import escape
from pathlib import Path


def money(cents, compact=False):
    if compact:
        return f"${cents / 100_000_000:,.2f}M"
    return f"${cents / 100:,.0f}"


def trend_svg(monthly):
    """Two bars per fiscal month: budget and actual; accessible static SVG."""
    width, height = 1050, 330
    pad_l, plot_top, plot_bottom = 76, 30, 270
    usable_height = plot_bottom - plot_top
    peak = max(max(x["actual_cents"], x["budget_cents"]) for x in monthly) * 1.15
    gap = 74
    bar_w = 24
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
           'role="img" aria-labelledby="chart-title chart-desc">',
           '<title id="chart-title">Monthly budget and actual expenses</title>',
           '<desc id="chart-desc">Paired budget and actual bars for every fiscal month, October to September.</desc>',
           '<rect width="1050" height="330" fill="#ffffff"/>']
    for tick in range(5):
        value = (peak * tick / 4)
        y = plot_bottom - value / peak * usable_height
        svg += [f'<line x1="{pad_l}" y1="{y:.1f}" x2="1026" y2="{y:.1f}" stroke="#e4eaf2"/>',
                f'<text x="{pad_l-8}" y="{y+4:.1f}" text-anchor="end" fill="#62748a" '
                f'font-size="12">{money(value, True)}</text>']
    import calendar
    for i, month in enumerate(monthly):
        x = pad_l + 27 + i * gap
        for index, (key, color) in enumerate((("budget_cents", "#7896ca"), ("actual_cents", "#1b6b81"))):
            h = month[key] / peak * usable_height
            svg.append(f'<rect x="{x + index*bar_w}" y="{plot_bottom-h:.1f}" width="{bar_w-2}" '
                       f'height="{h:.1f}" fill="{color}" rx="3"/>')
        name = calendar.month_abbr[int(month["month_start"][5:7])]
        svg.append(f'<text x="{x+22}" y="{plot_bottom+23}" text-anchor="middle" '
                   f'font-size="13" fill="#334155">{name}</text>')
    svg += ['<rect x="380" y="310" width="11" height="11" rx="2" fill="#7896ca"/>',
            '<text x="396" y="320" fill="#334155" font-size="12">Budget</text>',
            '<rect x="483" y="310" width="11" height="11" rx="2" fill="#1b6b81"/>',
            '<text x="500" y="320" fill="#334155" font-size="12">Actual</text>', '</svg>']
    return "\n".join(svg)


def render_html(root: Path, result: dict) -> None:
    report_dir = root / "reports"
    chart_dir = report_dir / "charts"
    chart_dir.mkdir(parents=True, exist_ok=True)
    chart = trend_svg(result["monthly"])
    (chart_dir / "monthly_spend.svg").write_text(chart + "\n", encoding="utf-8")
    variance = result["variance_cents"]
    status = "UNFAVORABLE" if variance > 0 else ("FAVORABLE" if variance < 0 else "ON PLAN")
    pct = result["variance_pct"]
    def trows(rows, title_col):
        lines = []
        for r in rows:
            delta = r["variance_cents"]
            ratio = 100 * delta / r["budget_cents"] if r["budget_cents"] else 0
            css = ' class="unfavorable"' if delta > 0 else ' class="favorable"'
            lines.append('<tr><td>' + escape(str(r[title_col])) + '</td>'
                         f'<td>{money(r["budget_cents"])}</td><td>{money(r["actual_cents"])}</td>'
                         f'<td{css}>{money(delta) if delta >= 0 else "−" + money(-delta)}</td>'
                         f'<td{css}>{ratio:+.1f}%</td></tr>')
        return "\n".join(lines)
    monthly_rows = []
    import calendar
    for r in result["monthly"]:
        r = dict(r)
        r["display_month"] = calendar.month_name[int(r["month_start"][5:7])]
        monthly_rows.append(r)
    labor = next(r for r in result["classifications"] if r["expense_class"] == "Labor")
    share = labor["actual_cents"] / result["actual_cents"] * 100
    html = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="Synthetic financial reporting demonstration, SQL and Power BI portfolio">
<title>FY{result["fiscal_year"]} | Financial Performance Overview</title>
<style>
:root {{--ink:#183248;--muted:#66758a;--line:#dae3ed;--accent:#1b6b81;--bg:#f2f6fa;--card:#fff;--bad:#a43131;--good:#237047;}}
*{{box-sizing:border-box}}body{{margin:0;font:15px/1.6 system-ui,-apple-system,Segoe UI,sans-serif;color:var(--ink);background:var(--bg)}}
main{{max-width:1170px;padding:28px 20px 64px;margin:auto}}header{{background:linear-gradient(120deg,#183248,#1c6072);color:#fff;padding:32px;border-radius:14px}}
h1{{font-size:clamp(25px,4vw,38px);margin:4px 0}}h2{{font-size:20px;margin:0 0 16px}}.eyebrow{{font-size:12px;text-transform:uppercase;letter-spacing:.13em;opacity:.8}}.sub{{color:#cde4ed;margin:0}}
.kpis{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;margin:20px 0}}.kpi,.panel{{background:var(--card);padding:22px;border:1px solid var(--line);border-radius:12px}}
.kpi .label{{font-size:13px;color:var(--muted)}}.kpi .value{{font-size:clamp(21px,2.6vw,30px);font-weight:750;letter-spacing:-.035em}}.kpi .small{{font-size:12px;color:var(--muted)}}.bad{{color:var(--bad)}}.good{{color:var(--good)}}
.panel{{margin:18px 0}}.chart{{overflow-x:auto}}.chart svg{{min-width:750px;width:100%;height:auto}}.table-wrap{{overflow-x:auto}}table{{border-collapse:collapse;width:100%;font-size:14px;white-space:nowrap}}th,td{{padding:11px 12px;border-bottom:1px solid var(--line);text-align:right}}th{{background:#eef3f8;color:#43566c;font-size:12px;text-transform:uppercase;letter-spacing:.03em}}th:first-child,td:first-child{{text-align:left}}tr:last-child td{{border:0}}td.unfavorable{{color:var(--bad);font-weight:650}}td.favorable{{color:var(--good);font-weight:650}}
.note{{color:var(--muted);font-size:13px}}.tag{{display:inline-block;border:1px solid #eab9b9;background:#fff1f1;color:#922b2b;padding:2px 9px;border-radius:50px;font-size:12px;font-weight:750}}footer{{color:var(--muted);font-size:12px;margin-top:32px}}
@media(max-width:800px){{.kpis{{grid-template-columns:repeat(2,1fr)}}header{{padding:23px}}.kpi,.panel{{padding:16px}}}}
@media(max-width:480px){{.kpis{{grid-template-columns:1fr 1fr;gap:9px}}.kpi .value{{font-size:21px}}main{{padding:12px 12px 36px}}}}
</style>
</head>
<body><main>
<header><div class="eyebrow">SolSystemsDev / Project 002 / Module 01</div>
<h1>Financial Performance Overview</h1>
<p class="sub">FY{result["fiscal_year"]} · October–September · Through fiscal month {result["through_fiscal_month"]} · Synthetic demonstration</p></header>
<section class="kpis" aria-label="Executive KPIs">
<div class="kpi"><div class="label">Fiscal YTD Budget</div><div class="value">{money(result["budget_cents"],True)}</div><div class="small">Expense plan</div></div>
<div class="kpi"><div class="label">Fiscal YTD Actual</div><div class="value">{money(result["actual_cents"],True)}</div><div class="small">Recorded expenses</div></div>
<div class="kpi"><div class="label">YTD Expense Variance</div><div class="value {'bad' if variance > 0 else 'good'}">{money(abs(variance),True)}</div><div class="small">{status} · {pct:+.2f}% vs plan</div></div>
<div class="kpi"><div class="label">Labor Share of Actual</div><div class="value">{share:.1f}%</div><div class="small">Labor vs non-labor</div></div>
</section>
<section class="panel"><h2>Monthly spend against plan</h2><p class="note">Expense variance = Actual − Budget. Positive values indicate unfavorable overspend.</p>
<div class="chart">{chart}</div></section>
<section class="panel"><h2>Department performance · Fiscal YTD</h2><div class="table-wrap"><table><thead><tr><th>Department</th><th>Budget</th><th>Actual</th><th>Variance $</th><th>Variance %</th></tr></thead>
<tbody>{trows(result["departments"], "department_name")}</tbody></table></div></section>
<section class="panel"><h2>General ledger variance drivers</h2><div class="table-wrap"><table><thead><tr><th>GL account</th><th>Budget</th><th>Actual</th><th>Variance $</th><th>Variance %</th></tr></thead>
<tbody>{trows(result["gl_accounts"], "gl_account_name")}</tbody></table></div></section>
<section class="panel"><h2>Monthly variance detail</h2><div class="table-wrap"><table><thead><tr><th>Fiscal month</th><th>Budget</th><th>Actual</th><th>Variance $</th><th>Variance %</th></tr></thead>
<tbody>{trows(monthly_rows, "display_month")}</tbody></table></div></section>
<section class="panel"><h2>Data quality and accounting conventions</h2>
<p>Budget values reconcile to the source budget ledger. Actual expenses reconcile to the complete synthetic transaction ledger. Reporting joins on fiscal month, department and general-ledger account. All amounts are USD.</p>
<p class="note">This is a portfolio simulation, not actual organizational financial information. Fiscal year is named by its ending September; e.g., FY2026 = 2025-10-01 through 2026-09-30. All figures are generated with seed 42.</p></section>
<footer>Developed by Jonathon McDonnell · SolSystemsDev · SQL / Python / Financial BI · v0.1</footer>
</main></body></html>'''
    (report_dir / "executive_dashboard.html").write_text(html, encoding="utf-8")
