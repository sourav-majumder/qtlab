@echo off
xcopy /y spyview_console.exe old_version
wget -e robots=off -nv -nd --no-parent -N -A .exe,.bat,.txt -r -l1 http://kavli.nano.tudelft.nl/~gsteele/spyview/windows_testing/spyview_console.exe
cacls spyview_console.exe /e /g "Everyone":R
)
pause
