from enum import Enum
import json
import logging
import requests
import sys
from typing import Optional
import yaml

logger: logging.Logger = logging.getLogger(__name__)

class ReponseCodes(Enum):
    update_successful = 200
    created_successful = 201

class BlogArticle():
    def __init__(self, md_content: str, source_url: str) -> None:
        self.text: str = md_content
        self.tags: list[str] | None
        self.title: str | None
        self.article_payload = None

        self.tags = self.get_md_property("tags")
        self.description: str = self.get_md_property("description")[0]
        self.canonical_url: str = source_url
        self.title = self.get_md_title()
        self.content: str = self.get_md_body()

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

    def get_md_body(self) -> Optional[str]:
        self.text = self.text.lstrip("\n")
        if self.text.startswith("## "):
            return self.text.lstrip("\n")
        
        return ""

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

        eval_response(response, ReponseCodes.created_successful)

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

        logger.error(f"payload: {article_payload}")
        eval_response(response, ReponseCodes.update_successful)


def eval_response(response: requests.Response, type: ReponseCodes) -> None:
    if response.status_code == type.value:
        logger.info(f"Article {type.name}!")
        logger.debug("Response:", response.json())
        return

    logger.error(f"Failed to {type.name} article. Status code: {response.status_code}")
    logger.error(f"Response: {response.content}")
    sys.exit(1)


def unpublish_existing_blog(api_key: str, id: str) -> None:
        headers_dev: dict[str, str] = {
            "Content-Type": "application/json",
            "api-key": api_key,
        }

        article_payload: dict[str, dict[str, bool]] = {
            "article": {
                "published": False,
                "title": "[Deleted]",
            }
        }

        response: requests.Response = requests.put(
            url=f"https://dev.to/api/articles/{id}",
            headers=headers_dev,
            data=json.dumps(article_payload),
        )

        eval_response(response, ReponseCodes.update_successful)
