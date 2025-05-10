activ_console = menubar.addMenu("Консоль")
activ_console_run = QAction("Запуск консоли", self)
activ_console_run.triggered.connect(lambda: subprocess.Popen('start cmd.exe /k echo Привет из Python!', shell=True))
activ_console.addAction(activ_console_run)