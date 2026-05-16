Set oShell = CreateObject("WScript.Shell")
Set oFSO = CreateObject("Scripting.FileSystemObject")

' Obtener la carpeta donde está este script
strPath = oFSO.GetParentFolderName(WScript.ScriptFullName)

' Iniciar uvicorn sin ventana
oShell.Run "cmd /c cd /d """ & strPath & """ && uvicorn backend.main:app --port 8000", 0, False

' Esperar 3 segundos
WScript.Sleep 3000

' Iniciar servidor frontend sin ventana
oShell.Run "cmd /c cd /d """ & strPath & "\frontend"" && python -m http.server 3000", 0, False

' Esperar 2 segundos
WScript.Sleep 2000

' Abrir navegador
oShell.Run "http://localhost:3000"