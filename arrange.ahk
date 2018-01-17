#SingleInstance force

moveWindow(winTitle, xCoord, yCoord, width, height) {
    WinRestore, %winTitle%
    WinMove, %winTitle%, , %xCoord%, %yCoord%, %width%, %height%
}

IfWinExist, ATDS {
    moveWindow(ATDS, 640, 0, 1280, 720)
    return
}

IfWinExist, python.exe {
    moveWindow(python.exe, 0, 0, 640, 1080)
    return
}
