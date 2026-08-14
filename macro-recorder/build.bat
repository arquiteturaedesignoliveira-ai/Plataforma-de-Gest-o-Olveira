@echo off
REM Gera o executavel Windows (MacroRecorder.exe) usando PyInstaller.
REM Execute a partir da pasta macro-recorder, com o ambiente virtual ativo.

pip install -r requirements.txt
pyinstaller --noconfirm --onefile --windowed --name MacroRecorder --paths src src\main.py

echo.
echo Executavel gerado em dist\MacroRecorder.exe
