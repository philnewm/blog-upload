import json
import requests
from typing import Optional
import yaml


class BlogArticle():
    def __init__(self, md_content: str) -> None:
        self.text: str = md_content
        self.tags: list[str] | None
        self.title: str | None
        self.content: str | None
        self.article_payload = None

        self.tags = self.get_md_tags()
        self.title = self.get_md_title()
        self.content = self.get_md_content()

    def get_md_tags(self) -> list[str]:
        if self.text.startswith("---"):
            parts: list[str] = self.text.split("---", 2)
            self.text: str = parts[2]
            return yaml.safe_load(parts[1]).get("tags", [])

        return []

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
        
    def upload_devto(self, api_key: str, canonical_url: str, description: str, published: bool= False) -> None:

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
                "canonical_url": canonical_url,
                "description": description,
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


def eval_response(response: requests.Response) -> None:
    # TODO change to logging
    if response.status_code == 201:
        print("Article published successfully!")
        print("Response:", response.json())
        return

    print(f"Failed to publish article. Status code: {response.status_code}")
    print("Response:", response.json())
