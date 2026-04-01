#!/usr/bin/env python3
"""
Start the Midnight Proof Server
"""

import sys
import subprocess
from pathlib import Path

def main():
    proof_server = Path("docker/proof/server.py")
    
    if not proof_server.exists():
        print("Error: docker/proof/server.py not found!")
        return 1
    
    print("Starting Midnight Proof Server on localhost:6300...")
    print("Press Ctrl+C to stop")
    print()
    
    try:
        subprocess.run([sys.executable, str(proof_server)])
    except KeyboardInterrupt:
        print("\nStopping proof server...")
        return 0

if __name__ == "__main__":
    sys.exit(main())
