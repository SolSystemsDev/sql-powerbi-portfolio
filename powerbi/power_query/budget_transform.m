// Power Query (M), standalone reference query named FactBudget.
// First create a Text parameter named pCsvRoot with the FULL local path to data/synthetic.
let
    Source = Csv.Document(
        File.Contents(pCsvRoot & "/budgets.csv"),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Typed = Table.TransformColumnTypes(Headers, {
        {"budget_id", type text}, {"month_start", type date},
        {"department_id", type text}, {"gl_account_id", type text},
        {"budget_cents", Int64.Type}
    }),
    TrimmedKeys = Table.TransformColumns(Typed, {
        {"department_id", Text.Trim, type text},
        {"gl_account_id", Text.Trim, type text}
    }),
    UniqueBudgetGrain = Table.Distinct(
        TrimmedKeys, {"month_start", "department_id", "gl_account_id"}
    ),
    // Fail closed on duplicates rather than silently dropping budget rows.
    Output = if Table.RowCount(TrimmedKeys) <> Table.RowCount(UniqueBudgetGrain)
        then error "Duplicate budget grain: month / department / GL"
        else TrimmedKeys
in
    Output
