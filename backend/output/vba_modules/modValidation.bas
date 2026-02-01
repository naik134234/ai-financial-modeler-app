Attribute VB_Name = "modValidation"

' =============================================================
' Module: modValidation - Model Audit & Checks
' =============================================================

Public Sub RunValidation()
    Dim issues As Integer
    issues = 0
    
    ' Check balance sheet
    Dim assets As Double, liabEquity As Double
    On Error Resume Next
    assets = Sheets("Balance Sheet").Range("TotalAssets").Value
    liabEquity = Sheets("Balance Sheet").Range("TotalLiabEquity").Value
    On Error GoTo 0
    
    If Abs(assets - liabEquity) > 0.01 And assets > 0 Then
        issues = issues + 1
        Debug.Print "Balance sheet imbalance: " & Abs(assets - liabEquity)
    End If
    
    ' Check for errors
    Dim ws As Worksheet
    Dim cell As Range
    For Each ws In ThisWorkbook.Worksheets
        For Each cell In ws.UsedRange.SpecialCells(xlCellTypeFormulas)
            If IsError(cell.Value) Then
                issues = issues + 1
                Debug.Print "Error in " & ws.Name & "!" & cell.Address
            End If
        Next cell
    Next ws
    
    If issues = 0 Then
        MsgBox "Validation passed! No issues found.", vbInformation
    Else
        MsgBox issues & " issue(s) found. Check Immediate Window (Ctrl+G) for details.", vbExclamation
    End If
End Sub

Public Sub HighlightInputs()
    Dim ws As Worksheet
    Dim cell As Range
    
    For Each ws In ThisWorkbook.Worksheets
        For Each cell In ws.UsedRange.SpecialCells(xlCellTypeConstants)
            If IsNumeric(cell.Value) Then
                cell.Interior.Color = RGB(255, 242, 204)
            End If
        Next cell
    Next ws
    
    MsgBox "Input cells highlighted in yellow", vbInformation
End Sub
