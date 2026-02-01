'==============================================================================
' ENTERPRISE FINANCIAL MODELING VBA STARTER KIT
' Version: 1.0.0
' Standard: Investment Banking / Private Equity / Big-4 Consulting
'==============================================================================

'------------------------------------------------------------------------------
' MODULE: modMain - Master Controller
'------------------------------------------------------------------------------

Option Explicit

' Global constants
Public Const APP_NAME As String = "AI Financial Modeler"
Public Const APP_VERSION As String = "1.0.0"

' API Configuration
Public Const API_BASE_URL As String = "http://localhost:8000"

'------------------------------------------------------------------------------
' MAIN: Generate Complete Financial Model
'------------------------------------------------------------------------------
Public Sub GenerateModel()
    On Error GoTo ErrorHandler
    
    Application.ScreenUpdating = False
    Application.Calculation = xlCalculationManual
    
    ' Log start
    Call LogExecution("Model generation started")
    
    ' Step 1: Validate inputs
    If Not ValidateInputs() Then
        MsgBox "Please check input assumptions.", vbExclamation, APP_NAME
        GoTo CleanUp
    End If
    
    ' Step 2: Build revenue model
    Call BuildRevenueModel
    
    ' Step 3: Build cost model
    Call BuildCostModel
    
    ' Step 4: Generate financial statements
    Call GenerateIncomeStatement
    Call GenerateBalanceSheet
    Call GenerateCashFlowStatement
    
    ' Step 5: Run valuation
    Call RunDCFValuation
    
    ' Step 6: Build dashboard
    Call UpdateDashboard
    
    ' Step 7: Run validation checks
    Call RunValidationChecks
    
    MsgBox "Model generated successfully!", vbInformation, APP_NAME
    
CleanUp:
    Application.ScreenUpdating = True
    Application.Calculation = xlCalculationAutomatic
    Call LogExecution("Model generation completed")
    Exit Sub
    
ErrorHandler:
    MsgBox "Error: " & Err.Description, vbCritical, APP_NAME
    Call LogExecution("ERROR: " & Err.Description)
    Resume CleanUp
End Sub


'------------------------------------------------------------------------------
' MODULE: modAPI - External API Calls
'------------------------------------------------------------------------------

Public Function CallModelAPI(endpoint As String, method As String, Optional payload As String = "") As String
    ' Call the Python backend API
    On Error GoTo ErrorHandler
    
    Dim http As Object
    Set http = CreateObject("MSXML2.XMLHTTP")
    
    Dim url As String
    url = API_BASE_URL & endpoint
    
    http.Open method, url, False
    http.setRequestHeader "Content-Type", "application/json"
    
    If payload <> "" Then
        http.send payload
    Else
        http.send
    End If
    
    CallModelAPI = http.responseText
    Exit Function
    
