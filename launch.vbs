Option Explicit

Dim sh, fso, root, base, chrome, edge, py, i, logFile, logStream

Set sh = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
root = fso.GetParentFolderName(WScript.ScriptFullName)
sh.CurrentDirectory = root
base = "http://127.0.0.1:8017/"
logFile = sh.ExpandEnvironmentStrings("%TEMP%") & "\favour-house.log"

Function IsUp()
  Dim http
  IsUp = False
  Err.Clear
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

Function PythonCmd()
  Dim p
  p = sh.ExpandEnvironmentStrings("%LOCALAPPDATA%") & "\Programs\Python\Python313\python.exe"
  If fso.FileExists(p) Then
    PythonCmd = Chr(34) & p & Chr(34)
  ElseIf sh.Run("cmd /c where py >nul 2>nul", 0, True) = 0 Then
    PythonCmd = "py"
  Else
    PythonCmd = "python"
  End If
End Function

If Not IsUp() Then
  py = PythonCmd()

  If Not fso.FileExists(root & "\db.sqlite3") Then
    sh.Run "cmd /c " & Chr(34) & py & " manage.py migrate --noinput" & Chr(34), 0, True
    sh.Run "cmd /c " & Chr(34) & py & " manage.py seed_demo" & Chr(34), 0, True
  End If

  Set logStream = fso.CreateTextFile(logFile, True)
  logStream.WriteLine "[" & Now & "] launching server"
  logStream.Close
  sh.Run "cmd /c " & Chr(34) & py & " manage.py runserver 8017 >> " & Chr(34) & logFile & Chr(34) & " 2>&1" & Chr(34), 0, False

  For i = 1 To 40
    WScript.Sleep 500
    If IsUp() Then Exit For
  Next

  If Not IsUp() Then
    MsgBox "The Favour House server did not start." & vbCrLf & vbCrLf & _
           "Details were saved to:" & vbCrLf & logFile, 48, "Favour House"
  End If
End If

chrome = sh.ExpandEnvironmentStrings("%ProgramFiles%") & "\Google\Chrome\Application\chrome.exe"
edge = sh.ExpandEnvironmentStrings("%ProgramFiles(x86)%") & "\Microsoft\Edge\Application\msedge.exe"

If fso.FileExists(chrome) Then
  sh.Run Chr(34) & chrome & Chr(34) & " --app=" & base & " --window-size=1500,960", 1, False
ElseIf fso.FileExists(edge) Then
  sh.Run Chr(34) & edge & Chr(34) & " --app=" & base & " --window-size=1500,960", 1, False
Else
  sh.Run base, 1, False
End If
