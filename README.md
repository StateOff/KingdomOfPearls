# KingdomOfPearls
Text based Adventure Roleplaying Game

# Developer installation

## Linux

- Use a shell and font with good Unicode support
  - I tested Kitty which has good defaults
    - https://sw.kovidgoyal.net/kitty/
  - Make sure to use 3.10 (others 3.x might work but are untested)
```shell
pip install virtualenv
virtualenv _venv
. _venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Windows
- Install the Windows Termnial (as built-in shells in windows do not have Unicode support)
  - https://apps.microsoft.com/store/detail/windows-terminal/9N0DX20HK701

- Install python 3.10 from:
  - https://www.python.org/downloads/windows/

- Open the shell in Powershell
  - Set-ExecutionPolicy Unrestricted -Scope Proces
    - This allows virtualenv to be activate
```shell
pip install virtualenv
virtualenv _venv
. _venv/Scripts/activate.ps1
pip install -r requirements.txt
python main.py
```
  - Hold CRTL and scroll to adjust the font size to something reasonable 
