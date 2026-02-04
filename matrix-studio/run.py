#!/usr/bin/env python3
"""
🌊 MATRIX UNIFIED BROADCASTING STUDIO
Main entry point for the organized project structure
"""

import sys
import os
import argparse

# Add core directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core'))

if __name__ == '__main__':
    from unified_broadcast_server import unified_system, app, socketio
    
    parser = argparse.ArgumentParser(description='Matrix Unified Broadcasting Studio')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8080, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--init-db', action='store_true', help='Initialize database')
    
    args = parser.parse_args()
    
    if args.init_db:
        print("Initializing database...")
        with app.app_context():
            from unified_broadcast_server import db
            db.create_all()
        print("Database initialized successfully")
    else:
        print("Starting Matrix Unified Broadcasting Studio")
        print(f"Server will be available at: http://{args.host}:{args.port}")
        print("Studio Interface: http://localhost:8080")
        print("API Documentation: http://localhost:8080/api/docs")
        print("=" * 60)
        
        import time
        # Set start time for uptime calculation
        unified_system.start_time = time.time()
        
        # Start server
        socketio.run(
            app,
            host=args.host,
            port=args.port,
            debug=args.debug,
            allow_unsafe_werkzeug=True
        )