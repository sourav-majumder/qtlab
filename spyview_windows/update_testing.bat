@echo off
xcopy /y *.exe old_version
xcopy /y *.bat old_version
wget -e robots=off -nv -nd --no-parent -N -A .exe,.bat,.txt -r -l1 http://kavli.nano.tudelft.nl/~gsteele/spyview/windows_testing/
@echo setting permissions
for %%f in (*.exe *.bat) do (
cacls %%f /e /g "Everyone":R
)
pause
