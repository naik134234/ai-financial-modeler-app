Attribute VB_Name = "modCalc"

' =============================================================
' Module: modCalc - Financial Calculations
' =============================================================

Public Function CalcWACC(costOfEquity As Double, costOfDebt As Double, _
                          taxRate As Double, equityWeight As Double) As Double
    CalcWACC = (equityWeight * costOfEquity) + ((1 - equityWeight) * costOfDebt * (1 - taxRate))
End Function

Public Function CalcTerminalValue(fcff As Double, terminalGrowth As Double, wacc As Double) As Double
    If wacc <= terminalGrowth Then
        CalcTerminalValue = 0
    Else
        CalcTerminalValue = fcff * (1 + terminalGrowth) / (wacc - terminalGrowth)
    End If
End Function

Public Function CalcDCF(cashFlows As Range, wacc As Double) As Double
    Dim i As Integer
    Dim pv As Double
    pv = 0
    
    For i = 1 To cashFlows.Count
        pv = pv + cashFlows(i).Value / ((1 + wacc) ^ i)
    Next i
    
    CalcDCF = pv
End Function

Public Sub RecalculateModel()
    Application.Calculate
    MsgBox "Model recalculated!", vbInformation
End Sub
