@echo off
echo Ce script va copier les fichiers ESManualCheck et ESManualKill dans les dossiers script d'EmulationStation,
echo pour permettre d'ecouter les evenements d'ES et d'ouvrir le manuel (hotkey r1) et le fermer (hotkey).
echo.
echo This script will copy the ESManualCheck and ESManualKill files into EmulationStation's script folders,
echo to enable listening to ES events and open the manual (hotkey r1) and close (hotkey).
echo.
pause

SET source1=.\.esinstall\ESManualCheck.exe
SET dest1=..\..\emulationstation\.emulationstation\scripts\game-start
SET source2=.\.esinstall\ESManualKill.exe
SET dest2=..\..\emulationstation\.emulationstation\scripts\game-end

echo Work in progress...

IF EXIST "%source1%" (
    copy "%source1%" "%dest1%"
    echo Nice! Parfait!
) ELSE (
    echo Files not found - Fichier ESManualCheck non trouve
)
IF EXIST "%source2%" (
    copy "%source2%" "%dest2%"
    echo Nice! Parfait!
) ELSE (
    echo Files not found - Fichier ESManualKill non trouve
)

pause
