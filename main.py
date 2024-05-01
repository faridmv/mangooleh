'''
Created on May 1, 2024

@author: Farid
'''

import requests
import threading
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import platform
import os
import time

class DownloadManager:
    def __init__(self, root):
        self.root = root
        self.url_entry = None
        self.num_chunks_entry = None
        self.output_file_entry = None
        self.download_button = None
        self.pause_button = None
        self.resume_button = None
        self.stop_button = None
        self.download_threads = []
        self.pause_event = threading.Event()
        self.stop_event = threading.Event()
        self.progress_bar = None
        self.total_size_label = None
        self.downloaded_label = None
        self.remaining_label = None
        self.downloaded_bytes = 0
        self.total_size = 0
        self.speed_label = None
        self.elapsed_label = None
        self.remaining_time_label = None
        
        self.default_num_chunks = 4
        self.default_chunk_size = 65536
        
        # Initialize start time
        self.start_time = time.time()

    def create_widgets(self):
        tk.Label(self.root, text="URL:").grid(row=0, column=0)
        self.url_entry = tk.Entry(self.root, width=150)
        self.url_entry.grid(row=0, column=1, columnspan=3)

        tk.Label(self.root, text="Number of Chunks:").grid(row=1, column=0)
        self.num_chunks_entry = tk.Entry(self.root)
        self.num_chunks_entry.grid(row=1, column=1)

        tk.Label(self.root, text="Output File:").grid(row=2, column=0)
        self.output_file_entry = tk.Entry(self.root, width=150)
        self.output_file_entry.grid(row=2, column=1, columnspan=3)

        self.download_button = tk.Button(self.root, text="Download", command=self.start_download)
        self.download_button.grid(row=3, column=0)

        self.pause_button = tk.Button(self.root, text="Pause", command=self.pause_download)
        self.pause_button.grid(row=3, column=1)

        self.resume_button = tk.Button(self.root, text="Resume", command=self.resume_download)
        self.resume_button.grid(row=3, column=2)

        self.stop_button = tk.Button(self.root, text="Stop", command=self.stop_download)
        self.stop_button.grid(row=3, column=3)

        self.progress_bar = ttk.Progressbar(self.root, mode='determinate')  
        self.progress_bar.grid(row=4, column=0, columnspan=4, padx=5, pady=5, sticky='we')
        
        # Create labels
        self.total_size_label = tk.Label(self.root, text="Total Size: 0 bytes")
        self.total_size_label.grid(row=5, column=0, padx=10, pady=5)
        
        self.downloaded_label = tk.Label(self.root, text="Downloaded: 0 bytes")
        self.downloaded_label.grid(row=6, column=0, padx=10, pady=5)
        
        self.remaining_label = tk.Label(self.root, text="Remaining: 0 bytes")
        self.remaining_label.grid(row=7, column=0, padx=10, pady=5)
        
        self.speed_label = tk.Label(self.root, text="Download Speed: 0 bytes/second")
        self.speed_label.grid(row=8, column=0, padx=10, pady=5)
        
        self.elapsed_label = tk.Label(self.root, text="Time Elapsed: 0 seconds")
        self.elapsed_label.grid(row=9, column=0, padx=10, pady=5)
        
        self.remaining_time_label = tk.Label(self.root, text="Remaining Time: N/A")
        self.remaining_time_label.grid(row=10, column=0, padx=10, pady=5)

    def download_chunk(self, url, start_byte, end_byte, file_path):
        print(f"Downloading chunk: {start_byte}-{end_byte}")
        print(f"URL: {url}")
        try:
            headers = {'Range': f'bytes={start_byte}-{end_byte}'}
            response = requests.get(url, headers=headers, stream=True)
            print(f"Response status code: {response.status_code}")
            print(f"Response headers: {response.headers}")
    
            with open(file_path, 'r+b') as f:
                f.seek(start_byte)
                self.downloaded_bytes = start_byte
    
                for chunk in response.iter_content(chunk_size=self.default_chunk_size):
                    if chunk:
                        f.write(chunk)
                        self.downloaded_bytes += len(chunk)
                        progress = (self.downloaded_bytes / end_byte) * 100
                        self.progress_bar["value"] = progress
                        self.root.update_idletasks()  # Update the GUI
                        if self.stop_event.is_set():
                            break
        except Exception as e:
            print(f"Error occurred: {e}")

    #===========================================================================
    # def download_file(self, url):
    #     try:
    #         response = requests.head(url)
    #         self.total_size = int(response.headers.get('content-length', 0))
    #         chunk_size = (self.total_size + self.default_num_chunks - 1) // self.default_num_chunks
    # 
    #         with open(self.output_file_entry.get(), 'wb') as f:
    #             start_byte = 0
    #             for _ in range(self.default_num_chunks):
    #                 end_byte = min(start_byte + chunk_size - 1, self.total_size - 1)
    #                 headers = {'Range': f'bytes={start_byte}-{end_byte}'}
    #                 response = requests.get(url, headers=headers, stream=True)
    #                 for chunk in response.iter_content(chunk_size=self.default_chunk_size):
    #                     if chunk:
    #                         f.write(chunk)
    #                         self.downloaded_bytes += len(chunk)
    #                         self.progress_bar["value"] += len(chunk) * 100 / self.total_size
    #                         self.update_labels()
    #                         self.root.update_idletasks()  # Update the GUI
    #                 start_byte = end_byte + 1
    # 
    #         messagebox.showinfo("Download Manager", "Download completed.")
    #     except Exception as e:
    #         messagebox.showerror("Download Manager", f"Error occurred: {e}")
    #     finally:
    #         self.download_button.config(state=tk.NORMAL)  # Re-enable the download button
    #===========================================================================
    
    def download_file(self):
        url = self.url_entry.get()
        output_file = self.output_file_entry.get()
    
        try:
            response = requests.get(url, stream=True)
            self.total_size = int(response.headers.get('content-length', 0))
            with open(output_file, 'wb') as f:
                self.downloaded_bytes = 0
                for chunk in response.iter_content(chunk_size=self.default_chunk_size):
                    if chunk:
                        f.write(chunk)
                        self.downloaded_bytes += len(chunk)
                        progress = (self.downloaded_bytes / self.total_size) * 100
                        self.progress_bar["value"] = progress
                        self.root.update_idletasks()  # Update the GUI
                        self.update_labels()
            messagebox.showinfo("Download Manager", "Download completed.")
        except Exception as e:
            messagebox.showerror("Download Manager", f"Error occurred: {e}")

    def start_download(self):
        url = self.url_entry.get()
        self.download_button.config(state=tk.DISABLED)  # Disable the download button
        #download_thread = threading.Thread(target=self.download_file, args=(url,))
        download_thread = threading.Thread(target=self.download_file)
        download_thread.start()

    def pause_download(self):
        self.pause_event.set()

    def resume_download(self):
        self.pause_event.clear()

    def stop_download(self):
        self.stop_event.set()
        for thread in self.download_threads:
            thread.join()
        messagebox.showinfo("Download Manager", "Download stopped.")
    
    def get_default_download_folder(self):
        system = platform.system()
        if system == 'Windows':
            return os.path.join(os.environ['USERPROFILE'], 'Downloads')
        elif system == 'Darwin':  # macOS
            return os.path.join(os.path.expanduser('~'), 'Downloads')
        elif system == 'Linux':
            return os.path.join(os.path.expanduser('~'), 'Downloads')
        else:
            return None
    
    def set_output_file(self, file_path):
        self.output_file_entry.delete(0, tk.END)
        self.output_file_entry.insert(0, file_path)
    
    def set_num_chunks_entry(self, num_chunks_entry):
        self.num_chunks_entry.delete(0, tk.END)
        self.num_chunks_entry.insert(0, num_chunks_entry)
    
    def get_default_num_chunks(self):
        return self.default_num_chunks
    
    def update_labels(self):
        # Update labels with file size, downloaded bytes, and remaining bytes
        self.total_size_label.config(text=f"Total Size: {self.total_size} bytes")
        self.downloaded_label.config(text=f"Downloaded: {self.downloaded_bytes} bytes")
        remaining_bytes = max(self.total_size - self.downloaded_bytes, 0)
        self.remaining_label.config(text=f"Remaining: {remaining_bytes} bytes")
        
        # Calculate download speed
        current_time = time.time()
        elapsed_time = current_time - self.start_time
        download_speed_bytes = self.downloaded_bytes / elapsed_time if elapsed_time > 0 else 0
        download_speed_mb = download_speed_bytes / (1024 * 1024)  # Convert bytes to megabytes
        self.speed_label.config(text=f"Speed: {download_speed_mb:.2f} MB/second")
        
        # Update elapsed time
        self.elapsed_label.config(text=f"Time Elapsed: {elapsed_time:.2f} seconds")
        
        # Calculate remaining time
        remaining_time = (remaining_bytes / download_speed_mb) if download_speed_mb > 0 else 0
        self.remaining_time_label.config(text=f"Remaining Time: {remaining_time:.2f} seconds")

def main():
    root = tk.Tk()
    root.title("Mangooleh - Download Manager")

    manager = DownloadManager(root)
    manager.create_widgets()
    
    manager.set_output_file(manager.get_default_download_folder())
    manager.set_num_chunks_entry(manager.get_default_num_chunks())

    root.mainloop()

if __name__ == "__main__":
    main()
