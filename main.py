from fastapi import FastAPI, Query, HTTPException
from enum import Enum
import requests
import xmltodict

app = FastAPI()


class Source(str, Enum):
    APPLE = "apple",


@app.get("/podcast")
async def get_podcast(source: Source, id: int = Query(ge=0)):
    if source == Source.APPLE:
        api_endpoint = "https://itunes.apple.com/lookup"
        query_params = {"id": id}
        lookup_response = requests.get(api_endpoint, query_params)
        if lookup_response.status_code != 200:
            raise HTTPException(status_code=lookup_response.status_code, detail=lookup_response.content)

        lookup_data = lookup_response.json()
        results = lookup_data.get("results", [])
        if len(results) == 0:
            raise HTTPException(status_code=404, detail="Podcast not found")

        first_result = results[0]
        podcast_data = {
            "name": first_result.get("collectionCensoredName", ""),
            "author": first_result.get("artistName", ""),
            "genres": first_result.get("genres", []),
            "image": first_result.get("artworkUrl600", ""),
            "totalEpisodes": first_result.get("trackCount", 0),
            "releaseDate": first_result.get("releaseDate", ""),
        }

        rss_feed_url = first_result.get("feedUrl", "")
        if not rss_feed_url:
            podcast_data["isRssAvailable"] = False
        else:
            rss_response = requests.get(rss_feed_url)
            if rss_response.status_code != 200:
                podcast_data["isRssAvailable"] = False
            else:
                rss_data = xmltodict.parse(rss_response.text)
                if not rss_data:
                    podcast_data["isRssAvailable"] = False
                else:
                    podcast_data["isRssAvailable"] = True
                    podcast_data["summary"] = rss_data.get("rss", {}).get("channel", {}).get("description", "")
                    items = rss_data.get("rss", {}).get("channel", {}).get("item", [])
                    if isinstance(items, list):
                        last_episode_date = items[0].get("pubDate", "")
                    else:
                        last_episode_date = items.get("pubDate", "")
                    podcast_data["lastEpisodeReleaseDate"] = last_episode_date

        return podcast_data
