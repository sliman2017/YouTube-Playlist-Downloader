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

# Get the directory where the executable is located
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    application_path = os.path.dirname(sys.executable)
else:
    # Running as script
    application_path = os.path.dirname(os.path.abspath(__file__))

# Add ffmpeg to PATH if it exists in the app directory
ffmpeg_path = os.path.join(application_path, 'ffmpeg.exe')
if os.path.exists(ffmpeg_path):
    os.environ["PATH"] = application_path + os.pathsep + os.environ["PATH"]

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
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        self.is_downloading = False
        self.output_dir = str(Path.home() / "Downloads" / "YouTube")
        self.video_frames = {}
        self.current_video = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface."""
        # Main container
        main_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title = ctk.CTkLabel(
            main_frame,
            text="YouTube Playlist Downloader",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=(0, 5))
        
        subtitle = ctk.CTkLabel(
            main_frame,
            text="Download playlists in the highest quality",
            font=ctk.CTkFont(size=13),
            text_color="gray"
        )
        subtitle.pack(pady=(0, 20))
        
        # URL Input Section
        url_frame = ctk.CTkFrame(main_frame)
        url_frame.pack(fill="x", pady=(0, 15))
        
        url_label = ctk.CTkLabel(
            url_frame,
            text="Playlist URL",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        url_label.pack(anchor="w", padx=15, pady=(12, 5))
        
        self.url_entry = ctk.CTkEntry(
            url_frame,
            placeholder_text="https://www.youtube.com/playlist?list=...",
            height=40,
            font=ctk.CTkFont(size=12)
        )
        self.url_entry.pack(fill="x", padx=15, pady=(0, 12))
        
        # Output Directory Section
        dir_frame = ctk.CTkFrame(main_frame)
        dir_frame.pack(fill="x", pady=(0, 15))
        
        dir_label = ctk.CTkLabel(
            dir_frame,
            text="Download Location",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        dir_label.pack(anchor="w", padx=15, pady=(12, 5))
        
        dir_select_frame = ctk.CTkFrame(dir_frame, fg_color="transparent")
        dir_select_frame.pack(fill="x", padx=15, pady=(0, 12))
        
        self.dir_label = ctk.CTkLabel(
            dir_select_frame,
            text=self.output_dir,
            font=ctk.CTkFont(size=11),
            anchor="w"
        )
        self.dir_label.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        browse_btn = ctk.CTkButton(
            dir_select_frame,
            text="Browse",
            width=90,
            height=32,
            command=self.browse_directory
        )
        browse_btn.pack(side="right")
        
        # Progress Section
        progress_frame = ctk.CTkFrame(main_frame)
        progress_frame.pack(fill="x", pady=(0, 15))
        
        self.status_label = ctk.CTkLabel(
            progress_frame,
            text="Ready to download",
            font=ctk.CTkFont(size=12),
            anchor="w"
        )
        self.status_label.pack(anchor="w", padx=15, pady=(12, 8))
        
        self.progress_bar = ctk.CTkProgressBar(progress_frame)
        self.progress_bar.pack(fill="x", padx=15, pady=(0, 12))
        self.progress_bar.set(0)
        
        # Download Button
        self.download_btn = ctk.CTkButton(
            main_frame,
            text="Download Playlist",
            height=45,
            font=ctk.CTkFont(size=15, weight="bold"),
            command=self.start_download
        )
        self.download_btn.pack(fill="x", pady=(0, 15))
        
        # Video List Section
        list_frame = ctk.CTkFrame(main_frame)
        list_frame.pack(fill="both", expand=True)
        
        list_header = ctk.CTkFrame(list_frame)
        list_header.pack(fill="x", padx=15, pady=(12, 8))
        
        list_label = ctk.CTkLabel(
            list_header,
            text="Videos",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w"
        )
        list_label.pack(side="left")
        
        self.video_count_label = ctk.CTkLabel(
            list_header,
            text="0 videos",
            font=ctk.CTkFont(size=11),
            text_color="gray",
            anchor="e"
        )
        self.video_count_label.pack(side="right")
        
        # Scrollable frame for video list
        self.video_list_scroll = ctk.CTkScrollableFrame(
            list_frame,
            fg_color="transparent"
        )
        self.video_list_scroll.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
    def browse_directory(self):
        """Open directory browser."""
        directory = filedialog.askdirectory(initialdir=self.output_dir)
        if directory:
            self.output_dir = directory
            self.dir_label.configure(text=directory)
    
    def update_status(self, message, progress=None):
        """Update status label and progress bar."""
        self.status_label.configure(text=message)
        if progress is not None:
            self.progress_bar.set(progress)
    
    def add_video_to_list(self, video_id, title, index):
        """Add a video to the list."""
        video_frame = ctk.CTkFrame(self.video_list_scroll, height=70)
        video_frame.pack(fill="x", pady=4)
        video_frame.pack_propagate(False)
        
        # Left side - number and title
        left_frame = ctk.CTkFrame(video_frame, fg_color="transparent")
        left_frame.pack(side="left", fill="both", expand=True, padx=12, pady=8)
        
        number_label = ctk.CTkLabel(
            left_frame,
            text=f"{index}.",
            font=ctk.CTkFont(size=11, weight="bold"),
            width=30,
            anchor="w"
        )
        number_label.pack(side="left", padx=(0, 8))
        
        # Title and download info container
        title_container = ctk.CTkFrame(left_frame, fg_color="transparent")
        title_container.pack(side="left", fill="both", expand=True)
        
        title_label = ctk.CTkLabel(
            title_container,
            text=title[:70] + "..." if len(title) > 70 else title,
            font=ctk.CTkFont(size=11),
            anchor="w"
        )
        title_label.pack(anchor="w")
        
        # Download info (speed and size)
        download_info_label = ctk.CTkLabel(
            title_container,
            text="",
            font=ctk.CTkFont(size=9),
            text_color="gray",
            anchor="w"
        )
        download_info_label.pack(anchor="w")
        
        # Right side - status and progress
        right_frame = ctk.CTkFrame(video_frame, fg_color="transparent")
        right_frame.pack(side="right", padx=12, pady=8)
        
        status_label = ctk.CTkLabel(
            right_frame,
            text="⏳ Waiting",
            font=ctk.CTkFont(size=11),
            text_color="gray",
            width=120
        )
        status_label.pack(anchor="e")
        
        # Progress bar for this video
        progress_bar = ctk.CTkProgressBar(right_frame, width=120, height=4)
        progress_bar.pack(anchor="e", pady=(4, 0))
        progress_bar.set(0)
        
        self.video_frames[video_id] = {
            'frame': video_frame,
            'status': status_label,
            'progress': progress_bar,
            'download_info': download_info_label,
            'title': title
        }
    
    def update_video_status(self, video_id, status, progress=None, color=None, download_info=None):
        """Update a video's status in the list."""
        if video_id in self.video_frames:
            self.video_frames[video_id]['status'].configure(text=status)
            if color:
                self.video_frames[video_id]['status'].configure(text_color=color)
            if progress is not None:
                self.video_frames[video_id]['progress'].set(progress)
            if download_info is not None:
                self.video_frames[video_id]['download_info'].configure(text=download_info)
    
    def progress_hook(self, d):
        """Handle download progress."""
        if d['status'] == 'downloading':
            try:
                # Get current video info
                info_dict = d.get('info_dict', {})
                video_id = info_dict.get('id', '')
                
                if video_id and video_id != self.current_video:
                    if self.current_video and self.current_video in self.video_frames:
                        self.root.after(0, self.update_video_status, 
                                      self.current_video, "✓ Downloaded", 1.0, "#00ff00", "")
                    self.current_video = video_id
                
                percent_str = d.get('_percent_str', '0%').strip()
                percent = float(percent_str.replace('%', '')) / 100
                speed = d.get('_speed_str', 'N/A').strip()
                
                # Get downloaded size and total size
                downloaded_bytes = d.get('downloaded_bytes', 0)
                total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                
                # Format sizes
                def format_bytes(bytes_num):
                    if bytes_num == 0:
                        return "0 B"
                    for unit in ['B', 'KB', 'MB', 'GB']:
                        if bytes_num < 1024.0:
                            return f"{bytes_num:.1f} {unit}"
                        bytes_num /= 1024.0
                    return f"{bytes_num:.1f} TB"
                
                downloaded_str = format_bytes(downloaded_bytes)
                total_str = format_bytes(total_bytes) if total_bytes > 0 else "Unknown"
                
                # Create download info string
                download_info = f"📥 {downloaded_str} / {total_str} • {speed}"
                
                # Update main progress
                self.root.after(0, self.update_status, 
                              f"Downloading... {percent_str} | Speed: {speed}",
                              None)
                
                # Update video-specific progress with size and speed info
                if video_id:
                    self.root.after(0, self.update_video_status,
                                  video_id, f"⬇️ {percent_str}", percent, "#3b8ed0", download_info)
            except:
                pass
                
        elif d['status'] == 'finished':
            info_dict = d.get('info_dict', {})
            video_id = info_dict.get('id', '')
            if video_id:
                # Get final file size
                file_size = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                
                def format_bytes(bytes_num):
                    if bytes_num == 0:
                        return "0 B"
                    for unit in ['B', 'KB', 'MB', 'GB']:
                        if bytes_num < 1024.0:
                            return f"{bytes_num:.1f} {unit}"
                        bytes_num /= 1024.0
                    return f"{bytes_num:.1f} TB"
                
                size_str = format_bytes(file_size)
                download_info = f"✓ Downloaded • {size_str}"
                
                self.root.after(0, self.update_video_status,
                              video_id, "🔄 Processing", 1.0, "#ff9500", download_info)
    
    def download_playlist(self):
        """Download the playlist."""
        url = self.url_entry.get().strip()
        
        if not url:
            self.root.after(0, self.update_status, "Error: Please enter a URL", 0)
            self.is_downloading = False
            self.download_btn.configure(state="normal", text="Download Playlist")
            return
        
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        
        # Clear previous video list
        for widget in self.video_list_scroll.winfo_children():
            widget.destroy()
        self.video_frames.clear()
        self.current_video = None
        
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
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # First, extract playlist info
                self.root.after(0, self.update_status, "Fetching playlist information...", 0.05)
                info = ydl.extract_info(url, download=False)
                
                if 'entries' in info:
                    playlist_title = info.get('title', 'Unknown')
                    entries = [e for e in info['entries'] if e]
                    video_count = len(entries)
                    
                    self.root.after(0, self.video_count_label.configure, 
                                  {"text": f"{video_count} videos"})
                    self.root.after(0, self.update_status, 
                                  f"Found {video_count} videos in playlist", 0.1)
                    
                    # Add all videos to the list
                    for idx, entry in enumerate(entries, 1):
                        video_id = entry.get('id', f'video_{idx}')
                        title = entry.get('title', 'Unknown Title')
                        self.root.after(0, self.add_video_to_list, video_id, title, idx)
                
                # Now download
                self.root.after(0, self.update_status, "Starting downloads...", 0.15)
                ydl.download([url])
                
                # Mark last video as complete
                if self.current_video and self.current_video in self.video_frames:
                    self.root.after(0, self.update_video_status,
                                  self.current_video, "✓ Downloaded", 1.0, "#00ff00", "")
            
            self.root.after(0, self.update_status, "All downloads completed!", 1.0)
            
        except Exception as e:
            self.root.after(0, self.update_status, f"Error: {str(e)}", 0)
        
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
        
        download_thread = threading.Thread(target=self.download_playlist, daemon=True)
        download_thread.start()
    
    def run(self):
        """Run the application."""
        self.root.mainloop()


if __name__ == "__main__":
    app = YouTubeDownloaderGUI()
    app.run()