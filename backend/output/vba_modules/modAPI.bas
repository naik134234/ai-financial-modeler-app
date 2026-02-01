Attribute VB_Name = "modAPI"

' =============================================================
' Module: modAPI - API Integration Functions
' =============================================================

Private Const API_BASE_URL As String = "http://localhost:8000/api"

Public Function CallAPI(endpoint As String, Optional method As String = "GET") As String
    On Error GoTo ErrorHandler
    
    Dim http As Object
    Set http = CreateObject("MSXML2.XMLHTTP")
    
    http.Open method, API_BASE_URL & endpoint, False
    http.setRequestHeader "Content-Type", "application/json"
    http.send
    
    If http.Status = 200 Then
        CallAPI = http.responseText
    Else
        CallAPI = "{"error": "HTTP " & http.Status & ""}"
    End If
    
    Exit Function
ErrorHandler:
    CallAPI = "{"error": "" & Err.Description & ""}"
End Function

Public Sub RefreshStockData()
    Dim ticker As String
    ticker = Range("Assumptions!B3").Value
    
    If ticker = "" Then
        MsgBox "Please enter a stock ticker in Assumptions!B3", vbExclamation
        Exit Sub
    End If
    
    Application.StatusBar = "Fetching data for " & ticker & "..."
    
    Dim response As String
    response = CallAPI("/stocks/" & ticker)
    
    If InStr(response, "error") = 0 Then
        MsgBox "Data refreshed successfully!", vbInformation
    Else
        MsgBox "Failed to refresh data: " & response, vbCritical
    End If
    
    Application.StatusBar = False
End Sub
