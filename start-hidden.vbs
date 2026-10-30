Option Explicit

Dim sh, fso, root, py, base, i

Set sh = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
root = fso.GetParentFolderName(WScript.ScriptFullName)
sh.CurrentDirectory = root
base = "http://127.0.0.1:8017/"
py = "C:\Users\ABID\AppData\Local\Programs\Python\Python313\python.exe"
If Not fso.FileExists(py) Then py = "python"

If Not IsUp() Then
  sh.Run "cmd /c """ & py & """ manage.py runserver 127.0.0.1:8017 >> server.log 2>&1", 0, False
  For i = 1 To 40
    WScript.Sleep 500
    If IsUp() Then Exit For
  Next
End If

Function IsUp()
  Dim http
  IsUp = False
  On Error Resume Next
  Set http = CreateObject("MSXML2.XMLHTTP")
  http.Open "GET", base, False
  http.Send
  If Err.Number = 0 Then
    If http.Status >= 200 And http.Status < 500 Then IsUp = True
  End If
  Err.Clear
  On Error GoTo 0
End Function
