@echo off
echo ============================================
echo BUILD - MiNegocio Instalador
echo ============================================
echo.

echo Instalando dependencias del build...
pip install pyinstaller pywin32 psycopg2-binary python-dotenv requests
echo.

echo Compilando instalador y launcher...
python deploy\build_installer.py
echo.

echo ============================================
echo Build completado. Revisa deploy\dist\
echo ============================================
pause
