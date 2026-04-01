"""
Compact ABI Codegen — reads .compact files and generates Python classes.

This is the feature that doesn't exist in ANY other blockchain's Python SDK.
Instead of manually writing contract call wrappers, developers point this at
their .compact file and get a fully-typed Python class back.
"""

import re
import subprocess
import json
from pathlib import Path
from typing import Any
from .exceptions import CompactParseError


def compile_compact(contract_path: str, output_dir: str | None = None) -> Path:
    """
    Compile a .compact contract using the Compact compiler.
    
    This requires the Compact compiler to be installed:
        npm install -g @midnight-ntwrk/compact-compiler
    
    On Windows, this will try to use WSL/Ubuntu if available.
    
    Args:
        contract_path: Path to the .compact file
        output_dir: Output directory (defaults to contracts/managed/<contract_name>)
    
    Returns:
        Path to the compiled contract directory
    
    Raises:
        CompactParseError: If compilation fails
    """
    import platform
    import os
    
    contract_path = Path(contract_path)
    
    if not contract_path.exists():
        raise CompactParseError(f"Contract file not found: {contract_path}")
    
    # Default output directory
    if output_dir is None:
        output_dir = Path("contracts/managed") / contract_path.stem
    else:
        output_dir = Path(output_dir)
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Determine if we're on Windows and should use WSL
    is_windows = platform.system() == "Windows"
    use_wsl = False
    compact_cmd = "compact"
    
    if is_windows:
        # Check if compactc is available in WSL
        try:
            result = subprocess.run(
                ["wsl", "which", "compactc"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                use_wsl = True
                compact_cmd = "compactc"
                print("Using compactc from WSL/Ubuntu...")
            else:
                # Try compact in WSL
                result = subprocess.run(
                    ["wsl", "which", "compact"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    use_wsl = True
                    compact_cmd = "compact"
                    print("Using compact from WSL/Ubuntu...")
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
    
    # Check if compiler is available
    if use_wsl:
        check_cmd = ["wsl", compact_cmd, "--version"]
    else:
        check_cmd = [compact_cmd, "--version"]
    
    try:
        result = subprocess.run(
            check_cmd,
            capture_output=True,
            text=True,
            timeout=5
        )
        # Just check if command succeeded (compactc returns version number only)
        if result.returncode != 0:
            raise CompactParseError(
                "Compact compiler not found!\n\n"
                "Install it with:\n"
                "  npm install -g @midnight-ntwrk/compact-compiler\n\n"
                "On Windows, install in WSL/Ubuntu:\n"
                "  wsl\n"
                "  npm install -g @midnight-ntwrk/compact-compiler\n\n"
                "Then run:\n"
                f"  {compact_cmd} compile {contract_path} {output_dir}"
            )
        print(f"Found {compact_cmd} version: {result.stdout.strip()}")
    except FileNotFoundError:
        raise CompactParseError(
            "Compact compiler not found!\n\n"
            "Install it with:\n"
            "  npm install -g @midnight-ntwrk/compact-compiler\n\n"
            "On Windows, install in WSL/Ubuntu:\n"
            "  wsl\n"
            "  npm install -g @midnight-ntwrk/compact-compiler\n\n"
            "Then run:\n"
            f"  {compact_cmd} compile {contract_path} {output_dir}"
        )
    
    # Prepare paths for compilation
    if use_wsl:
        # Convert Windows paths to WSL paths
        # C:\Users\... -> /mnt/c/Users/...
        def win_to_wsl_path(win_path):
            p = str(win_path).replace("\\", "/")
            # Handle absolute paths like C:/Users/...
            if len(p) > 1 and p[1] == ":":
                drive = p[0].lower()
                return f"/mnt/{drive}{p[2:]}"
            # Handle relative paths
            return p
        
        contract_wsl = win_to_wsl_path(contract_path.absolute())
        output_wsl = win_to_wsl_path(output_dir.absolute())
        
        # compactc doesn't use "compile" subcommand
        compile_cmd = ["wsl", compact_cmd, contract_wsl, output_wsl]
    else:
        # Regular compact uses "compile" subcommand
        if compact_cmd == "compactc":
            compile_cmd = [compact_cmd, str(contract_path), str(output_dir)]
        else:
            compile_cmd = [compact_cmd, "compile", str(contract_path), str(output_dir)]
    
    # Compile the contract
    print(f"Compiling {contract_path} to {output_dir}...")
    print(f"Command: {' '.join(compile_cmd)}")
    
    try:
        result = subprocess.run(
            compile_cmd,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode != 0:
            raise CompactParseError(
                f"Compilation failed:\n{result.stderr}\n{result.stdout}\n\n"
                f"Command: {' '.join(compile_cmd)}"
            )
        
        print(f"[OK] Compiled successfully to {output_dir}")
        print(f"Output:\n{result.stdout}")
        
        # Verify output files exist
        contract_js = output_dir / "contract" / "index.cjs"
        if not contract_js.exists():
            # Try .js extension
            contract_js = output_dir / "contract" / "index.js"
            if not contract_js.exists():
                raise CompactParseError(
                    f"Compilation succeeded but output file not found.\n"
                    f"Expected: {output_dir / 'contract' / 'index.js'}\n"
                    f"Output directory contents:\n{list(output_dir.rglob('*'))}"
                )
        
        return output_dir
        
    except subprocess.TimeoutExpired:
        raise CompactParseError("Compilation timed out (>120s)")
    except Exception as e:
        raise CompactParseError(f"Compilation error: {e}")


def parse_compact_circuits(contract_path: str) -> list[str]:
    """Extract all exported circuit names from a .compact file."""
    source = Path(contract_path).read_text()
    circuits = re.findall(r'export\s+circuit\s+(\w+)\s*\(', source)
    if not circuits:
        raise CompactParseError(
            f"No exported circuits found in {contract_path}. "
            "Make sure your circuits use 'export circuit name()' syntax."
        )
    return circuits


def compact_to_python(contract_path: str) -> type:
    """
    Read a .compact contract file and generate a Python class.
    
    Each exported circuit becomes a Python method.
    
    Example:
        .compact file has:  export circuit post(message: Bytes)
        Generated class has: .post(message=b"hello")
    
    Usage:
        BulletinBoard = compact_to_python("contracts/bulletin_board.compact")
        board = BulletinBoard(contract_instance)
        board.post(message=b"hello midnight!")
    """
    source = Path(contract_path).read_text()

    # Parse circuits with their parameters
    circuit_pattern = re.compile(
        r'export\s+circuit\s+(\w+)\s*\((.*?)\)',
        re.DOTALL
    )
    circuits = circuit_pattern.findall(source)

    if not circuits:
        raise CompactParseError(f"No exported circuits in {contract_path}")

    # Parse ledger state fields
    ledger_pattern = re.compile(r'ledger\s*\{([^}]+)\}', re.DOTALL)
    ledger_match = ledger_pattern.search(source)
    ledger_fields = []
    if ledger_match:
        field_pattern = re.compile(r'(\w+)\s*:\s*(\w+)')
        ledger_fields = field_pattern.findall(ledger_match.group(1))

    # Build dynamic class methods
    methods = {}

    for circuit_name, params_str in circuits:
        param_names = [
            p.strip().split(":")[0].strip()
            for p in params_str.split(",")
            if p.strip()
        ]

        def make_circuit_method(name: str, pnames: list[str]):
            def method(self, private_inputs: dict | None = None, **kwargs):
                """Auto-generated from .compact circuit definition."""
                public_inputs = {k: v for k, v in kwargs.items() if k in pnames}
                return self._contract.call(
                    circuit_name=name,
                    private_inputs=private_inputs or {},
                    public_inputs=public_inputs,
                )
            method.__name__ = name
            method.__doc__ = (
                f"Call the '{name}' circuit.\n"
                f"Public params: {pnames}\n"
                f"Use private_inputs={{}} for secret data."
            )
            return method

        methods[circuit_name] = make_circuit_method(circuit_name, param_names)

    # Add state() method
    def state_method(self):
        """Read current on-chain ledger state."""
        return self._contract.state()
    methods["state"] = state_method

    # Add __init__
    def init_method(self, contract):
        self._contract = contract
        self._ledger_fields = ledger_fields
    methods["__init__"] = init_method

    # Create and return the class
    contract_name = Path(contract_path).stem.replace("_", " ").title().replace(" ", "")
    generated_class = type(contract_name, (), methods)
    generated_class.__doc__ = f"Auto-generated from {contract_path}"
    return generated_class
