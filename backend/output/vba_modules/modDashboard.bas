Attribute VB_Name = "modDashboard"

' =============================================================
' Module: modDashboard - Dashboard Controls
' =============================================================

Public Sub UpdateDashboard()
    On Error Resume Next
    
    ' Update timestamp
    Sheets("Dashboard").Range("B1").Value = "Last Updated: " & Format(Now, "dd-mmm-yyyy hh:mm")
    
    ' Refresh charts
    Dim cht As ChartObject
    For Each cht In Sheets("Dashboard").ChartObjects
        cht.Chart.Refresh
    Next cht
    
    Application.StatusBar = "Dashboard updated"
End Sub

Public Sub ExportToPDF()
    Dim savePath As String
    savePath = Application.GetSaveAsFilename( _
        InitialFileName:=ThisWorkbook.Name & "_Export.pdf", _
        FileFilter:="PDF Files (*.pdf), *.pdf")
    
    If savePath <> "False" Then
        Sheets("Dashboard").ExportAsFixedFormat Type:=xlTypePDF, Filename:=savePath
        MsgBox "Exported to: " & savePath, vbInformation
    End If
End Sub
