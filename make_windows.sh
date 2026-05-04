pyinstaller --onedir ^
--add-binary "ffmpeg/ffmpeg.exe;ffmpeg" ^
--add-binary "ffmpeg/ffprobe.exe;ffmpeg" ^
--add-binary "ffmpeg/ffplay.exe;ffmpeg" ^
--name descargador ^
--icon icon.ico ^
downloader.py