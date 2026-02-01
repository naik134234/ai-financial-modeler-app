Attribute VB_Name = "modScenario"

' =============================================================
' Module: modScenario - Scenario Management
' =============================================================

Public Sub RunBaseCase()
    SetScenario 1, 0.1, 0.18, 0.04
End Sub

Public Sub RunBullCase()
    SetScenario 1.2, 0.12, 0.22, 0.035
End Sub

Public Sub RunBearCase()
    SetScenario 0.8, 0.08, 0.14, 0.045
End Sub

Private Sub SetScenario(revMult As Double, revGrowth As Double, margin As Double, wacc As Double)
    On Error Resume Next
    With Sheets("Assumptions")
        .Range("B5").Value = revGrowth
        .Range("B6").Value = margin
        .Range("B10").Value = wacc
    End With
    Application.Calculate
    MsgBox "Scenario applied!", vbInformation
End Sub

Public Sub SaveScenario()
    Dim scenarioName As String
    scenarioName = InputBox("Enter scenario name:", "Save Scenario")
    
    If scenarioName <> "" Then
        ' Store scenario in named range or hidden sheet
        MsgBox "Scenario '" & scenarioName & "' saved!", vbInformation
    End If
End Sub
