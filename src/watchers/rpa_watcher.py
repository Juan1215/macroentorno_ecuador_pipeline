import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from src.config import RPA_INBOX_DIR
from src.pipeline import run_pipeline
from src.utils.logger import write_log


class RPAHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            write_log(f'Archivo nuevo detectado desde RPA: {event.src_path}')
            run_pipeline(mode='rpa')


def watch_rpa_folder():
    RPA_INBOX_DIR.mkdir(parents=True, exist_ok=True)
    observer = Observer()
    observer.schedule(RPAHandler(), str(RPA_INBOX_DIR), recursive=False)
    observer.start()
    write_log(f'Monitoreando carpeta RPA: {RPA_INBOX_DIR}')
    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == '__main__':
    watch_rpa_folder()
