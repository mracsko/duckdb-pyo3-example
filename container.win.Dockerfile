#FROM mcr.microsoft.com/windows/servercore:ltsc2022
FROM mcr.microsoft.com/windows/servercore:1809
#FROM mcr.microsoft.com/dotnet/framework/runtime:4.8

# ========== Python ==========
# Based on Dockerfile: https://github.com/MicrosoftDocs/Virtualization-Documentation/blob/main/windows-container-samples/python/Dockerfile
# Using Python 3.10.11 due to https://stackoverflow.com/questions/74296856/install-pyarrow-in-vs-code-for-windows
RUN powershell.exe -Command \
    $ErrorActionPreference = 'Stop'; \
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; \
	Invoke-WebRequest "https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe" -OutFile "/python-3.10.11.exe"; \
	Start-Process c:\python-3.10.11.exe -ArgumentList '/quiet InstallAllUsers=1 PrependPath=1' -Wait ; \
	Remove-Item -Force python-3.10.11.exe;

# ========== Visual C++ Runtime ==========
# https://arrow.apache.org/docs/python/install.html
# VS 2015
ADD https://download.microsoft.com/download/6/A/A/6AA4EDFF-645B-48C5-81CC-ED5963AEAD48/vc_redist.x64.exe /vc_redist.x64.exe
RUN c:\vc_redist.x64.exe /install /quiet /norestart
RUN del vc_redist.x64.exe

# ========== MVSC Build Tools ==========
# Based on: https://tech.fpcomplete.com/blog/rust-kubernetes-windows/

# Restore the default Windows shell for correct batch processing.
SHELL ["cmd", "/S", "/C"]

# Download the Build Tools bootstrapper.
# URL retrieved from: https://visualstudio.microsoft.com/downloads/
ADD https://aka.ms/vs/17/release/vs_BuildTools.exe /vs_buildtools.exe

# Install Build Tools with the Microsoft.VisualStudio.Workload.AzureBuildTools workload,
# excluding workloads and components with known issues.
RUN vs_buildtools.exe --quiet --wait --norestart --nocache \
    --installPath C:\BuildTools \
    --add Microsoft.Component.MSBuild \
    --add Microsoft.VisualStudio.Component.Windows10SDK.18362 \
    --add Microsoft.VisualStudio.Component.Windows11SDK.22621 \
    --add Microsoft.VisualStudio.Component.VC.Tools.x86.x64	\
 || IF "%ERRORLEVEL%"=="3010" EXIT 0

# Define the entry point for the docker container.
# This entry point starts the developer command prompt and launches the PowerShell shell.
ENTRYPOINT ["C:\\BuildTools\\Common7\\Tools\\VsDevCmd.bat", "&&", "powershell.exe", "-NoLogo", "-ExecutionPolicy", "Bypass"]

# ========== Rust ==========
# Based on: https://tech.fpcomplete.com/blog/rust-kubernetes-windows/

ADD https://win.rustup.rs/x86_64 /rustup-init.exe
RUN start /w rustup-init.exe -y -v && echo "Error level is %ERRORLEVEL%"
RUN del rustup-init.exe

RUN setx /M PATH "C:\Users\ContainerAdministrator\.cargo\bin;%PATH%"

# ========== App ==========

RUN python -m pip install --upgrade pip
RUN pip install poetry

WORKDIR /app
COPY . .

RUN python -m venv .venv
RUN .\.venv\Scripts\activate && poetry install --no-interaction --no-root
RUN .\.venv\Scripts\activate && maturin develop --release

CMD ["./Run.ps1"]