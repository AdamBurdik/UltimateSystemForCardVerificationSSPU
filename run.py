#!/usr/bin/env python3
"""
FastAPI development server startup script

Usage:
    ./run.py                    # Run on default port 8000
    ./run.py --port 5000        # Run on custom port
    ./run.py --reload          # Enable auto-reload
"""

import uvicorn
import argparse
import os

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run FastAPI development server")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    parser.add_argument("--env", choices=["dev", "test", "prod"], default="dev",
                       help="Environment (dev/test/prod)")
    
    args = parser.parse_args()
    
    # Set environment
    os.environ["APP_ENV"] = args.env
    
    # Run uvicorn server
    uvicorn.run(
        "src.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload or args.env == "dev",
        log_level="info" if args.env == "prod" else "debug"
    )
