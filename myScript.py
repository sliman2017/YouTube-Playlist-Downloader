#!/usr/bin/env python3
"""
YouTube Playlist Downloader - Dual View Modern UI
Downloads YouTube playlists in the highest quality available.
Requires: pip install yt-dlp customtkinter pillow requests
"""

import os
import sys
import threading
from pathlib import Path
from tkinter import filedialog
import customtkinter as ctk
from urllib.request import urlopen
from io import BytesIO

# Get the directory where the executable is located
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
else:
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

try:
    from PIL import Image, ImageTk
except ImportError:
    Image = None
    ImageTk = None


class YouTubeDownloaderGUI:
    def __init__(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.root = ctk.CTk()
        self.root.title("YouTube Playlist Downloader")
        self.root.geometry("500x400")
        
        self.colors = {
            'bg_primary': '#0A0E1A',
            'bg_secondary': '#111827',
            'bg_card': '#1F2937',
            'accent_cyan': '#06B6D4',
            'accent_blue': '#3B82F6',
            'accent_purple': '#8B5CF6',
            'text_primary': '#F9FAFB',
            'text_secondary': '#9CA3AF',
            'success': '#10B981',
            'warning': '#F59E0B',
            'error': '#EF4444'
        }
        
        self.root.configure(fg_color=self.colors['bg_primary'])
        
        self.is_downloading = False
        self.output_dir = str(Path.home() / "Downloads" / "YouTube")
        self.video_frames = {}
        self.current_video = None
        self.download_quality = "highest"
        self.thumbnail_cache = {}
        
        self.setup_compact_view()
        
    def setup_compact_view(self):
        """Compact input view for starting downloads."""
        self.compact_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.compact_frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Logo/Header
        header = ctk.CTkFrame(self.compact_frame, fg_color=self.colors['bg_secondary'], corner_radius=15)
        header.pack(fill="x", pady=(0, 25))
        
        header_content = ctk.CTkFrame(header, fg_color="transparent")
        header_content.pack(padx=25, pady=20)
        
        icon = ctk.CTkLabel(
            header_content,
            text="▶",
            font=ctk.CTkFont(size=42, weight="bold"),
            text_color=self.colors['accent_cyan']
        )
        icon.pack()
        
        title = ctk.CTkLabel(
            header_content,
            text="YouTube Playlist Downloader",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=self.colors['text_primary']
        )
        title.pack(pady=(10, 0))
        
        subtitle = ctk.CTkLabel(
            header_content,
            text="Download entire playlists in highest quality",
            font=ctk.CTkFont(size=12),
            text_color=self.colors['text_secondary']
        )
        subtitle.pack()
        
        # URL Input
        url_frame = ctk.CTkFrame(self.compact_frame, fg_color=self.colors['bg_secondary'], corner_radius=12)
        url_frame.pack(fill="x", pady=(0, 12))
        
        url_label = ctk.CTkLabel(
            url_frame,
            text="📎 Playlist URL",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.colors['text_primary']
        )
        url_label.pack(anchor="w", padx=20, pady=(15, 8))
        
        url_input_container = ctk.CTkFrame(url_frame, fg_color="transparent")
        url_input_container.pack(fill="x", padx=20, pady=(0, 15))
        
        self.url_entry = ctk.CTkEntry(
            url_input_container,
            placeholder_text="Paste YouTube playlist URL here...",
            height=45,
            font=ctk.CTkFont(size=12),
            fg_color=self.colors['bg_card'],
            border_color=self.colors['accent_cyan'],
            border_width=2,
            corner_radius=10
        )
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        
        paste_btn = ctk.CTkButton(
            url_input_container,
            text="📋",
            width=45,
            height=45,
            font=ctk.CTkFont(size=16),
            fg_color=self.colors['accent_cyan'],
            hover_color=self.colors['accent_blue'],
            corner_radius=10,
            command=self.paste_url
        )
        paste_btn.pack(side="right")
        
        # Location Input
        location_frame = ctk.CTkFrame(self.compact_frame, fg_color=self.colors['bg_secondary'], corner_radius=12)
        location_frame.pack(fill="x", pady=(0, 12))
        
        loc_label = ctk.CTkLabel(
            location_frame,
            text="📁 Save To",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.colors['text_primary']
        )
        loc_label.pack(anchor="w", padx=20, pady=(15, 8))
        
        loc_input_container = ctk.CTkFrame(location_frame, fg_color="transparent")
        loc_input_container.pack(fill="x", padx=20, pady=(0, 15))
        
        self.dir_entry = ctk.CTkEntry(
            loc_input_container,
            height=45,
            font=ctk.CTkFont(size=11),
            fg_color=self.colors['bg_card'],
            border_color=self.colors['accent_purple'],
            border_width=2,
            corner_radius=10
        )
        self.dir_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.dir_entry.insert(0, self.output_dir)
        
        browse_btn = ctk.CTkButton(
            loc_input_container,
            text="🔍",
            width=45,
            height=45,
            font=ctk.CTkFont(size=16),
            fg_color=self.colors['accent_purple'],
            hover_color="#7C3AED",
            corner_radius=10,
            command=self.browse_directory
        )
        browse_btn.pack(side="right")
        
        # Quality selector
        quality_frame = ctk.CTkFrame(self.compact_frame, fg_color=self.colors['bg_secondary'], corner_radius=12)
        quality_frame.pack(fill="x", pady=(0, 20))
        
        quality_content = ctk.CTkFrame(quality_frame, fg_color="transparent")
        quality_content.pack(fill="x", padx=20, pady=15)
        
        quality_label = ctk.CTkLabel(
            quality_content,
            text="⚙️ Quality",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.colors['text_primary']
        )
        quality_label.pack(side="left")
        
        self.quality_selector = ctk.CTkSegmentedButton(
            quality_content,
            values=["Highest", "1080p", "720p", "Audio Only"],
            command=self.quality_changed,
            font=ctk.CTkFont(size=11),
            fg_color=self.colors['bg_card'],
            selected_color=self.colors['accent_cyan'],
            selected_hover_color=self.colors['accent_blue']
        )
        self.quality_selector.pack(side="right")
        self.quality_selector.set("Highest")
        
        # Download Button
        self.download_btn = ctk.CTkButton(
            self.compact_frame,
            text="⬇ Start Download",
            height=55,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=self.colors['accent_cyan'],
            hover_color=self.colors['accent_blue'],
            corner_radius=12,
            command=self.start_download
        )
        self.download_btn.pack(fill="x")
    
    def setup_download_view(self):
        """Expanded view showing download progress."""
        # Destroy compact view
        self.compact_frame.pack_forget()
        
        # Expand window
        self.root.geometry("1200x800")
        
        # Create download view
        self.download_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.download_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Top control bar
        control_bar = ctk.CTkFrame(self.download_frame, fg_color=self.colors['bg_secondary'], corner_radius=15, height=80)
        control_bar.pack(fill="x", pady=(0, 15))
        control_bar.pack_propagate(False)
        
        control_content = ctk.CTkFrame(control_bar, fg_color="transparent")
        control_content.pack(fill="both", expand=True, padx=25, pady=15)
        
        # Left side - Title and stats
        left_info = ctk.CTkFrame(control_content, fg_color="transparent")
        left_info.pack(side="left", fill="both", expand=True)
        
        self.playlist_title_label = ctk.CTkLabel(
            left_info,
            text="Downloading Playlist...",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors['text_primary'],
            anchor="w"
        )
        self.playlist_title_label.pack(anchor="w")
        
        stats_container = ctk.CTkFrame(left_info, fg_color="transparent")
        stats_container.pack(anchor="w", pady=(5, 0))
        
        self.video_count_label = ctk.CTkLabel(
            stats_container,
            text="0 videos",
            font=ctk.CTkFont(size=11),
            text_color=self.colors['text_secondary']
        )
        self.video_count_label.pack(side="left", padx=(0, 15))
        
        self.total_size_label = ctk.CTkLabel(
            stats_container,
            text="Total: 0 MB",
            font=ctk.CTkFont(size=11),
            text_color=self.colors['text_secondary']
        )
        self.total_size_label.pack(side="left", padx=(0, 15))
        
        self.speed_label = ctk.CTkLabel(
            stats_container,
            text="Speed: 0 MB/s",
            font=ctk.CTkFont(size=11),
            text_color=self.colors['accent_cyan']
        )
        self.speed_label.pack(side="left")
        
        # Right side - Actions
        right_actions = ctk.CTkFrame(control_content, fg_color="transparent")
        right_actions.pack(side="right")
        
        self.pause_btn = ctk.CTkButton(
            right_actions,
            text="⏸",
            width=45,
            height=45,
            font=ctk.CTkFont(size=18),
            fg_color=self.colors['warning'],
            hover_color="#D97706",
            corner_radius=10,
            state="disabled"
        )
        self.pause_btn.pack(side="left", padx=(0, 8))
        
        self.cancel_btn = ctk.CTkButton(
            right_actions,
            text="✕",
            width=45,
            height=45,
            font=ctk.CTkFont(size=18),
            fg_color=self.colors['error'],
            hover_color="#DC2626",
            corner_radius=10,
            command=self.cancel_download
        )
        self.cancel_btn.pack(side="left")
        
        # Overall progress
        progress_section = ctk.CTkFrame(self.download_frame, fg_color=self.colors['bg_secondary'], corner_radius=15)
        progress_section.pack(fill="x", pady=(0, 15))
        
        progress_content = ctk.CTkFrame(progress_section, fg_color="transparent")
        progress_content.pack(fill="x", padx=25, pady=15)
        
        progress_header = ctk.CTkFrame(progress_content, fg_color="transparent")
        progress_header.pack(fill="x", pady=(0, 8))
        
        self.status_label = ctk.CTkLabel(
            progress_header,
            text="⚡ Starting download...",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.colors['text_primary']
        )
        self.status_label.pack(side="left")
        
        self.progress_percentage = ctk.CTkLabel(
            progress_header,
            text="0%",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.colors['accent_cyan']
        )
        self.progress_percentage.pack(side="right")
        
        self.progress_bar = ctk.CTkProgressBar(
            progress_content,
            height=10,
            corner_radius=5,
            progress_color=self.colors['accent_cyan'],
            fg_color=self.colors['bg_card']
        )
        self.progress_bar.pack(fill="x")
        self.progress_bar.set(0)
        
        # Video list
        list_section = ctk.CTkFrame(self.download_frame, fg_color=self.colors['bg_secondary'], corner_radius=15)
        list_section.pack(fill="both", expand=True)
        
        list_header = ctk.CTkFrame(list_section, fg_color="transparent")
        list_header.pack(fill="x", padx=25, pady=(15, 10))
        
        list_title = ctk.CTkLabel(
            list_header,
            text="🎬 Videos",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors['text_primary']
        )
        list_title.pack(side="left")
        
        self.video_list_scroll = ctk.CTkScrollableFrame(
            list_section,
            fg_color="transparent"
        )
        self.video_list_scroll.pack(fill="both", expand=True, padx=25, pady=(0, 20))
    
    def quality_changed(self, value):
        """Handle quality selection change."""
        quality_map = {
            "Highest": "highest",
            "1080p": "1080p",
            "720p": "720p",
            "Audio Only": "audio"
        }
        self.download_quality = quality_map.get(value, "highest")
    
    def paste_url(self):
        """Paste URL from clipboard."""
        try:
            clipboard_text = self.root.clipboard_get()
            self.url_entry.delete(0, "end")
            self.url_entry.insert(0, clipboard_text)
        except:
            pass
    
    def browse_directory(self):
        """Open directory browser."""
        directory = filedialog.askdirectory(initialdir=self.output_dir)
        if directory:
            self.output_dir = directory
            self.dir_entry.delete(0, "end")
            self.dir_entry.insert(0, directory)
    
    def cancel_download(self):
        """Cancel download and return to compact view."""
        self.is_downloading = False
        self.download_frame.pack_forget()
        self.root.geometry("500x400")
        self.setup_compact_view()
    
    def update_status(self, message, progress=None):
        """Update status label and progress bar."""
        if hasattr(self, 'status_label'):
            self.status_label.configure(text=message)
        if progress is not None and hasattr(self, 'progress_bar'):
            self.progress_bar.set(progress)
            if hasattr(self, 'progress_percentage'):
                self.progress_percentage.configure(text=f"{int(progress * 100)}%")
    
    def add_video_to_list(self, video_id, title, index, thumbnail_url=None):
        """Add a video card to the list with thumbnail."""
        video_card = ctk.CTkFrame(
            self.video_list_scroll,
            fg_color=self.colors['bg_card'],
            corner_radius=12,
            height=110
        )
        video_card.pack(fill="x", pady=5)
        video_card.pack_propagate(False)
        
        card_content = ctk.CTkFrame(video_card, fg_color="transparent")
        card_content.pack(fill="both", expand=True, padx=15, pady=12)
        
        # Thumbnail placeholder
        thumbnail_frame = ctk.CTkFrame(
            card_content,
            width=140,
            height=85,
            fg_color=self.colors['bg_primary'],
            corner_radius=8
        )
        thumbnail_frame.pack(side="left", padx=(0, 15))
        thumbnail_frame.pack_propagate(False)
        
        # Index on thumbnail
        index_label = ctk.CTkLabel(
            thumbnail_frame,
            text=str(index),
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.colors['accent_cyan']
        )
        index_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Info container
        info_container = ctk.CTkFrame(card_content, fg_color="transparent")
        info_container.pack(side="left", fill="both", expand=True)
        
        # Title
        title_label = ctk.CTkLabel(
            info_container,
            text=title[:80] + "..." if len(title) > 80 else title,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.colors['text_primary'],
            anchor="w",
            wraplength=600
        )
        title_label.pack(anchor="w")
        
        # Download info
        download_info_label = ctk.CTkLabel(
            info_container,
            text="",
            font=ctk.CTkFont(size=10),
            text_color=self.colors['text_secondary'],
            anchor="w"
        )
        download_info_label.pack(anchor="w", pady=(3, 0))
        
        # Progress bar
        progress_container = ctk.CTkFrame(info_container, fg_color="transparent")
        progress_container.pack(fill="x", pady=(8, 0))
        
        progress_bar = ctk.CTkProgressBar(
            progress_container,
            height=6,
            corner_radius=3,
            progress_color=self.colors['accent_cyan'],
            fg_color=self.colors['bg_primary']
        )
        progress_bar.pack(side="left", fill="x", expand=True, padx=(0, 10))
        progress_bar.set(0)
        
        # Status
        status_label = ctk.CTkLabel(
            progress_container,
            text="⏳ Waiting",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=self.colors['text_secondary'],
            width=100
        )
        status_label.pack(side="right")
        
        self.video_frames[video_id] = {
            'card': video_card,
            'thumbnail': thumbnail_frame,
            'index_label': index_label,
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
                if progress >= 1.0:
                    self.video_frames[video_id]['progress'].configure(
                        progress_color=self.colors['success']
                    )
            if download_info is not None:
                self.video_frames[video_id]['download_info'].configure(text=download_info)
    
    def progress_hook(self, d):
        """Handle download progress."""
        if d['status'] == 'downloading':
            try:
                info_dict = d.get('info_dict', {})
                video_id = info_dict.get('id', '')
                
                if video_id and video_id != self.current_video:
                    if self.current_video and self.current_video in self.video_frames:
                        self.root.after(0, self.update_video_status, 
                                      self.current_video, "✓ Done", 1.0, self.colors['success'], "")
                    self.current_video = video_id
                
                percent_str = d.get('_percent_str', '0%').strip()
                percent = float(percent_str.replace('%', '')) / 100
                speed = d.get('_speed_str', 'N/A').strip()
                
                downloaded_bytes = d.get('downloaded_bytes', 0)
                total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                
                def format_bytes(bytes_num):
                    if bytes_num == 0:
                        return "0 B"
                    for unit in ['B', 'KB', 'MB', 'GB']:
                        if bytes_num < 1024.0:
                            return f"{bytes_num:.1f} {unit}"
                        bytes_num /= 1024.0
                    return f"{bytes_num:.1f} TB"
                
                downloaded_str = format_bytes(downloaded_bytes)
                total_str = format_bytes(total_bytes) if total_bytes > 0 else "?"
                
                download_info = f"📥 {downloaded_str} / {total_str} • {speed}"
                
                self.root.after(0, self.speed_label.configure, {"text": f"Speed: {speed}"})
                self.root.after(0, self.update_status, f"⬇ Downloading... {percent_str}", None)
                
                if video_id:
                    self.root.after(0, self.update_video_status,
                                  video_id, f"⬇ {percent_str}", percent, self.colors['accent_cyan'], download_info)
            except:
                pass
                
        elif d['status'] == 'finished':
            info_dict = d.get('info_dict', {})
            video_id = info_dict.get('id', '')
            if video_id:
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
                download_info = f"✓ {size_str}"
                
                self.root.after(0, self.update_video_status,
                              video_id, "🔄 Merging", 1.0, self.colors['warning'], download_info)
    
    def download_playlist(self):
        """Download the playlist."""
        url = self.url_entry.get().strip()
        
        if not url:
            return
        
        self.output_dir = self.dir_entry.get().strip()
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        
        # Build format string based on quality
        format_str = 'bestvideo+bestaudio/best'
        if self.download_quality == '1080p':
            format_str = 'bestvideo[height<=1080]+bestaudio/best[height<=1080]'
        elif self.download_quality == '720p':
            format_str = 'bestvideo[height<=720]+bestaudio/best[height<=720]'
        elif self.download_quality == 'audio':
            format_str = 'bestaudio/best'
        
        ydl_opts = {
            'format': format_str,
            'outtmpl': os.path.join(self.output_dir, '%(playlist_title)s/%(playlist_index)s - %(title)s.%(ext)s'),
            'merge_output_format': 'mp4' if self.download_quality != 'audio' else 'm4a',
            'ignoreerrors': True,
            'quiet': True,
            'no_warnings': True,
            'progress_hooks': [self.progress_hook],
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.root.after(0, self.update_status, "🔍 Fetching playlist info...", 0.05)
                info = ydl.extract_info(url, download=False)
                
                if 'entries' in info:
                    playlist_title = info.get('title', 'Unknown Playlist')
                    entries = [e for e in info['entries'] if e]
                    video_count = len(entries)
                    
                    self.root.after(0, self.playlist_title_label.configure, {"text": playlist_title})
                    self.root.after(0, self.video_count_label.configure, {"text": f"{video_count} videos"})
                    self.root.after(0, self.update_status, f"✨ Found {video_count} videos", 0.1)
                    
                    for idx, entry in enumerate(entries, 1):
                        video_id = entry.get('id', f'video_{idx}')
                        title = entry.get('title', 'Unknown Title')
                        thumbnail = entry.get('thumbnail')
                        self.root.after(0, self.add_video_to_list, video_id, title, idx, thumbnail)
                
                self.root.after(0, self.update_status, "⚡ Starting downloads...", 0.15)
                ydl.download([url])
                
                if self.current_video and self.current_video in self.video_frames:
                    self.root.after(0, self.update_video_status,
                                  self.current_video, "✓ Done", 1.0, self.colors['success'], "")
            
            self.root.after(0, self.update_status, "🎉 All downloads completed!", 1.0)
            
        except Exception as e:
            self.root.after(0, self.update_status, f"❌ Error: {str(e)}", 0)
        
        finally:
            self.is_downloading = False
    
    def start_download(self):
        """Start download in a separate thread."""
        if self.is_downloading:
            return
        
        url = self.url_entry.get().strip()
        if not url:
            return
        
        self.is_downloading = True
        
        # Switch to download view
        self.setup_download_view()
        
        download_thread = threading.Thread(target=self.download_playlist, daemon=True)
        download_thread.start()
    
    def run(self):
        """Run the application."""
        self.root.mainloop()


if __name__ == "__main__":
    app = YouTubeDownloaderGUI()
    app.run()