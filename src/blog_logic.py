import json
from pathlib import Path
import logging
import requests
from typing import Optional
import yaml

logger: logging.Logger = logging.getLogger(__name__)

class BlogArticle():
    def __init__(self, md_content: str, source_url: str) -> None:
        self.text: str = md_content
        self.tags: list[str] | None
        self.title: str | None
        self.content: str | None
        self.article_payload = None

        self.tags = self.get_md_property("tags")
        self.description: str = self.get_md_property("description")[0]
        self.canonical_url: str = source_url
        self.title = self.get_md_title()
        self.content = self.get_md_content()

    def get_md_property(self, property_name: str) -> list[str]:
        if self.text.startswith("---"):
            parts: list[str] = self.text.split("---", 2)
            self.text: str = parts[2]
            return yaml.safe_load(parts[1]).get(property_name, [""])

        return [""]

    def get_md_title(self) -> Optional[str]:
        self.text = self.text.lstrip("\n")
        if self.text.startswith("# "):
            parts: list[str] = self.text.split("\n", 1)
            self.text = parts[1]
            return parts[0].lstrip("# ")

    def get_md_content(self) -> Optional[str]:
        self.text = self.text.lstrip("\n")
        if self.text.startswith("## "):
            return self.text.lstrip("\n")

    def create_new_blog(self, api_key: str, published: bool= False) -> None:

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

        response: requests.Response = requests.post(
            url='https://dev.to/api/articles',
            headers=headers_dev,
            data=json.dumps(article_payload)
        )

        eval_response(response)

    def update_existing_blog(self, api_key: str, id: str, published: bool) -> None:
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

        response: requests.Response = requests.put(
            url=f"https://dev.to/api/articles/{id}",
            headers=headers_dev,
            data=json.dumps(article_payload),
        )

        eval_response(response)

def eval_response(response: requests.Response) -> None:
    if response.status_code == 201:
        logger.info("Article published successfully!")
        logger.debug("Response:", response.json())
        return

    logger.error(f"Failed to publish article. Status code: {response.status_code}")
    logger.error("Response:", response.json())


def unpublish_existing_blog(api_key: str, id: str) -> None:
        headers_dev: dict[str, str] = {
            "Content-Type": "application/json",
            "api-key": api_key,
        }

        article_payload: dict[str, dict[str, bool]] = {
            "article": {
                "published": False
            }
        }

        response: requests.Response = requests.put(
            url=f"https://dev.to/api/articles/{id}",
            headers=headers_dev,
            data=json.dumps(article_payload),
        )

        eval_response(response)
