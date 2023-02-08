from fastapi import FastAPI, Query
from enum import Enum

app = FastAPI()


class Source(str, Enum):
    APPLE = "apple",


@app.get("/podcasts/")
async def get_podcast(source: Source, id: int = Query(ge=0)):
    return {"source": source, "id": id}
