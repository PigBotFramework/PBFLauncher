import pathlib, os
def makeSurePathExists(pathToFile):
    pathlib.Path(pathToFile).mkdir(parents=True, exist_ok=True)

def path(pathToFile):
    return os.path.join(pathlib.Path().cwd(), pathToFile)