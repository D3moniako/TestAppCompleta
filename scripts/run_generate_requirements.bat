@echo off 
rem  vuol dire commento
rem Imposta il percorso del tuo ambiente Python
set PYTHON_EXECUTABLE="C:\Python39\python.exe"

rem Esegui lo script Python
%PYTHON_EXECUTABLE% scripts\generate_requirements.py

rem Metti in pausa alla fine (opzionale)
pause