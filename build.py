import PyInstaller.__main__

PyInstaller.__main__.run([
    "lib/app.py",
    "--noconsole",
    "-F",
    "--distpath .",
    "-y",
    "-n CoffeeChatPairing",
    "--target-arch universal2",
])
