import json
import logging
import requests
import sys
import time
import yaml

from enum import Enum
from pathlib import Path


logger: logging.Logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class ReponseCodes(Enum):
    update_successful = 200
    created_successful = 201

class TimeOuts(Enum):
    # INFO create and update to 1 second prevents timeouts
    create = 1
    update = 1
    rate_limit = 30
    request = 0.2


class BlogArticle():
    def __init__(self, md_content: str, source_url: str="") -> None:
        self.text: str = md_content
        self.tags: list[str] | None
        self.article_payload = None

        self.tags = self.get_md_property("tags")
        self.description: str = self.get_md_property("description")[0]
        self.canonical_url: str = source_url
        self.title: str = self.get_md_title()
        self.content: str = self.get_md_body()

    def get_md_property(self, property_name: str) -> list[str]:
        if self.text.startswith("---"):
            parts: list[str] = self.text.split("---", 2)
            self.text: str = parts[2]
            return yaml.safe_load(parts[1]).get(property_name, [""])

        return [""]

    def get_md_title(self) -> str:
        self.text = self.text.lstrip("\n")
        if self.text.startswith("# "):
            parts: list[str] = self.text.split("\n", 1)
            self.text = parts[1]
            return parts[0].lstrip("# ")
        
        return ""

    def get_md_body(self) -> str:
        self.text = self.text.lstrip("\n")
        if self.text.startswith("## "):
            return self.text.lstrip("\n")
        
        return ""

    def create_new_blog(self, api_key: str, published: bool = False, retries: int = 3) -> requests.Response:

        headers_dev: dict[str, str] = {
            "Content-Type": "application/json",
            "api-key": api_key,
        }

        article_payload: dict[str, dict[str, str | bool | list[str] | None]] = {
            "article": {
                "title": self.title,
                "body_markdown": self.content,
                "published": published,
                "series": None,
                "main_image": None,
                "canonical_url": self.canonical_url or None,
                "description": self.description or None,
                "tags": self.tags,
                "organization_id": None,
            }
        }

        for _ in range(retries - 1):
            logger.info(f"Creating article '{self.title}' after {TimeOuts.create.value} seconds")
            time.sleep(TimeOuts.create.value)
            response: requests.Response = requests.post(
                url='https://dev.to/api/articles',
                headers=headers_dev,
                data=json.dumps(article_payload)
            )

            if response.status_code == ReponseCodes.created_successful.value:
                return response

            logger.warning(f"Got error {response.content}. Retrying in {TimeOuts.rate_limit.value} seconds...")
            time.sleep(TimeOuts.rate_limit.value)

        logger.error(f"Failed creating article '{self.title}' after {retries} retries. Status code: {response.status_code}")
        sys.exit(1)

    def update_existing_blog(self, api_key: str, id: str, published: bool, retries: int = 3) -> requests.Response:
        headers_dev: dict[str, str] = {
            "Content-Type": "application/json",
            "api-key": api_key,
        }

        article_payload: dict[str, dict[str, str | bool | list[str] | None]] = {
            "article": {
                "title": self.title,
                "body_markdown": self.content,
                "published": published, 
                "series": None,
                "main_image": None,
                "canonical_url": self.canonical_url,
                "description": self.description,
                "tags": self.tags,
                "organization_id": None,
            }
        }

        for _ in range(retries - 1):
            logger.info(f"Updating article '{self.title}' after {TimeOuts.update.value} seconds")
            time.sleep(TimeOuts.update.value)
            response: requests.Response = requests.put(
                url=f"https://dev.to/api/articles/{id}",
                headers=headers_dev,
                data=json.dumps(article_payload),
            )

            if response.status_code == ReponseCodes.update_successful.value:
                return response

            logger.warning(f"Got error {response.content}. Retrying in {TimeOuts.rate_limit.value} seconds...")
            time.sleep(TimeOuts.rate_limit.value)

        logger.error(f"Failed updating article '{self.title}' after {retries} retries. Status code: {response.status_code}")
        sys.exit(1)


def get_published_title(article_id: int) -> str:
    api_url: str = f"https://dev.to/api/articles/{article_id}"
    logger.info(f"Requesting published article title from id {article_id} after {TimeOuts.request.value} seconds")
    time.sleep(TimeOuts.request.value)
    response: requests.Response = requests.get(api_url)

    if response.status_code == 200:
        article = response.json()
        return article["title"]

    logger.error(f"Error: {response.status_code}, {response.text}")
    sys.exit(1)


def get_unpublished_title(api_key: str, article_id: int) -> str:
    api_url = "https://dev.to/api/articles/me/unpublished"
    headers: dict[str, str] = {"api-key": api_key}
    logger.info(f"Requesting unpublished article title from id {article_id} after {TimeOuts.request.value} seconds")
    time.sleep(TimeOuts.request.value)
    response: requests.Response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        articles = response.json()
        article = next((article for article in articles if article["id"] == article_id), None)

        if article:
            return article["title"]

        logger.error("Article not found.")
        sys.exit(1)

    logger.error(f"Error: {response.status_code}, {response.text}")
    sys.exit(1)


def unpublish_blog(api_key: str, id: str, title: str, retries: int = 3) -> requests.Response:

        headers_dev: dict[str, str] = {
            "Content-Type": "application/json",
            "api-key": api_key,
        }

        article_payload = {
            "article": {
                "published": False,
                "title": f"[Deleted] - {title}",
            }
        }

        for _ in range(retries - 1):
            logger.info(f"Updating article {title} after {TimeOuts.update.value} seconds")
            time.sleep(TimeOuts.update.value)
            response: requests.Response = requests.put(
                url=f"https://dev.to/api/articles/{id}",
                headers=headers_dev,
                data=json.dumps(article_payload),
            )

            if response.status_code == ReponseCodes.update_successful.value:
                return response

            logger.warning(f"Got error {response.content}. Retrying in {TimeOuts.rate_limit.value} seconds...")
            time.sleep(TimeOuts.rate_limit.value)

        logger.error(f"Failed unpublishin article '{title}' after {retries} retries. Status code: {response.status_code}")
        sys.exit(1)


def extract_front_matter(path: Path) -> dict[str, str]:
    """Get markdown file front-matter ijn yaml format.

    Args:
        path (Path):path to markdown file

    Returns:
        dict[str, str]: Extracted dictionary
    """

    lines: list[str] = path.read_text().splitlines()

    delimiter_indices: list[int] = [i for i, line in enumerate(lines) if line.strip() == "---"]

    if len(delimiter_indices) < 2:
        return {}

    start: int = 0
    end: int = 0
    start, end = delimiter_indices[0], delimiter_indices[1]
    front_matter_lines: list[str] = lines[start + 1:end]
    front_matter_text: str = "\n".join(front_matter_lines)

    return yaml.safe_load(front_matter_text) or {}


def get_articles(api_key: str, published: bool = True) -> list[dict[str, str]]:
    headers: dict[str, str] = {
        "api-key": api_key
    }
    api_enpoint: str = ["unpublished", "published"][published]

    response: requests.Response = requests.get(f"https://dev.to/api/articles/me/{api_enpoint}", headers=headers)

    if response.status_code == 200:
        return response.json()

    logger.error("Failed to fetch articles:", response.status_code)
    return [{"": ""}]