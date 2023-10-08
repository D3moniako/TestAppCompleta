:: run_all_generate_docker_compose.bat
@echo off
cd %~dp0
for /d %%i in (microservizi\*) do (
    cd "microservizi\%%i"
    echo Running run_generate_docker_compose.bat in microservizio: %%i
    call ..\run_generate_docker_compose.bat
    cd ..
)
