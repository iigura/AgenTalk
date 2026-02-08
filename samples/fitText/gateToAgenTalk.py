import sys
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import AgenTalk

dirs=['./gate','./result','./archive','./error']
for d in dirs:
	p=Path(d)
	p.mkdir(parents=True,exist_ok=True)

AgenTalk.init('../../config.yaml')
Count=0

class IncomingFileHandler(FileSystemEventHandler):
    def on_created(self,e):
        global Count
        if not e.is_directory:
            targetFilePath=e.src_path
            print(f"[{Count}] detect new file:",targetFilePath)
            Count+=1
            session=AgenTalk.newSession(f"fitText_{targetFilePath}")
            absPath=Path(e.src_path).resolve() 
            session.invoke('fitText.firstDraft',str(absPath))

observer=Observer()
eventHandler=IncomingFileHandler()
observer.schedule(eventHandler,'./gate',recursive=False)
observer.start()

print(f"started {sys.argv[0]}")
try:
    observer.join()
except KeyboardInterrupt:
    observer.stop()
    observer.join()
print(f"terminated {sys.argv[0]}")

