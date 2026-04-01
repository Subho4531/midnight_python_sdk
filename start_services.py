#!/usr/bin/env python3
"""
Start all Midnight services locally (without Docker)
"""

import subprocess
import sys
import time
from pathlib import Path

def start_service(name, script_path, port):
    """Start a service in the background"""
    print(f"Starting {name} on port {port}...")
    
    try:
        process = subprocess.Popen(
            [sys.executable, str(script_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a moment to see if it crashes
        time.sleep(2)
        
        if process.poll() is None:
            print(f"✓ {name} started (PID: {process.pid})")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"✗ {name} failed to start:")
            print(stderr)
            return None
    except Exception as e:
        print(f"✗ Error starting {name}: {e}")
        return None

def main():
    print("=" * 60)
    print("Starting Midnight Services")
    print("=" * 60)
    print()
    
    services = [
        ("Proof Server", Path("docker/proof/server.py"), 6300),
        ("Node Server", Path("docker/node/server.py"), 9944),
        ("Indexer Server", Path("docker/indexer/server.py"), 8088),
    ]
    
    processes = []
    
    for name, script, port in services:
        if not script.exists():
            print(f"✗ {name} script not found: {script}")
            continue
        
        proc = start_service(name, script, port)
        if proc:
            processes.append((name, proc))
    
    print()
    print("=" * 60)
    print(f"Started {len(processes)}/{len(services)} services")
    print("=" * 60)
    print()
    print("Services running:")
    for name, proc in processes:
        print(f"  • {name} (PID: {proc.pid})")
    
    print()
    print("Press Ctrl+C to stop all services")
    print()
    
    try:
        # Keep running
        while True:
            time.sleep(1)
            
            # Check if any process died
            for name, proc in processes:
                if proc.poll() is not None:
                    print(f"✗ {name} stopped unexpectedly")
    
    except KeyboardInterrupt:
        print("\n\nStopping services...")
        for name, proc in processes:
            proc.terminate()
            print(f"  Stopped {name}")
        
        print("\nAll services stopped.")

if __name__ == "__main__":
    main()
