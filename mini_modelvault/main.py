"""
mini-modelvault Main Entry Point

This module provides the command-line and HTTP server interfaces for the mini-modelvault application.
It uses Typer for CLI management and Uvicorn for serving the HTTP API. The user can select between CLI and HTTP server modes.
Logging is set up at startup, and all major actions are logged for observability.
"""
import typer
import uvicorn
import sys
import os
from typing import Optional
from .logger import setup_logger
import subprocess
from rich.console import Console
from .utils.model_check import check_and_pull_models

console = Console()

app = typer.Typer(add_completion=False, help="""
mini-modelvault: Run LLMs, vision, and more — all on your own hardware, with full privacy and control.

Available Modes:
  CLI: Run inference or start an interactive session from the command line.\n
    - Use --text/-t to provide a text query.\n
    - Use --image/-i to provide an image file for vision models.\n
    - If neither is provided, an interactive session is started.\n
    - In interactive session, to provide an image, use the format: <image>[image_path]<image>\n
  HTTP server: Start a FastAPI server exposing endpoints for inference and health checks.\n
    - POST /generate: Run inference (text and/or image, with optional streaming).\n
      - To enable streaming output, use the query parameter: stream=true\n
    - GET /health: Get health status.\n
    - GET /status: Get device resource usage and health status.\n

Use -h or --help with any command to see more details.\n
""")

run_app = typer.Typer(help="Run mini-modelvault in different modes.")

logger = setup_logger(os.getenv('LOG_DIR', './logs'), 'main')

@app.callback(invoke_without_command=True)
def main_callback(ctx: typer.Context, help: bool = typer.Option(False, '--help', '-h', is_eager=True, help='Show this message and exit.')):
    if help or ctx.invoked_subcommand is None:
        print_rich_help()
        raise typer.Exit()

def print_rich_help():
    console.print("\n[bold magenta]" + "="*60 + "[/bold magenta]")
    console.print("[bold cyan]🌟 Welcome to mini-modelvault! 🌟[/bold cyan]")
    console.print("[bold magenta]" + "="*60 + "[/bold magenta]\n")
    console.print("[green]Run LLMs, vision, and more — all on your own hardware, with full privacy and control.[/green]\n")
    console.print("[yellow bold]Available Modes:[/yellow bold]")
    console.print("[green]  CLI: Run inference or start an interactive session from the command line.[/green]")
    console.print("[green]    - Use --text/-t to provide a text query.[/green]")
    console.print("[green]    - Use --image/-i to provide an image file for vision models.[/green]")
    console.print("[green]    - If neither is provided, an interactive session is started.[/green]")
    console.print("[green]    - In interactive session, to provide an image, use the format: <image>[image_path]<image>[/green]")
    console.print("[blue]  HTTP server: Start a FastAPI server exposing endpoints for inference and health checks.[/blue]")
    console.print("[blue]    - POST /generate: Run inference (text and/or image, with optional streaming).[/blue]")
    console.print("[blue]      - To enable streaming output, use the query parameter: stream=true[/blue]")
    console.print("[blue]    - GET /health: Get health status.[/blue]")
    console.print("[blue]    - GET /status: Get device resource usage and health status.[/blue]\n")
    console.print("[cyan]Use -h or --help with any command to see more details.[/cyan]")
    console.print("[bold magenta]" + "="*60 + "[/bold magenta]\n")

@app.command()
def cli(
    input_text: Optional[str] = typer.Option(None, '--text', '-t', help="Text query to process"),
    input_image: Optional[str] = typer.Option(None, '--image', '-i', help="Path to the input image (optional)")
):
    """
    Run CLI mode for mini-modelvault.

    Parameters:
        input_text (Optional[str]): Text query to process. If provided, will be passed to the CLI module.
        input_image (Optional[str]): Path to the input image. If provided, will be passed to the CLI module.

    This function initializes the CLI mode, sets up arguments, and delegates execution to the CLI module.
    """
    logger.info("CLI mode selected.")
    typer.echo("💬 Initializing CLI mode...")
    from mini_modelvault.services import cli as cli_module
    sys.argv = [sys.argv[0]]
    if input_text:
        sys.argv.extend(['--text', input_text])
    if input_image:
        sys.argv.extend(['--image', input_image])
    try:
        typer.run(cli_module.main)
    except Exception as e:
        logger.error(f"CLI execution failed: {e}")
        raise

