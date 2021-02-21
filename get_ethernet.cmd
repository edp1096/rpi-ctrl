@echo off
setLocal enableDelayedExpansion
set c=0

for /f "skip=2 tokens=3*" %%A in ('netsh interface show interface') do (
    set /a c+=1
    set int!c!=%%B
    echo %%B
)
