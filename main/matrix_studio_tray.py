#!/usr/bin/env python3
"""
🌊 MATRIX BROADCAST STUDIO - SYSTEM TRAY INTEGRATION
Professional background operation with system tray support
"""

import sys
import os
import threading
import time
import webbrowser
from pathlib import Path
import subprocess

# Try to import system tray libraries
try:
    import pystray
    from pystray import MenuItem as item
    from PIL import Image, ImageDraw
    TRAY_AVAILABLE = True
except ImportError:
    TRAY_AVAILABLE = False
    print("⚠️  System tray functionality not available. Install with: pip install pystray pillow")

class MatrixTrayApp:
    def __init__(self, port=8080):
        self.port = port
        self.app_process = None
        self.running = False
        
    def create_icon(self):
        """Create Matrix-style icon for system tray"""
        if not TRAY_AVAILABLE:
            return None
            
        # Create a simple Matrix-style icon
        image = Image.new('RGB', (64, 64), color='black')
        draw = ImageDraw.Draw(image)
        
        # Draw Matrix-like M
        draw.line([(10, 50), (10, 10)], fill='lime', width=2)
        draw.line([(10, 10), (25, 30)], fill='lime', width=2)
        draw.line([(25, 30), (40, 10)], fill='lime', width=2)
        draw.line([(40, 10), (40, 50)], fill='lime', width=2)
        draw.line([(45, 50), (45, 10), (55, 10), (55, 50)], fill='lime', width=2)
        
        return image
    
    def start_app(self):
        """Start the Matrix Broadcast Studio in background"""
        try:
            # Start the main application
            script_path = Path(__file__).parent / "matrix_studio_final.py"
            self.app_process = subprocess.Popen([
                sys.executable, str(script_path), "--port", str(self.port)
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            self.running = True
            print(f"✅ Matrix Broadcast Studio started on port {self.port}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start application: {e}")
            return False
    
    def stop_app(self):
        """Stop the Matrix Broadcast Studio"""
        if self.app_process:
            self.app_process.terminate()
            self.app_process.wait()
            self.running = False
            print("🌊 Matrix Broadcast Studio stopped")
    
    def open_browser(self):
        """Open web interface in browser"""
        webbrowser.open(f"http://localhost:{self.port}")
    
    def open_api_docs(self):
        """Open API documentation in browser"""
        webbrowser.open(f"http://localhost:{self.port}/api")
    
    def show_status(self):
        """Show current status"""
        if self.running:
            print(f"🌊 Matrix Broadcast Studio is running on port {self.port}")
            print(f"📱 Web Interface: http://localhost:{self.port}")
            print(f"🔌 API Endpoint: http://localhost:{self.port}/api")
        else:
            print("❌ Matrix Broadcast Studio is not running")
    
    def run_tray(self):
        """Run system tray application"""
        if not TRAY_AVAILABLE:
            print("❌ System tray not available. Please install pystray and pillow")
            return False
            
        # Create menu
        menu = pystray.Menu(
            item('Open Web Interface', self.open_browser),
            item('API Documentation', self.open_api_docs),
            item('Show Status', self.show_status),
            pystray.Menu.SEPARATOR,
            item('Restart Studio', self.restart_app),
            item('Stop Studio', self.stop_and_exit),
            pystray.Menu.SEPARATOR,
            item('Exit', self.quit)
        )
        
        # Create and run tray icon
        icon = pystray.Icon(
            "matrix_studio",
            self.create_icon(),
            "Matrix Broadcast Studio",
            menu
        )
        
        # Start the app first
        if self.start_app():
            print("🌊 Starting Matrix Broadcast Studio with system tray...")
            print("📍 Right-click the system tray icon for options")
            icon.run()
        
        return True
    
    def restart_app(self):
        """Restart the application"""
        self.stop_app()
        time.sleep(2)
        self.start_app()
    
    def stop_and_exit(self):
        """Stop app and remove tray icon"""
        self.stop_app()
        if TRAY_AVAILABLE:
            import pystray
            pystray.Icon.stop(pystray.Icon("matrix_studio"))
    
    def quit(self):
        """Quit the application"""
        self.stop_app()
        if TRAY_AVAILABLE:
            import pystray
            pystray.Icon.stop(pystray.Icon("matrix_studio"))
        sys.exit(0)

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Matrix Broadcast Studio System Tray")
    parser.add_argument("--port", type=int, default=8080, help="Port to run the application on")
    parser.add_argument("--no-tray", action="store_true", help="Run without system tray")
    
    args = parser.parse_args()
    
    print("🌊 MATRIX BROADCAST STUDIO - SYSTEM TRAY MODE")
    print("=" * 50)
    
    tray_app = MatrixTrayApp(port=args.port)
    
    if args.no_tray:
        # Run without tray
        if tray_app.start_app():
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                tray_app.stop_app()
    else:
        # Run with tray
        tray_app.run_tray()

if __name__ == "__main__":
    main()