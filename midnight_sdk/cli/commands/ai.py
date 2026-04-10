"""AI inference commands."""

import typer
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import numpy as np

from ...client import MidnightClient
from ...config import ConfigManager

app = typer.Typer(help="AI model training and inference")
console = Console()


@app.command("train")
def ai_train(
    data: Path = typer.Argument(..., help="Training data file (CSV/JSON)"),
    model_name: str = typer.Option("model", "--name", "-n", help="Model name"),
    profile: str = typer.Option(None, "--profile", "-p", help="Network profile"),
):
    """Train AI model."""
    if not data.exists():
        console.print(f"[red]File not found: {data}[/red]")
        raise typer.Exit(1)
    
    config_mgr = ConfigManager()
    config_mgr.load()
    profile_obj = config_mgr.get_profile(profile)
    
    try:
        with console.status("[cyan]Training model..."):
            client = MidnightClient(network=profile_obj.name)
            
            # Load data
            if data.suffix == ".csv":
                import pandas as pd
                df = pd.read_csv(data)
                X = df.iloc[:, :-1].values
                y = df.iloc[:, -1].values
            else:
                data_dict = json.loads(data.read_text())
                X = np.array(data_dict["features"])
                y = np.array(data_dict["labels"])
            
            # Train model
            client.ai.train(X, y)
            
            # Save model
            model_dir = Path.home() / ".midnight" / "models"
            model_dir.mkdir(parents=True, exist_ok=True)
            model_path = model_dir / f"{model_name}.joblib"
            
            import joblib
            joblib.dump(client.ai.model, model_path)
        
        console.print(f"[green]✓[/green] Model trained and saved to {model_path}")
    except Exception as e:
        console.print(f"[red]Training failed: {e}[/red]")
        raise typer.Exit(1)


@app.command("infer")
def ai_infer(
    features: str = typer.Argument(..., help="JSON feature array"),
    model_name: str = typer.Option("model", "--model", "-m", help="Model name"),
    sign: bool = typer.Option(False, "--sign", help="Submit as transaction"),
    wallet: str = typer.Option(None, "--wallet", "-w", help="Wallet name"),
    profile: str = typer.Option(None, "--profile", "-p", help="Network profile"),
):
    """Run AI inference."""
    try:
        features_array = json.loads(features)
    except json.JSONDecodeError:
        console.print("[red]Invalid JSON features[/red]")
        raise typer.Exit(1)
    
    config_mgr = ConfigManager()
    config_mgr.load()
    profile_obj = config_mgr.get_profile(profile)
    
    # Load model
    model_dir = Path.home() / ".midnight" / "models"
    model_path = model_dir / f"{model_name}.joblib"
    
    if not model_path.exists():
        console.print(f"[red]Model '{model_name}' not found[/red]")
        raise typer.Exit(1)
    
    try:
        import joblib
        model = joblib.load(model_path)
        
        client = MidnightClient(network=profile_obj.name)
        client.ai.model = model
        
        if sign:
            # Submit as transaction
            if not wallet:
                wallet = config_mgr.config.default_wallet
            if not wallet:
                console.print("[red]No wallet specified[/red]")
                raise typer.Exit(1)
            
            wallet_path = Path(config_mgr.config.wallets[wallet])
            mnemonic = wallet_path.read_text().strip()
            
            with console.status("[cyan]Running inference with transaction..."):
                result = client.ai.infer_with_tx(features_array, mnemonic)
            
            console.print(f"[green]✓[/green] Inference completed")
            console.print(f"[cyan]Prediction:[/cyan] {result['prediction']}")
            console.print(f"[cyan]TX Hash:[/cyan] {result['tx_hash']}")
        else:
            # Local inference only
            prediction = client.ai.infer(features_array)
            console.print(f"[cyan]Prediction:[/cyan] {prediction}")
    except Exception as e:
        console.print(f"[red]Inference failed: {e}[/red]")
        raise typer.Exit(1)


@app.command("model-list")
def ai_model_list():
    """List trained models."""
    model_dir = Path.home() / ".midnight" / "models"
    
    if not model_dir.exists():
        console.print("[yellow]No models found[/yellow]")
        return
    
    models = list(model_dir.glob("*.joblib"))
    
    if not models:
        console.print("[yellow]No models found[/yellow]")
        return
    
    table = Table(title="Trained Models")
    table.add_column("Name", style="cyan")
    table.add_column("Path", style="dim")
    table.add_column("Size", style="yellow", justify="right")
    
    for model_path in models:
        name = model_path.stem
        size = model_path.stat().st_size
        size_str = f"{size / 1024:.1f} KB" if size < 1024 * 1024 else f"{size / (1024 * 1024):.1f} MB"
        table.add_row(name, str(model_path), size_str)
    
    console.print(table)


@app.command("model-info")
def ai_model_info(name: str = typer.Argument(..., help="Model name")):
    """Show model details."""
    model_dir = Path.home() / ".midnight" / "models"
    model_path = model_dir / f"{name}.joblib"
    
    if not model_path.exists():
        console.print(f"[red]Model '{name}' not found[/red]")
        raise typer.Exit(1)
    
    try:
        import joblib
        model = joblib.load(model_path)
        
        console.print(f"[cyan]Model:[/cyan] {name}")
        console.print(f"[cyan]Type:[/cyan] {type(model).__name__}")
        console.print(f"[cyan]Path:[/cyan] {model_path}")
        
        if hasattr(model, "n_features_in_"):
            console.print(f"[cyan]Features:[/cyan] {model.n_features_in_}")
        if hasattr(model, "classes_"):
            console.print(f"[cyan]Classes:[/cyan] {model.classes_}")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
