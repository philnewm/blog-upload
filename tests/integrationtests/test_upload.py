import os
import pytest
from pathlib import Path
import json
import shutil
import requests
from src.blog_logic import BlogArticle


def get_devto_api_key() -> str:
    """Retrieves the Dev.to API key from a local file or GitHub Actions secret."""

    key_path: Path = Path("~/.keys.json").expanduser()

    if key_path.exists():
        keys: dict[str, str] = json.loads(key_path.read_text())
        return keys.get("dev_to", "")

    return os.getenv("DEVTO_API_KEY", "")


@pytest.mark.parametrize("i", range(11))
def test_batch_article_creation(generated_markdown: str, i: int) -> None:

    devto_key: str = get_devto_api_key()
    assert devto_key, "Dev.to API key is missing!"

    published: bool = False
    blog_article = BlogArticle(md_content=Path(generated_markdown).read_text())
    response: requests.Response = blog_article.create_new_blog(api_key=devto_key, published=published)

    shutil.rmtree(Path(generated_markdown).parent)
    assert response.status_code == 201


def test_batch_article_update(generated_markdown_list: list[str]) -> None:

    devto_key: str = get_devto_api_key()
    assert devto_key, "Dev.to API key is missing!"
    published: bool = False

    blog_ids: list[str] = []

    for markdown_file_path in generated_markdown_list:
        blog_article = BlogArticle(md_content=Path(markdown_file_path).read_text())
        response: requests.Response = blog_article.create_new_blog(api_key=devto_key, published=published)
    
        assert response.status_code == 201
        blog_ids.append(json.loads(response.content)["id"])

    for blog_id, markdown_file_path in zip(blog_ids, generated_markdown_list):
        blog_article = BlogArticle(md_content=Path(markdown_file_path).read_text())
        blog_article.title = f"Updated - {blog_article.title}"
        update_response: requests.Response = blog_article.update_existing_blog(api_key=devto_key, id=blog_id, published=published)

        assert update_response.status_code == 200