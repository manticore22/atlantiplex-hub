#!/usr/bin/env python3
"""
🌊 MATRIX BROADCAST STUDIO - SYSTEM TRAY INTEGRATION
Professional background operation with system tray integration and comprehensive status display
Features: System tray, background processing, real-time status, notifications
"""

import os
import sys
import time
import json
import threading
import subprocess
import logging
import psutil
from datetime import datetime
from pathlib import Path

# Try to import system tray libraries
try:
    import pystray
    from pystray import MenuItem as item
    from PIL import Image, ImageDraw
    TRAY_AVAILABLE = True
except ImportError:
    TRAY_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('matrix_studio.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MatrixTrayApp:
    """Professional system tray application with comprehensive status"""
    
    def __init__(self, port=8080):
        self.port = port
        self.app_process = None
        self.running = False
        self.status = {
            'app': 'stopped',
            'guest_count': 0,
            'scene_count': 0,
            'streaming': False,
            'viewer_count': 0,
            'uptime': 0,
            'cpu_usage': 0.0,
            'memory_usage': 0.0,
            'disk_usage': 0.0
            'port': port,
            'active_platforms': []
        }
        self.start_time = None
        self.notification_count = 0
        
        logger.info(f"🌊 Matrix Tray App initialized on port {port}")
    
    def create_icon(self):
        """Create Matrix-style icon for system tray"""
        if not TRAY_AVAILABLE:
            return None
            
        # Create a more elaborate Matrix-style icon
        image = Image.new('RGB', (64, 64), color='black')
        draw = ImageDraw.Draw(image)
        
        # Draw stylized "M" for Matrix
        # Left vertical line
        draw.line([(8, 16), (8, 48)], fill='lime', width=3)
        # Top horizontal line
        draw.line([(8, 16), (24, 16)], fill='lime', width=3)
        # Diagonal down to middle
        draw.line([(24, 16), (40, 32)], fill='lime', width=3)
        # Diagonal up to bottom
        draw.line([(24, 48), (40, 32)], fill='lime', width=3)
        # Right vertical line
        draw.line([(40, 32), (40, 48)], fill='lime', width=3)
        # Bottom horizontal line
        draw.line([(40, 48), (56, 48)], fill='lime', width=3)
        
        # Second M (smaller)
        draw.line([(16, 28), (16, 44)], fill='green', width=2)
        draw.line([(16, 28), (20, 28)], fill='green', width=2)
        draw.line([(20, 28), (26, 36)], fill='green', width=2)
        draw.line([(26, 36), (26, 44)], fill='green', width=2)
        draw.line([(26, 44), (32, 44)], fill='green', width=2)
        draw.line([(32, 44), (32, 56)], fill='green', width=2)
        draw.line([(32, 56), (48, 56)], fill='green', width=2)
        
        # Add digital effect dots
        for i in range(3):
            x = 10 + i * 20
            y = 52
            draw.ellipse([x-1, y-1, x+1, y+1], fill='cyan', outline='cyan')
        
        return image
    
    def update_status(self):
        """Update system status information"""
        try:
            # System resource usage
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            self.status.update({
                'cpu_usage': cpu_percent,
                'memory_usage': memory.percent,
                'disk_usage': disk.percent,
                'timestamp': datetime.now().isoformat()
            })
            
            # Calculate uptime
            if self.start_time:
                self.status['uptime'] = int((datetime.now() - self.start_time).total_seconds())
            
        except Exception as e:
            logger.error(f"Error updating status: {e}")
    
    def show_notification(self, title, message):
        """Show system notification"""
        try:
            import win10toast
            win10toast.ToastNotifier().show_toast(
                "Matrix Broadcast Studio",
                f"{title}\n{message}",
                duration=5,
                icon_path=None
                threaded=True
            )
            self.notification_count += 1
        except ImportError:
            # Fallback to simple notification
            print(f"🔔 {title}: {message}")
        except Exception as e:
            logger.error(f"Notification error: {e}")
    
    def get_status_text(self):
        """Get formatted status text"""
        cpu_usage = self.status.get('cpu_usage', 0)
        memory_usage = self.status.get('memory_usage', 0)
        uptime = self.status.get('uptime', 0)
        guest_count = self.status.get('guest_count', 0)
        
        return (
            f"CPU: {cpu_usage:.1f}% | "
            f"Memory: {memory_usage:.1f}% | "
            f"Uptime: {uptime//60}:{uptime%60:02d} | "
            f"Guests: {guest_count}/6 | "
            f"Notifications: {self.notification_count}"
        )
    
    def get_status_details(self):
        """Get detailed status information"""
        return (
            f"Matrix Broadcast Studio Status\n"
            f"═══════════════════════════\n"
            f"🌊 Application: {self.status['app'].upper()}\n"
            f"📡 Port: {self.status['port']}\n"
            f"👥 Guests: {self.status['guest_count']}/6\n"
            f"🎬 Scenes: {self.status['scene_count']}\n"
            f"📹 Streaming: {'Active' if self.status['streaming'] else 'Stopped'}\n"
            f"👀 Viewers: {self.status['viewer_count']}\n"
            f"⏱️  Uptime: {self.status['uptime']} seconds\n"
            f"💻 CPU Usage: {self.status['cpu_usage']:.1f}%\n"
            f"🧠 Memory Usage: {self.status['memory_usage']:.1f}%\n"
            f"💾 Disk Usage: {self.status['disk_usage']:.1f}%\n"
            f"🔔 Notifications: {self.notification_count}\n"
            f"═════════════════════════\n"
            f"Last Updated: {self.status.get('timestamp', 'Never')}\n"
        )
    
    def get_menu_items(self):
        """Get context menu items"""
        return (
            item('Show Status', self.show_status_window),
            item('Open Web Interface', self.open_browser),
            item('Open API Docs', self.open_api_docs),
            item('System Info', self.show_system_info),
            pystray.Menu.SEPARATOR,
            item('Guest Management', self.open_guest_management),
            item('Scene Manager', self.open_scene_manager),
            item('Broadcast Control', self.open_broadcast_control),
            pystray.Menu.SEPARATOR,
            item('Restart Studio', self.restart_app),
            item('Stop Studio', self.stop_app),
            pystray.Menu.SEPARATOR,
            item('Notifications', self.notification_menu),
            item('Exit', self.quit_app, default=True)
        )
    
    def show_status_window(self):
        """Show detailed status window"""
        try:
            import tkinter as tk
            from tkinter import messagebox
            
            root = tk.Tk()
            root.title("🌊 Matrix Broadcast Studio - System Status")
            root.geometry("600x400")
            root.configure(bg='#000000', fg='#00ff00')
            root.option_add('*foreground', '#00ff00')
            root.option_add('*background', '#000000')
            
            # Create status display
            status_text = tk.Text(
                root,
                bg='#000000',
                fg='#00ff00',
                font=('Consolas', 10),
                wrap=tk.WORD,
                width=70,
                height=20
            )
            status_text.pack(padx=10, pady=10)
            
            # Insert status
            status_text.insert('1.0', self.get_status_details())
            
            root.mainloop()
            
        except Exception as e:
            logger.error(f"Status window error: {e}")
            self.show_notification("Status Window", f"Error: {str(e)}")
    
    def open_browser(self, icon=None, item=None):
        """Open web interface in browser"""
        try:
            import webbrowser
            url = f"http://localhost:{self.port}"
            webbrowser.open(url)
            self.show_notification("Browser Opened", f"Opening {url}")
        except Exception as e:
            logger.error(f"Browser launch error: {e}")
            self.show_notification("Browser Error", f"Failed to open: {str(e)}")
    
    def open_api_docs(self, icon=None, item=None):
        """Open API documentation"""
        try:
            import webbrowser
            url = f"http://localhost:{self.port}/api"
            webbrowser.open(url)
            self.show_notification("API Docs Opened", f"Opening {url}")
        except Exception as e:
            logger.error(f"API docs error: {e}")
            self.show_notification("API Error", f"Failed to open: {str(e)}")
    
    def show_system_info(self, icon=None, item=None):
        """Show system information"""
        try:
            import tkinter as tk
            from tkinter import messagebox
            
            root = tk.Tk()
            root.title("🌊 Matrix Broadcast Studio - System Information")
            root.geometry("700x500")
            root.configure(bg='#000000', fg='#00ff00')
            root.option_add('*foreground', '#00ff00')
            root.option_add('*background', '#000000')
            
            # System info text
            info_text = f"""
            System Information
            ════════════════════════════════════════
            🖥️  Operating System: {os.name} {os.uname().release if hasattr(os, 'uname') else ''}
            💻 Python Version: {sys.version.split()[0]}
            🧠  Architecture: {os.uname().machine if hasattr(os, 'uname') else 'Unknown'}
            💾 Memory: {psutil.virtual_memory().total // (1024**3):,} GB Total
            💽 CPU: {psutil.cpu_count()} cores
            📀 Current Directory: {os.getcwd()}
            🌊 Matrix Studio Version: 2.0.0
            📡 Running Port: {self.port}
            ⏱️  Uptime: {self.status.get('uptime', 0)} seconds
            ════════════════════════════════════════════
            
            Component Status
            ════════════════════════════════════════
            🎬 Guest Manager: {'✅ Ready' if self.status['guest_count'] > 0 else '🔄 Ready'}
            🎭 Scene Manager: {'✅ Ready' if self.status['scene_count'] > 0 else '🔄 Ready'}
            🖼️  Avatar System: {'✅ Ready' if self.status.get('avatar_count', 0) > 0 else '🔄 Ready'}
            📹  Broadcasting: {'🟢 Live' if self.status['streaming'] else '⚫ Stopped'}
            🔌  API System: {'✅ Running' if self.status['app'] == 'running' else '🔄 Stopped'}
            ═══════════════════════════════════════════
            """
            
            text_widget = tk.Text(root, bg='#000000', fg='#00ff00', font=('Consolas', 9), wrap=tk.WORD)
            text_widget.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
            text_widget.insert('1.0', info_text)
            
            root.mainloop()
            
        except Exception as e:
            logger.error(f"System info window error: {e}")
            self.show_notification("System Info Error", f"Failed to show: {str(e)}")
    
    def open_guest_management(self, icon=None, item=None):
        """Open guest management"""
        self.open_browser()
    
    def open_scene_manager(self, icon=None, item=None):
        """Open scene manager"""
        self.open_browser()
    
    def open_broadcast_control(self, icon=None, item=None):
        """Open broadcast control"""
        self.open_browser()
    
    def notification_menu(self, icon=None, item=None):
        """Notification settings menu"""
        # Placeholder for notification settings
        self.show_notification("Notifications", "Notification settings coming soon!")
    
    def restart_app(self, icon=None, item=None):
        """Restart the application"""
        self.stop_app(icon, item)
        time.sleep(2)
        self.start_app()
    
    def stop_app(self, icon=None, item=None):
        """Stop the application"""
        self.running = False
        self.status['app'] = 'stopped'
        
        if self.app_process and self.app_process.poll() is None:
            self.app_process.terminate()
            try:
                self.app_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.app_process.kill()
        
        self.update_icon()
        self.show_notification("Studio Stopped", "Matrix Broadcast Studio has been stopped")
    
    def update_icon(self):
        """Update tray icon based on status"""
        if not TRAY_AVAILABLE:
            return
            
        # Update icon based on streaming status
        if self.status['streaming']:
            self.icon = self.create_icon()
        else:
            # Create grayscale version for stopped state
            icon = self.create_icon()
            if icon:
                icon = icon.convert('L')
                # Add Matrix green tint
                pixels = list(icon.getdata())
                for i in range(len(pixels)):
                    if i % 4 == 0 or i % 4 == 1:  # Keep green for Matrix parts
                        continue
                    r, g, b = pixels[i]
                    # Grayscale with Matrix green tint
                    gray = int(0.299 * r + 0.587 * g + 0.114 * b)
                    pixels[i] = (gray, gray, gray)
            self.icon = Image.fromarray(pixels)
    
    def start_app(self):
        """Start the main application"""
        try:
            # Find the main script
            script_path = Path(__file__).parent / "production_ready_backend.py"
            if not script_path.exists():
                script_path = Path(__file__).parent / "matrix_studio_final.py"
            
            self.app_process = subprocess.Popen([
                sys.executable,
                str(script_path),
                f"--port={self.port}"
            ])
            
            self.running = True
            self.status['app'] = 'running'
            self.start_time = datetime.now()
            
            self.update_icon()
            self.show_notification("Studio Started", f"Matrix Broadcast Studio running on port {self.port}")
            
            logger.info(f"🌊 Matrix Broadcast Studio started on port {self.port}")
            
        except Exception as e:
            logger.error(f"Failed to start application: {e}")
            self.show_notification("Start Error", f"Failed to start: {str(e)}")
    
    def run_tray(self):
        """Run the system tray application"""
        if not TRAY_AVAILABLE:
            logger.warning("System tray not available. Please install pystray and pillow")
            print("🌊 Matrix Broadcast Studio running in console mode...")
            self.start_app()
            return
        
        # Create menu
        menu = self.get_menu_items()
        
        # Create and run icon
        self.icon = self.create_icon()
        
        # Start the app
        self.start_app()
        
        # Update icon periodically
        def update_loop():
            while self.running:
                self.update_status()
                self.icon.update_menu()
                time.sleep(5)
        
        update_thread = threading.Thread(target=update_loop, daemon=True)
        update_thread.start()
        
        # Run the tray icon
        try:
            self.icon.run()
        except KeyboardInterrupt:
            logger.info("🌊 Matrix Broadcast Studio shutting down...")
        finally:
            self.stop_app()
    
    def run_console(self):
        """Run in console mode without tray"""
        print("🌊 MATRIX BROADCAST STUDIO - CONSOLE MODE")
        print("=" * 60)
        print("Professional broadcasting system - Console mode")
        print("=" * 60)
        print("Starting on port:", self.port)
        print("Press Ctrl+C to stop")
        print("=" * 60)
        
        try:
            self.start_app()
            
            # Console status updates
            while self.running:
                self.update_status()
                status_text = self.get_status_text()
                print(f"\r🌊 [{status_text}] {datetime.now().strftime('%H:%M:%S')}", end='', flush=True)
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n🌊 Matrix Broadcast Studio shutting down...")
        finally:
            self.stop_app()

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Matrix Broadcast Studio System Tray")
    parser.add_argument("--port", type=int, default=8080, help="Port to run the application on")
    parser.add_argument("--no-tray", action="store_true", help="Run without system tray")
    parser.add_argument("--install-deps", action="store_true", help="Install missing dependencies")
    args = parser.parse_args()
    
    if args.install_deps:
        print("🌊 Installing missing dependencies...")
        subprocess.run([
            sys.executable, "-m", "pip", "install", 
            "pystray", "pillow", "win10toast", "psutil"
        ])
        return
    
    print("🌊 MATRIX BROADCAST STUDIO - SYSTEM TRAY INTEGRATION")
    print("=" * 60)
    print("Professional broadcasting system with background operation")
    print("=" * 60)
    
    tray_app = MatrixTrayApp(port=args.port)
    
    if args.no_tray:
        tray_app.run_console()
    else:
        tray_app.run_tray()

if __name__ == "__main__":
    main()