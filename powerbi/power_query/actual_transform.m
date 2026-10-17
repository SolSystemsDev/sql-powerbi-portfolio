// Power Query (M), standalone reference query named FactActual.
// First create a Text parameter named pCsvRoot with FULL path to data/synthetic.
let
    Source = Csv.Document(
        File.Contents(pCsvRoot & "/actuals.csv"),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Typed = Table.TransformColumnTypes(Headers, {
        {"transaction_id", type text}, {"transaction_date", type date},
        {"department_id", type text}, {"gl_account_id", type text},
        {"actual_cents", Int64.Type}, {"reference", type text}
    }),
    TrimmedKeys = Table.TransformColumns(Typed, {
        {"department_id", Text.Trim, type text},
        {"gl_account_id", Text.Trim, type text}
    }),
    WithMonth = Table.AddColumn(TrimmedKeys, "month_start",
        each Date.StartOfMonth([transaction_date]), type date),
    Output = WithMonth
in
    Output
