import logging
import zipfile

from pathlib import Path


logger = logging.getLogger('bandcamp_importer.importer')


class FilenameProcessingError(Exception):
    """
    Raise when we cannot process a zip file's filename to extract artist, album, and track info.
    """


def process_zip_filename(filename: str) -> tuple:
    try:
        artist, album = filename.split(" - ", 1)
    except ValueError:  # pragma: no cover
        raise FilenameProcessingError(f"Could not parse artist and album from {filename}.")
    album = album[:-4]
    logger.debug(f"{artist = }, {album = }")
    return artist, album


def import_zip_file(path: Path, media_root: Path) -> bool:
    imported = []

    try:
        artist, album = process_zip_filename(path.name)
    except FilenameProcessingError:  # pragma: no cover
        logger.error(f"Could not process zip filename {path}.")
        return imported

    target_path = media_root / artist / album
    if target_path.exists():
        logger.info(f"Skipping existing album in the media root: {target_path}")
        return False
    logger.debug(f"Extracting {path} to {str(target_path)}")
    with zipfile.ZipFile(path) as archive:
        archive.extractall(target_path)
    return True


def import_zip_files(zip_files: list, media_root: Path) -> list:
    files = []
    logger.debug(f"{zip_files = }")
    for path in zip_files:
        logger.debug(f"Importing {path}")
        if not zipfile.is_zipfile(path):
            logger.warning(f"{path} does not appear to be a .zip file; skipping.")
            continue
        if import_zip_file(path, media_root):
            files.append(path)
    return files


def import_from_directory(path: Path, media_root: Path) -> list:
    globbed = list(path.glob("*.zip"))
    logger.debug(f"Found {len(globbed)} zip files to import: {globbed = }")
    return import_zip_files(globbed, media_root)
