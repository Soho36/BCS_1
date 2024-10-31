import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

path = 'C:\\Users\\Liikurserv\\AppData\\Roaming\\MetaQuotes\\Terminal\\1D0E83E0BCAA42603583233CF21A762C\\MQL5\\Files'
file = 'OHLCVData_475.csv'


class CsvChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        print(f"File modified: {event.src_path}")  # This should print on any modification
        if not event.src_path.endswith(file):  # Replace with your CSV file path
            return
        print("CSV file updated; triggering function calls...")
        run_main_functions()  # Call a function that contains your main calls


def run_main_functions():
    print('The file has been changed')


if __name__ == "__main__":
    event_handler = CsvChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)  # CSV folder path
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
