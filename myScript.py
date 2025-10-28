#!/usr/bin/env python3
"""
YouTube Playlist Downloader - Modern GUI
Downloads YouTube playlists in the highest quality available.
Requires: pip install yt-dlp customtkinter
"""

import os
import sys
import threading
from pathlib import Path
from tkinter import filedialog
import customtkinter as ctk

try:
    import yt_dlp
except ImportError:
    print("Error: yt-dlp is not installed.")
    print("Please install it using: pip install yt-dlp")
    sys.exit(1)


class YouTubeDownloaderGUI:
    def __init__(self):
        # Set appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Create main window
        self.root = ctk.CTk()
        self.root.title("YouTube Playlist Downloader")
        self.root.geometry("700x550")
        self.root.resizable(False, False)
        
        self.is_downloading = False
        self.output_dir = str(Path.home() / "Downloads" / "YouTube")
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface."""
        # Main container
        main_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Title
        title = ctk.CTkLabel(
            main_frame,
            text="YouTube Playlist Downloader",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title.pack(pady=(0, 10))
        
        subtitle = ctk.CTkLabel(
            main_frame,
            text="Download playlists in the highest quality",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        subtitle.pack(pady=(0, 30))
        
        # URL Input Section
        url_frame = ctk.CTkFrame(main_frame)
        url_frame.pack(fill="x", pady=(0, 20))
        
        url_label = ctk.CTkLabel(
            url_frame,
            text="Playlist URL",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        url_label.pack(anchor="w", padx=20, pady=(15, 5))
        
        self.url_entry = ctk.CTkEntry(
            url_frame,
            placeholder_text="https://www.youtube.com/playlist?list=...",
            height=45,
            font=ctk.CTkFont(size=13)
        )
        self.url_entry.pack(fill="x", padx=20, pady=(0, 15))
        
        # Output Directory Section
        dir_frame = ctk.CTkFrame(main_frame)
        dir_frame.pack(fill="x", pady=(0, 20))
        
        dir_label = ctk.CTkLabel(
            dir_frame,
            text="Download Location",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        dir_label.pack(anchor="w", padx=20, pady=(15, 5))
        
        dir_select_frame = ctk.CTkFrame(dir_frame, fg_color="transparent")
        dir_select_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        self.dir_label = ctk.CTkLabel(
            dir_select_frame,
            text=self.output_dir,
            font=ctk.CTkFont(size=12),
            anchor="w"
        )
        self.dir_label.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        browse_btn = ctk.CTkButton(
            dir_select_frame,
            text="Browse",
            width=100,
            command=self.browse_directory
        )
        browse_btn.pack(side="right")
        
        # Progress Section
        progress_frame = ctk.CTkFrame(main_frame)
        progress_frame.pack(fill="x", pady=(0, 20))
        
        self.status_label = ctk.CTkLabel(
            progress_frame,
            text="Ready to download",
            font=ctk.CTkFont(size=13),
            anchor="w"
        )
        self.status_label.pack(anchor="w", padx=20, pady=(15, 10))
        
        self.progress_bar = ctk.CTkProgressBar(progress_frame)
        self.progress_bar.pack(fill="x", padx=20, pady=(0, 15))
        self.progress_bar.set(0)
        
        # Download Button
        self.download_btn = ctk.CTkButton(
            main_frame,
            text="Download Playlist",
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self.start_download
        )
        self.download_btn.pack(fill="x", pady=(0, 10))
        
        # Log text area
        log_frame = ctk.CTkFrame(main_frame)
        log_frame.pack(fill="both", expand=True)
        
        log_label = ctk.CTkLabel(
            log_frame,
            text="Download Log",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        log_label.pack(anchor="w", padx=15, pady=(10, 5))
        
        self.log_text = ctk.CTkTextbox(
            log_frame,
            height=100,
            font=ctk.CTkFont(size=11)
        )
        self.log_text.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
    def browse_directory(self):
        """Open directory browser."""
        directory = filedialog.askdirectory(initialdir=self.output_dir)
        if directory:
            self.output_dir = directory
            self.dir_label.configure(text=directory)
            self.log_message(f"Output directory changed to: {directory}")
    
    def log_message(self, message):
        """Add message to log."""
        self.log_text.insert("end", f"{message}\n")
        self.log_text.see("end")
    
    def update_status(self, message, progress=None):
        """Update status label and progress bar."""
        self.status_label.configure(text=message)
        if progress is not None:
            self.progress_bar.set(progress)
    
    def progress_hook(self, d):
        """Handle download progress."""
        if d['status'] == 'downloading':
            try:
                percent_str = d.get('_percent_str', '0%').strip()
                percent = float(percent_str.replace('%', '')) / 100
                speed = d.get('_speed_str', 'N/A')
                eta = d.get('_eta_str', 'N/A')
                
                self.root.after(0, self.update_status, 
                              f"Downloading... {percent_str} | Speed: {speed} | ETA: {eta}",
                              percent)
            except:
                pass
        elif d['status'] == 'finished':
            filename = os.path.basename(d.get('filename', 'Unknown'))
            self.root.after(0, self.log_message, f"✓ Completed: {filename}")
    
    def download_playlist(self):
        """Download the playlist."""
        url = self.url_entry.get().strip()
        
        if not url:
            self.root.after(0, self.update_status, "Error: Please enter a URL", 0)
            self.root.after(0, self.log_message, "❌ Error: No URL provided")
            self.is_downloading = False
            self.download_btn.configure(state="normal", text="Download Playlist")
            return
        
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': os.path.join(self.output_dir, '%(playlist_title)s/%(playlist_index)s - %(title)s.%(ext)s'),
            'merge_output_format': 'mp4',
            'ignoreerrors': True,
            'quiet': True,
            'no_warnings': True,
            'progress_hooks': [self.progress_hook],
        }
        
        try:
            self.root.after(0, self.log_message, f"Starting download from: {url}")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if 'entries' in info:
                    playlist_title = info.get('title', 'Unknown')
                    video_count = len(info['entries'])
                    
                    self.root.after(0, self.log_message, 
                                  f"Playlist: {playlist_title} ({video_count} videos)")
                    self.root.after(0, self.update_status, 
                                  f"Downloading {video_count} videos...", 0.1)
                
                ydl.download([url])
            
            self.root.after(0, self.update_status, "Download completed!", 1.0)
            self.root.after(0, self.log_message, "✅ All downloads completed successfully!")
            
        except Exception as e:
            self.root.after(0, self.update_status, "Download failed!", 0)
            self.root.after(0, self.log_message, f"❌ Error: {str(e)}")
        
        finally:
            self.is_downloading = False
            self.download_btn.configure(state="normal", text="Download Playlist")
    
    def start_download(self):
        """Start download in a separate thread."""
        if self.is_downloading:
            return
        
        self.is_downloading = True
        self.download_btn.configure(state="disabled", text="Downloading...")
        self.progress_bar.set(0)
        self.log_text.delete("1.0", "end")
        
        download_thread = threading.Thread(target=self.download_playlist, daemon=True)
        download_thread.start()
    
    def run(self):
        """Run the application."""
        self.root.mainloop()


if __name__ == "__main__":
    app = YouTubeDownloaderGUI()
    app.run()