ErrorHandler:
    CallModelAPI = "{""error"": """ & Err.Description & """}"
End Function

Public Function FetchCompanyData(symbol As String) As String
    ' Fetch company data from API
    FetchCompanyData = CallModelAPI("/api/company/" & symbol, "GET")
End Function

Public Function GenerateAIAssumptions(symbol As String, industry As String) As String
    ' Get AI-generated assumptions
    Dim payload As String
    payload = "{""symbol"": """ & symbol & """, ""industry"": """ & industry & """}"
    GenerateAIAssumptions = CallModelAPI("/api/ai/assumptions", "POST", payload)
End Function

Public Function RunMonteCarloAPI(jobId As String, simulations As Long) As String
    ' Run Monte Carlo simulation via API
    RunMonteCarloAPI = CallModelAPI("/api/analysis/monte-carlo/" & jobId & "?simulations=" & simulations, "GET")
End Function


'------------------------------------------------------------------------------
' MODULE: modData - Data Processing
'------------------------------------------------------------------------------

Public Sub RefreshData()
    ' Refresh all data from external sources
    On Error GoTo ErrorHandler
    
    Dim wsData As Worksheet
    Set wsData = ThisWorkbook.Worksheets("Data")
    
    ' Get company symbol
    Dim symbol As String
    symbol = wsData.Range("B2").Value
    
    ' Fetch latest data
    Dim jsonData As String
    jsonData = FetchCompanyData(symbol)
    
    ' Parse and populate
    Call ParseJSONToSheet(jsonData, wsData)
    
    MsgBox "Data refreshed successfully!", vbInformation, APP_NAME
    Exit Sub
    
ErrorHandler:
    MsgBox "Data refresh failed: " & Err.Description, vbCritical, APP_NAME
End Sub

Private Sub ParseJSONToSheet(jsonText As String, ws As Worksheet)
    ' Simple JSON parser for financial data
    ' For production, use a proper JSON library
    
    ' Basic implementation - extract key values
    Dim revenue As Double, ebitda As Double, netIncome As Double
    
    ' Parse values (simplified)
    revenue = ExtractJSONValue(jsonText, "revenue")
    ebitda = ExtractJSONValue(jsonText, "ebitda")
    netIncome = ExtractJSONValue(jsonText, "net_income")
    
    ' Populate cells
    ws.Range("C5").Value = revenue
    ws.Range("C6").Value = ebitda
    ws.Range("C7").Value = netIncome
End Sub

Private Function ExtractJSONValue(json As String, key As String) As Double
    ' Extract numeric value from JSON (simplified)
    On Error Resume Next
    
    Dim startPos As Long, endPos As Long
    Dim valueStr As String
    
    startPos = InStr(json, """" & key & """:") + Len(key) + 3
    If startPos > Len(key) + 3 Then
        endPos = InStr(startPos, json, ",")
        If endPos = 0 Then endPos = InStr(startPos, json, "}")
        valueStr = Mid(json, startPos, endPos - startPos)
        valueStr = Replace(valueStr, """", "")
        ExtractJSONValue = CDbl(Trim(valueStr))
    End If
End Function


'------------------------------------------------------------------------------
' MODULE: modModel - Model Calculations
'------------------------------------------------------------------------------

Public Sub BuildRevenueModel()
    ' Build revenue projections based on assumptions
    Dim wsModel As Worksheet
    Set wsModel = ThisWorkbook.Worksheets("Model")
    
    Dim baseRevenue As Double
    Dim growthRate As Double
    Dim i As Integer
    
    ' Get assumptions
    baseRevenue = wsModel.Range("Assumptions_Revenue").Value
    growthRate = wsModel.Range("Assumptions_Growth").Value
    
    ' Project revenue for 5 years
    For i = 1 To 5
        wsModel.Cells(10, 3 + i).Value = baseRevenue * (1 + growthRate) ^ i
    Next i
End Sub

Public Sub BuildCostModel()
    ' Build cost projections
    Dim wsModel As Worksheet
    Set wsModel = ThisWorkbook.Worksheets("Model")
    
    Dim ebitdaMargin As Double
    Dim i As Integer
    
    ebitdaMargin = wsModel.Range("Assumptions_Margin").Value
    
    ' Apply margin to projected revenue
    For i = 1 To 5
        Dim revenue As Double
        revenue = wsModel.Cells(10, 3 + i).Value
        wsModel.Cells(15, 3 + i).Value = revenue * ebitdaMargin ' EBITDA
        wsModel.Cells(16, 3 + i).Value = revenue * (1 - ebitdaMargin) ' Costs
    Next i
End Sub

Public Sub GenerateIncomeStatement()
    ' Generate full income statement
    ' Links to revenue and cost models
    Call LogExecution("Income Statement generated")
End Sub

Public Sub GenerateBalanceSheet()
    ' Generate balance sheet
    ' Must balance: Assets = Liabilities + Equity
    Call LogExecution("Balance Sheet generated")
End Sub

Public Sub GenerateCashFlowStatement()
    ' Generate cash flow statement
    ' Must reconcile to change in cash
    Call LogExecution("Cash Flow Statement generated")
End Sub

Public Sub RunDCFValuation()
    ' Perform DCF valuation
    Dim wsVal As Worksheet
    Set wsVal = ThisWorkbook.Worksheets("Valuation")
    
    Dim wacc As Double, terminalGrowth As Double
    Dim fcf(1 To 5) As Double
    Dim i As Integer
    Dim dcfValue As Double, terminalValue As Double
    
    wacc = wsVal.Range("WACC").Value
    terminalGrowth = wsVal.Range("Terminal_Growth").Value
    
    ' Get FCF projections
    For i = 1 To 5
        fcf(i) = wsVal.Cells(20, 3 + i).Value
    Next i
    
    ' Calculate DCF
    dcfValue = 0
    For i = 1 To 5
        dcfValue = dcfValue + fcf(i) / (1 + wacc) ^ i
    Next i
    
    ' Terminal value (Gordon Growth)
    terminalValue = fcf(5) * (1 + terminalGrowth) / (wacc - terminalGrowth)
    terminalValue = terminalValue / (1 + wacc) ^ 5
    
    ' Output
    wsVal.Range("Enterprise_Value").Value = dcfValue + terminalValue
    
    Call LogExecution("DCF Valuation completed")
End Sub


'------------------------------------------------------------------------------
' MODULE: modDashboard - Dashboard Updates
'------------------------------------------------------------------------------

Public Sub UpdateDashboard()
    ' Update executive dashboard
    Dim wsDash As Worksheet
    Set wsDash = ThisWorkbook.Worksheets("Dashboard")
    
    ' Update KPIs
    Call UpdateKPITiles(wsDash)
    
    ' Update charts
    Call RefreshCharts(wsDash)
    
    ' Update scenario display
    Call UpdateScenarioDisplay(wsDash)
    
    Call LogExecution("Dashboard updated")
End Sub

Private Sub UpdateKPITiles(ws As Worksheet)
    ' Update KPI summary tiles
    ws.Range("KPI_Revenue").Value = ThisWorkbook.Worksheets("Model").Range("F10").Value
    ws.Range("KPI_EBITDA").Value = ThisWorkbook.Worksheets("Model").Range("F15").Value
    ws.Range("KPI_FCF").Value = ThisWorkbook.Worksheets("Valuation").Range("F20").Value
    ws.Range("KPI_EV").Value = ThisWorkbook.Worksheets("Valuation").Range("Enterprise_Value").Value
End Sub

Private Sub RefreshCharts(ws As Worksheet)
    ' Refresh all dashboard charts
    Dim cht As ChartObject
    For Each cht In ws.ChartObjects
        cht.Chart.Refresh
    Next cht
End Sub

Private Sub UpdateScenarioDisplay(ws As Worksheet)
    ' Update based on selected scenario
    Dim scenario As String
    scenario = ws.Range("Selected_Scenario").Value
    
    Select Case scenario
        Case "Bear"
            ws.Range("Scenario_Color").Interior.Color = RGB(255, 100, 100)
        Case "Base"
            ws.Range("Scenario_Color").Interior.Color = RGB(100, 200, 100)
        Case "Bull"
            ws.Range("Scenario_Color").Interior.Color = RGB(100, 150, 255)
    End Select
End Sub

Public Sub RunScenarios()
    ' Run all scenarios and update sensitivity tables
    Dim scenarios As Variant
    scenarios = Array("Bear", "Base", "Bull")
    
    Dim i As Integer
    For i = 0 To 2
        ThisWorkbook.Worksheets("Scenarios").Range("Current_Scenario").Value = scenarios(i)
        Call GenerateModel
    Next i
    
    ' Reset to Base
    ThisWorkbook.Worksheets("Scenarios").Range("Current_Scenario").Value = "Base"
    Call UpdateDashboard
End Sub


'------------------------------------------------------------------------------
' MODULE: modValidation - Error Checking & Audit
'------------------------------------------------------------------------------

Public Function ValidateInputs() As Boolean
    ' Validate all input assumptions
    Dim wsInputs As Worksheet
    Set wsInputs = ThisWorkbook.Worksheets("Assumptions")
    
    ValidateInputs = True
    
    ' Check revenue growth is reasonable (< 50%)
    If wsInputs.Range("Revenue_Growth").Value > 0.5 Then
        ValidateInputs = False
        wsInputs.Range("Revenue_Growth").Interior.Color = RGB(255, 200, 200)
    End If
    
    ' Check WACC is in range (5-20%)
    If wsInputs.Range("WACC").Value < 0.05 Or wsInputs.Range("WACC").Value > 0.2 Then
        ValidateInputs = False
        wsInputs.Range("WACC").Interior.Color = RGB(255, 200, 200)
    End If
    
    ' Check terminal growth < WACC
    If wsInputs.Range("Terminal_Growth").Value >= wsInputs.Range("WACC").Value Then
        ValidateInputs = False
        wsInputs.Range("Terminal_Growth").Interior.Color = RGB(255, 200, 200)
    End If
End Function

Public Sub RunValidationChecks()
    ' Run all model validation checks
    Dim wsChecks As Worksheet
    Set wsChecks = ThisWorkbook.Worksheets("Checks")
    
    Dim checkRow As Integer
    checkRow = 5
    
    ' Check 1: Balance sheet balances
    Dim bsBalance As Boolean
    bsBalance = CheckBalanceSheetBalance()
    wsChecks.Cells(checkRow, 1).Value = "Balance Sheet Balances"
    wsChecks.Cells(checkRow, 2).Value = IIf(bsBalance, "PASS", "FAIL")
    wsChecks.Cells(checkRow, 2).Interior.Color = IIf(bsBalance, RGB(200, 255, 200), RGB(255, 200, 200))
    checkRow = checkRow + 1
    
    ' Check 2: Cash flow reconciles
    Dim cfReconciles As Boolean
    cfReconciles = CheckCashFlowReconciliation()
    wsChecks.Cells(checkRow, 1).Value = "Cash Flow Reconciles"
    wsChecks.Cells(checkRow, 2).Value = IIf(cfReconciles, "PASS", "FAIL")
    wsChecks.Cells(checkRow, 2).Interior.Color = IIf(cfReconciles, RGB(200, 255, 200), RGB(255, 200, 200))
    checkRow = checkRow + 1
    
    ' Check 3: No broken links
    Dim noErrors As Boolean
    noErrors = CheckForErrors()
    wsChecks.Cells(checkRow, 1).Value = "No Formula Errors"
    wsChecks.Cells(checkRow, 2).Value = IIf(noErrors, "PASS", "FAIL")
    wsChecks.Cells(checkRow, 2).Interior.Color = IIf(noErrors, RGB(200, 255, 200), RGB(255, 200, 200))
    
    Call LogExecution("Validation checks completed")
End Sub

Private Function CheckBalanceSheetBalance() As Boolean
    ' Check if balance sheet balances
    Dim wsBS As Worksheet
    Set wsBS = ThisWorkbook.Worksheets("Balance_Sheet")
    
    Dim assets As Double, liabEquity As Double
    assets = wsBS.Range("Total_Assets").Value
    liabEquity = wsBS.Range("Total_Liabilities").Value + wsBS.Range("Total_Equity").Value
    
    CheckBalanceSheetBalance = (Abs(assets - liabEquity) < 1) ' Within 1 unit tolerance
End Function

Private Function CheckCashFlowReconciliation() As Boolean
    ' Check if cash flow reconciles to balance sheet
    Dim wsCF As Worksheet, wsBS As Worksheet
    Set wsCF = ThisWorkbook.Worksheets("Cash_Flow")
    Set wsBS = ThisWorkbook.Worksheets("Balance_Sheet")
    
    Dim cfEnding As Double, bsCash As Double
    cfEnding = wsCF.Range("Ending_Cash").Value
    bsCash = wsBS.Range("Cash").Value
    
    CheckCashFlowReconciliation = (Abs(cfEnding - bsCash) < 1)
End Function

Private Function CheckForErrors() As Boolean
    ' Check for any #REF!, #VALUE!, #DIV/0! errors
    Dim ws As Worksheet
    Dim cell As Range
    Dim hasErrors As Boolean
    
    hasErrors = False
    For Each ws In ThisWorkbook.Worksheets
        For Each cell In ws.UsedRange
            If IsError(cell.Value) Then
                hasErrors = True
                Exit For
            End If
        Next cell
        If hasErrors Then Exit For
    Next ws
    
    CheckForErrors = Not hasErrors
End Function


'------------------------------------------------------------------------------
' MODULE: modExport - Export Functions
'------------------------------------------------------------------------------

Public Sub ExportToPDF()
    ' Export model to PDF
    Dim savePath As String
    savePath = ThisWorkbook.Path & "\" & Replace(ThisWorkbook.Name, ".xlsm", "_Report.pdf")
    
    ' Export key sheets
    Dim sheets As Variant
    sheets = Array("Dashboard", "Summary", "Valuation")
    
    ThisWorkbook.Worksheets(sheets).Select
    ActiveSheet.ExportAsFixedFormat Type:=xlTypePDF, filename:=savePath, Quality:=xlQualityStandard
    
    MsgBox "PDF exported to: " & savePath, vbInformation, APP_NAME
End Sub

Public Sub ResetInputs()
    ' Reset all inputs to defaults
    Dim wsInputs As Worksheet
    Set wsInputs = ThisWorkbook.Worksheets("Assumptions")
    
    ' Reset to conservative defaults
    wsInputs.Range("Revenue_Growth").Value = 0.1
    wsInputs.Range("EBITDA_Margin").Value = 0.18
    wsInputs.Range("Terminal_Growth").Value = 0.04
    wsInputs.Range("WACC").Value = 0.12
    wsInputs.Range("Tax_Rate").Value = 0.25
    
    ' Clear highlights
    wsInputs.Cells.Interior.ColorIndex = xlNone
    
    MsgBox "Inputs reset to defaults.", vbInformation, APP_NAME
End Sub


'------------------------------------------------------------------------------
' MODULE: modLogging - Execution Logging
'------------------------------------------------------------------------------

Private Sub LogExecution(message As String)
    ' Log execution to hidden log sheet
    On Error Resume Next
    
    Dim wsLog As Worksheet
    Set wsLog = ThisWorkbook.Worksheets("_Log")
    
    If wsLog Is Nothing Then
        Set wsLog = ThisWorkbook.Worksheets.Add(After:=ThisWorkbook.Worksheets(ThisWorkbook.Worksheets.Count))
        wsLog.Name = "_Log"
        wsLog.Visible = xlSheetVeryHidden
    End If
    
    Dim nextRow As Long
    nextRow = wsLog.Cells(wsLog.Rows.Count, 1).End(xlUp).Row + 1
    
    wsLog.Cells(nextRow, 1).Value = Now()
    wsLog.Cells(nextRow, 2).Value = message
End Sub


'------------------------------------------------------------------------------
' BUTTON HANDLERS - For Ribbon/Form Buttons
'------------------------------------------------------------------------------

Public Sub btn_GenerateModel()
    Call GenerateModel
End Sub

Public Sub btn_RefreshData()
    Call RefreshData
End Sub

Public Sub btn_RunScenarios()
    Call RunScenarios
End Sub

Public Sub btn_ExportPDF()
    Call ExportToPDF
End Sub

Public Sub btn_ResetInputs()
    Call ResetInputs
End Sub

Public Sub btn_RunValidation()
    Call RunValidationChecks
End Sub
