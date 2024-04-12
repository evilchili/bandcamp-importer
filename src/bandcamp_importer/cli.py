import io
import logging
import os
from pathlib import Path
from typing import Optional

import typer
from dotenv import load_dotenv
from rich.logging import RichHandler

from bandcamp_importer import importer

CONFIG_DEFAULTS = """
# Album Importer Defaults

# Where to store extracted media
MEDIA_ROOT=/music

# Where to look for downloaded zip files
DOWNLOADS=~/Downloads

LOG_LEVEL=INFO
"""

app = typer.Typer()
app_state = dict(
    config_file=Path("~/.config/bandcamp-importer.conf").expanduser(),
)

logger = logging.getLogger("bandcamp_importer.cli")


@app.callback(invoke_without_command=True)
def main(
    context: typer.Context,
    verbose: bool = typer.Option(False, help="Enable verbose output."),
    log_level: str = typer.Option("error", help=" Set the log level."),
    config_file: Optional[Path] = typer.Option(
        app_state["config_file"],
        help="Path to the bandcamp_importer configuration file",
    ),
    media_root: Optional[Path] = typer.Option(
        None,
        help="The root of your media folder. Defaults to /music, set by $MEDIA_ROOT."
    ),
    downloads: Optional[Path] = typer.Option(
        None,
        help="The path to your downloads folder."
    )
):
    """
    Extract album zip files downloaded from Bandcamp into your media root.
    """
    app_state["config_file"] = config_file
    load_dotenv(app_state["config_file"])
    load_dotenv(stream=io.StringIO(CONFIG_DEFAULTS))

    app_state['MEDIA_ROOT'] = (media_root or Path(os.environ['MEDIA_ROOT'])).expanduser().resolve()
    app_state['DOWNLOADS'] = (downloads or Path(os.environ['DOWNLOADS'])).expanduser().resolve()

    logging.basicConfig(
        format="%(message)s",
        level=getattr(logging, log_level.upper()),
        handlers=[RichHandler(rich_tracebacks=True, tracebacks_suppress=[typer])],
    )
    app_state["verbose"] = verbose

    logging.debug(f"{app_state = }")

    if context.invoked_subcommand is None:
        logger.debug("No command specified; invoking default handler.")
        import_album(context)


@app.command(context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def import_album(context: typer.Context):
    """
    The default command: Extract downloaded zip files into your media root.
    """
    file_list = [Path(arg) for arg in context.args]
    if file_list:
        paths = importer.import_zip_files(file_list, os.environ['DOWNLOADS'])
        logger.info(f"Imported {len(paths)}: " + "\n".join([str(p) for p in paths]))
        print(f"Imported {len(paths)} downloads.")
        return

    paths = importer.import_from_directory(app_state['DOWNLOADS'], app_state['MEDIA_ROOT'])
    logger.info(f"Imported {len(paths)} downloads from {app_state['DOWNLOADS']}: " + "\n".join([str(p) for p in paths]))
    print(f"Imported {len(paths)} downloads from {app_state['DOWNLOADS']}")
    return
