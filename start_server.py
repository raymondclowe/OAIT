#!/usr/bin/env python3
"""Start the OAIT WebSocket server."""

import uvicorn
import multiprocessing
import logging
from oait.config import get_settings

# Configure logging for oait modules
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
# Set oait modules to INFO level
logging.getLogger('oait').setLevel(logging.INFO)

# Set multiprocessing start method to 'spawn' to avoid semaphore leaks
# This must be done before any multiprocessing resources are created
if __name__ == "__main__":
    try:
        multiprocessing.set_start_method('spawn', force=True)
    except RuntimeError:
        pass  # Already set
    
    settings = get_settings()
    print(f"""
    ╔═══════════════════════════════════════════════════════════╗
    ║              OAIT - Observational AI Tutor                ║
    ║                  WebSocket Server                         ║
    ╚═══════════════════════════════════════════════════════════╝
    
    Starting server on {settings.server_host}:{settings.server_port}
    
    Open http://{settings.server_host if settings.server_host != '0.0.0.0' else 'localhost'}:{settings.server_port} in your browser
    
    Press Ctrl+C to stop the server
    """)
    
    uvicorn.run(
        "oait.server.websocket_server:app",
        host=settings.server_host,
        port=settings.server_port,
        log_level="info",
        reload=True  # Enable auto-reload during development
    )
