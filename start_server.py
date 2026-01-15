#!/usr/bin/env python3
"""Start the OAIT WebSocket server."""

import uvicorn
from oait.config import get_settings

if __name__ == "__main__":
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
