set NAME=qfscc
set VERSION=1.0.1
set DIR_NAME=%NAME%-%VERSION%
set ZIP_NAME=%NAME%-windows-%VERSION%
set BIN_DIR=bin
set TOP=%BIN_DIR%\%NAME%-%VERSION%

echo off

rmdir /S /Q %BIN_DIR% 2> nul

:setup_directories
echo Creating Directories...
mkdir %TOP%\

:copy_files
echo Copying Release Files...
copy build\exe.win32-3.3\* %TOP%\ > nul

:copy_changelog
echo Copying ChangeLog...
copy ChangeLog.md %TOP%\ > nul

:copy_readme
echo Copying README...
copy README.md %TOP%\ > nul

:copy_redist
echo Copying Redistributable...
copy vcredist_x86.exe %TOP%\ > nul

:zip_packages
echo Zipping Drivers...
cd %TOP%\ > nul
cd ..\ > nul
..\7za.exe a -tzip %ZIP_NAME%.zip %DIR_NAME% > nul
cd ..\ > nul