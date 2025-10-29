#!/usr/bin/env python3
"""
YouTube Playlist Downloader - Modern Futuristic UI
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


class ModernButton(ctk.CTkButton):
    """Custom modern button with hover effects."""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.default_color = kwargs.get('fg_color', ("#0EA5E9", "#0284C7"))
        self.hover_color = kwargs.get('hover_color', ("#06B6D4", "#0891B2"))
        
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
    
    def on_enter(self, e):
        self.configure(fg_color=self.hover_color)
    
    def on_leave(self, e):
        self.configure(fg_color=self.default_color)


class YouTubeDownloaderGUI:
    def __init__(self):
        # Set appearance - Dark mode
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Create main window
        self.root = ctk.CTk()
        self.root.title("YouTube Playlist Downloader")
        self.root.geometry("1000x800")
        
        # Configure colors - Futuristic palette
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
        
        # Configure root background
        self.root.configure(fg_color=self.colors['bg_primary'])
        
        self.is_downloading = False
        self.output_dir = str(Path.home() / "Downloads" / "YouTube")
        self.video_frames = {}
        self.current_video = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the futuristic user interface."""
        # Main container with padding
        main_container = ctk.CTkFrame(self.root, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=25, pady=25)
        
        # ===== HEADER SECTION =====
        header_frame = ctk.CTkFrame(
            main_container,
            fg_color=self.colors['bg_secondary'],
            corner_radius=20,
            height=90
        )
        header_frame.pack(fill="x", pady=(0, 20))
        header_frame.pack_propagate(False)
        
        # Icon and Title
        header_content = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_content.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Icon (using emoji as placeholder)
        icon_label = ctk.CTkLabel(
            header_content,
            text="▶",
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color=self.colors['accent_cyan']
        )
        icon_label.pack(side="left", padx=(0, 15))
        
        # Title container
        title_container = ctk.CTkFrame(header_content, fg_color="transparent")
        title_container.pack(side="left", fill="both", expand=True)
        
        title = ctk.CTkLabel(
            title_container,
            text="YouTube Playlist Downloader",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=self.colors['text_primary']
        )
        title.pack(anchor="w")
        
        subtitle = ctk.CTkLabel(
            title_container,
            text="Download entire playlists in the highest quality",
            font=ctk.CTkFont(size=13),
            text_color=self.colors['text_secondary']
        )
        subtitle.pack(anchor="w")
        
        # ===== URL INPUT SECTION =====
        url_section = ctk.CTkFrame(
            main_container,
            fg_color=self.colors['bg_secondary'],
            corner_radius=20
        )
        url_section.pack(fill="x", pady=(0, 15))
        
        url_content = ctk.CTkFrame(url_section, fg_color="transparent")
        url_content.pack(fill="x", padx=25, pady=20)
        
        url_label = ctk.CTkLabel(
            url_content,
            text="📎 Playlist URL",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors['text_primary'],
            anchor="w"
        )
        url_label.pack(anchor="w", pady=(0, 10))
        
        # URL input with paste button
        url_input_frame = ctk.CTkFrame(url_content, fg_color="transparent")
        url_input_frame.pack(fill="x")
        
        self.url_entry = ctk.CTkEntry(
            url_input_frame,
            placeholder_text="https://www.youtube.com/playlist?list=...",
            height=50,
            font=ctk.CTkFont(size=13),
            fg_color=self.colors['bg_card'],
            border_color=self.colors['accent_cyan'],
            border_width=2,
            corner_radius=12
        )
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        paste_btn = ctk.CTkButton(
            url_input_frame,
            text="📋 Paste",
            width=100,
            height=50,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=self.colors['accent_cyan'],
            hover_color=self.colors['accent_blue'],
            corner_radius=12,
            command=self.paste_url
        )
        paste_btn.pack(side="right")
        
        # ===== DOWNLOAD LOCATION SECTION =====
        location_section = ctk.CTkFrame(
            main_container,
            fg_color=self.colors['bg_secondary'],
            corner_radius=20
        )
        location_section.pack(fill="x", pady=(0, 15))
        
        location_content = ctk.CTkFrame(location_section, fg_color="transparent")
        location_content.pack(fill="x", padx=25, pady=20)
        
        location_label = ctk.CTkLabel(
            location_content,
            text="📁 Download Location",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors['text_primary'],
            anchor="w"
        )
        location_label.pack(anchor="w", pady=(0, 10))
        
        location_frame = ctk.CTkFrame(location_content, fg_color="transparent")
        location_frame.pack(fill="x")
        
        self.dir_display = ctk.CTkEntry(
            location_frame,
            height=50,
            font=ctk.CTkFont(size=12),
            fg_color=self.colors['bg_card'],
            border_color=self.colors['accent_purple'],
            border_width=2,
            corner_radius=12,
            state="readonly"
        )
        self.dir_display.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.dir_display.configure(state="normal")
        self.dir_display.insert(0, self.output_dir)
        self.dir_display.configure(state="readonly")
        
        browse_btn = ctk.CTkButton(
            location_frame,
            text="🔍 Browse",
            width=120,
            height=50,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=self.colors['accent_purple'],
            hover_color="#7C3AED",
            corner_radius=12,
            command=self.browse_directory
        )
        browse_btn.pack(side="right")
        
        # ===== PROGRESS SECTION =====
        progress_section = ctk.CTkFrame(
            main_container,
            fg_color=self.colors['bg_secondary'],
            corner_radius=20
        )
        progress_section.pack(fill="x", pady=(0, 15))
        
        progress_content = ctk.CTkFrame(progress_section, fg_color="transparent")
        progress_content.pack(fill="x", padx=25, pady=20)
        
        # Status and video count
        status_header = ctk.CTkFrame(progress_content, fg_color="transparent")
        status_header.pack(fill="x", pady=(0, 10))
        
        self.status_label = ctk.CTkLabel(
            status_header,
            text="⚡ Ready to download",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=self.colors['text_primary'],
            anchor="w"
        )
        self.status_label.pack(side="left")
        
        self.video_count_label = ctk.CTkLabel(
            status_header,
            text="0 videos",
            font=ctk.CTkFont(size=12),
            text_color=self.colors['text_secondary'],
            anchor="e"
        )
        self.video_count_label.pack(side="right")
        
        # Progress bar with gradient effect
        self.progress_bar = ctk.CTkProgressBar(
            progress_content,
            height=12,
            corner_radius=6,
            progress_color=self.colors['accent_cyan'],
            fg_color=self.colors['bg_card']
        )
        self.progress_bar.pack(fill="x")
        self.progress_bar.set(0)
        
        # ===== DOWNLOAD BUTTON =====
        self.download_btn = ctk.CTkButton(
            main_container,
            text="⬇ Download Playlist",
            height=60,
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color=(self.colors['accent_cyan'], self.colors['accent_blue']),
            hover_color=self.colors['accent_blue'],
            corner_radius=15,
            command=self.start_download
        )
        self.download_btn.pack(fill="x", pady=(0, 20))
        
        # ===== VIDEO LIST SECTION =====
        list_section = ctk.CTkFrame(
            main_container,
            fg_color=self.colors['bg_secondary'],
            corner_radius=20
        )
        list_section.pack(fill="both", expand=True)
        
        list_header = ctk.CTkFrame(list_section, fg_color="transparent")
        list_header.pack(fill="x", padx=25, pady=(20, 10))
        
        list_title = ctk.CTkLabel(
            list_header,
            text="🎬 Videos",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors['text_primary']
        )
        list_title.pack(side="left")
        
        # Scrollable video list
        self.video_list_scroll = ctk.CTkScrollableFrame(
            list_section,
            fg_color="transparent",
            corner_radius=0
        )
        self.video_list_scroll.pack(fill="both", expand=True, padx=25, pady=(0, 20))
    
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
            self.dir_display.configure(state="normal")
            self.dir_display.delete(0, "end")
            self.dir_display.insert(0, directory)
            self.dir_display.configure(state="readonly")
    
    def update_status(self, message, progress=None):
        """Update status label and progress bar."""
        self.status_label.configure(text=message)
        if progress is not None:
            self.progress_bar.set(progress)
    
    def add_video_to_list(self, video_id, title, index):
        """Add a video card to the list."""
        # Video card with glassmorphism effect
        video_card = ctk.CTkFrame(
            self.video_list_scroll,
            fg_color=self.colors['bg_card'],
            corner_radius=15,
            height=85
        )
        video_card.pack(fill="x", pady=6)
        video_card.pack_propagate(False)
        
        # Add subtle border effect
        video_card.configure(border_width=1, border_color=("#2D3748", "#374151"))
        
        card_content = ctk.CTkFrame(video_card, fg_color="transparent")
        card_content.pack(fill="both", expand=True, padx=20, pady=15)
        
        # Left side - Index and title
        left_container = ctk.CTkFrame(card_content, fg_color="transparent")
        left_container.pack(side="left", fill="both", expand=True)
        
        # Index badge
        index_badge = ctk.CTkLabel(
            left_container,
            text=f"{index}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors['accent_cyan'],
            width=35,
            height=35,
            fg_color=("#1E293B", "#0F172A"),
            corner_radius=8
        )
        index_badge.pack(side="left", padx=(0, 15))
        
        # Title and info container
        title_container = ctk.CTkFrame(left_container, fg_color="transparent")
        title_container.pack(side="left", fill="both", expand=True)
        
        title_label = ctk.CTkLabel(
            title_container,
            text=title[:65] + "..." if len(title) > 65 else title,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.colors['text_primary'],
            anchor="w"
        )
        title_label.pack(anchor="w")
        
        download_info_label = ctk.CTkLabel(
            title_container,
            text="",
            font=ctk.CTkFont(size=10),
            text_color=self.colors['text_secondary'],
            anchor="w"
        )
        download_info_label.pack(anchor="w", pady=(2, 0))
        
        # Right side - Status and progress
        right_container = ctk.CTkFrame(card_content, fg_color="transparent")
        right_container.pack(side="right", padx=(10, 0))
        
        status_label = ctk.CTkLabel(
            right_container,
            text="⏳ Waiting",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=self.colors['text_secondary'],
            width=130
        )
        status_label.pack(anchor="e")
        
        progress_bar = ctk.CTkProgressBar(
            right_container,
            width=130,
            height=6,
            corner_radius=3,
            progress_color=self.colors['accent_cyan'],
            fg_color=("#1E293B", "#0F172A")
        )
        progress_bar.pack(anchor="e", pady=(5, 0))
        progress_bar.set(0)
        
        self.video_frames[video_id] = {
            'card': video_card,
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
                # Change progress bar color based on status
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
                                      self.current_video, "✓ Complete", 1.0, self.colors['success'], "")
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
                
                self.root.after(0, self.update_status, 
                              f"⬇ Downloading... {percent_str} • {speed}",
                              None)
                
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
            self.root.after(0, self.update_status, "❌ Error: Please enter a URL", 0)
            self.is_downloading = False
            self.download_btn.configure(state="normal", text="⬇ Download Playlist")
            return
        
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        
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
                self.root.after(0, self.update_status, "🔍 Fetching playlist...", 0.05)
                info = ydl.extract_info(url, download=False)
                
                if 'entries' in info:
                    entries = [e for e in info['entries'] if e]
                    video_count = len(entries)
                    
                    self.root.after(0, self.video_count_label.configure, 
                                  {"text": f"{video_count} videos"})
                    self.root.after(0, self.update_status, 
                                  f"✨ Found {video_count} videos", 0.1)
                    
                    for idx, entry in enumerate(entries, 1):
                        video_id = entry.get('id', f'video_{idx}')
                        title = entry.get('title', 'Unknown Title')
                        self.root.after(0, self.add_video_to_list, video_id, title, idx)
                
                self.root.after(0, self.update_status, "⚡ Downloading...", 0.15)
                ydl.download([url])
                
                if self.current_video and self.current_video in self.video_frames:
                    self.root.after(0, self.update_video_status,
                                  self.current_video, "✓ Complete", 1.0, self.colors['success'], "")
            
            self.root.after(0, self.update_status, "🎉 All downloads completed!", 1.0)
            
        except Exception as e:
            self.root.after(0, self.update_status, f"❌ Error: {str(e)}", 0)
        
        finally:
            self.is_downloading = False
            self.download_btn.configure(state="normal", text="⬇ Download Playlist")
    
    def start_download(self):
        """Start download in a separate thread."""
        if self.is_downloading:
            return
        
        self.is_downloading = True
        self.download_btn.configure(state="disabled", text="⏳ Downloading...")
        self.progress_bar.set(0)
        
        download_thread = threading.Thread(target=self.download_playlist, daemon=True)
        download_thread.start()
    
    def run(self):
        """Run the application."""
        self.root.mainloop()


if __name__ == "__main__":
    app = YouTubeDownloaderGUI()
    app.run()