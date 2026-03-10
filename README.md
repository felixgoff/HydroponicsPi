# HydroponicsPi

This Github repository is for a school project.

## Setup:

### Requirements:

 - Go <sup>1.25.6</sup>
 - TinyGo
 - git
 - Go Extension in VS Code (Optional)

### Easy Install Requirements With Scoop

***Download Scoop:***
1. Open Powershell
2. Install Scoop with this command: 
```
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
Invoke-RestMethod -Uri https://get.scoop.sh | Invoke-Expression
```
***After Installing Scoop:***
```
scoop bucket add main
scoop install main/git
scoop install main/go
scoop install main/tinygo
```

### Setup Rasperry Pi Pico:
 - Hold down the button
 - Plug in to the computer with USB while holding down the button
 - Release the button

#

### Clone & Setup Repository:
```
git clone https://github.com/felixgoff/HydroponicsPi.git
cd ./HydroponicsPi
go install
```

Compile code and flash it to the device:
`tinygo flash -target=pico-w ./rPi.go`



### Todo list:
 - Fix the Wifi
 ### Rules:
 - Please dont vibe code the whole thing
 - Asking Ai about help or what this does, recommended for solution and suggestions is okay.
 - Use a smart AI