@app.command()
def http():
    """
    Run HTTP server mode for mini-modelvault.

    This function starts the HTTP server using Uvicorn, serving the FastAPI app defined in src/services/http_server.py.
    The server listens on http://127.0.0.1:8000 and reloads on code changes.
    """
    logger.info("HTTP server mode selected.")
    typer.echo("🚀 Starting HTTP server at http://127.0.0.1:8000 ...")
    try:
        uvicorn.run("mini_modelvault.services.http_server:app", host="127.0.0.1", port=8000, reload=True)
    except Exception as e:
        logger.error(f"HTTP server failed to start: {e}")
        raise

@run_app.command()
def cli(
    input_text: Optional[str] = typer.Option(None, '--text', '-t', help="Text query to process"),
    input_image: Optional[str] = typer.Option(None, '--image', '-i', help="Path to the input image (optional)")
):
    """
    Run CLI mode for mini-modelvault. (run subcommand)
    """
    logger.info("CLI mode selected (run subcommand).")
    typer.echo("💬 Initializing CLI mode...")
    from mini_modelvault.services import cli as cli_module
    sys.argv = [sys.argv[0]]
    if input_text:
        sys.argv.extend(['--text', input_text])
    if input_image:
        sys.argv.extend(['--image', input_image])
    try:
        typer.run(cli_module.main)
    except Exception as e:
        logger.error(f"CLI execution failed: {e}")
        raise

@run_app.command()
def http():
    """
    Run HTTP server mode for mini-modelvault. (run subcommand)
    """
    logger.info("HTTP server mode selected (run subcommand).")
    typer.echo("🚀 Starting HTTP server at http://127.0.0.1:8000 ...")
    try:
        uvicorn.run("mini_modelvault.services.http_server:app", host="127.0.0.1", port=8000, reload=True)
    except Exception as e:
        logger.error(f"HTTP server failed to start: {e}")
        raise

app.add_typer(run_app, name="run")

def main():
    check_and_pull_models()
    typer.echo(r"""
  __  __  _         _          __  __             _        _ __      __            _  _   
 |  \/  |(_)       (_)        |  \/  |           | |      | |\ \    / /           | || |  
 | \  / | _  _ __   _  ______ | \  / |  ___    __| |  ___ | | \ \  / /__ _  _   _ | || |_ 
 | |\/| || || '_ \ | ||______|| |\/| | / _ \  / _` | / _ \| |  \ \/ // _` || | | || || __|
 | |  | || || | | || |        | |  | || (_) || (_| ||  __/| |   \  /| (_| || |_| || || |_ 
 |_|  |_||_||_| |_||_|        |_|  |_| \___/  \__,_| \___||_|    \/  \__,_| \__,_||_| \__|

""")
    logger.info("mini-modelvault application started.")
    if len(sys.argv) == 1:
        typer.secho("Please select a mode to run mini-modelvault:", fg=typer.colors.CYAN, bold=True)
        typer.secho("  [1] CLI", fg=typer.colors.GREEN)
        typer.secho("  [2] HTTP server", fg=typer.colors.BLUE)
        typer.secho("  [3] Help", fg=typer.colors.MAGENTA)
        typer.secho("  [4] Exit", fg=typer.colors.RED)
        choice = typer.prompt(
            typer.style("Enter 1 for CLI, 2 for HTTP server, 3 for Help, or 4 for Exit", fg=typer.colors.YELLOW, bold=True),
            type=str
        )
        choice = choice.strip()
        if choice == "1":
            logger.info("User selected CLI mode.")
            sys.argv.append("cli")
        elif choice == "2":
            logger.info("User selected HTTP server mode.")
            sys.argv.append("http")
        elif choice == "3":
            logger.info("User requested help.")
            print_rich_help()
            sys.exit(0)
        elif choice == "4":
            logger.info("User selected Exit.")
            typer.secho("👋 Exiting mini-modelvault. Goodbye!", fg=typer.colors.RED, bold=True)
            sys.exit(0)
        else:
            logger.error("Invalid mode selection. Exiting.")
            typer.secho("❌ Invalid selection. Exiting.", fg=typer.colors.RED, bold=True)
            sys.exit(1)
    app()

if __name__ == "__main__":
    main() 