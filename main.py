import logging
from pathlib import Path

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

app = FastAPI()
PROJECT_ROOT = Path(__file__).parent
STORAGE_PATH = PROJECT_ROOT.joinpath('storage')
STATIC_NAME = "static"
STATIC_ROUTE = "/static"

app.mount(STATIC_ROUTE, StaticFiles(directory=STORAGE_PATH), name=STATIC_NAME)
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

[Path.joinpath(Path(STATIC_ROUTE), item.name) for item in STORAGE_PATH.iterdir() if item.is_file()]


def get_storage_filenames(path: Path, base_path: Path):
    storage_filenames = []
    for file in path.iterdir():
        if file.is_file():
            storage_filenames.append(Path.joinpath(base_path, file.name))
        elif file.is_dir():
            storage_filenames.extend(get_storage_filenames(file, base_path.joinpath(file.name)))
    return storage_filenames


def get_storage_files_paths():
    return [str(filename).replace('\\', '/')
            for filename in get_storage_filenames(STORAGE_PATH, Path(STATIC_ROUTE))]


@app.post("/files/upload")
def upload(file: UploadFile = File(...)):
    try:
        with open(STORAGE_PATH.joinpath(file.filename), 'wb') as f:
            while contents := file.file.read(1024 * 1024):
                f.write(contents)
    except BaseException as e:
        logging.exception(e)
        return {"message": "There was an error uploading the file"}
    finally:
        file.file.close()

    return {"message": f"Successfully uploaded {file.filename}"}


@app.get("/files")
def get_all_files():
    try:
        return get_storage_files_paths()
    except BaseException as e:
        logging.exception(e)
        return []
