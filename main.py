import click
import json
import logging

from pathlib import Path
from src import blog_logic

logger = logging.Logger(__file__)

@click.group()
def cli() -> None:
    pass

@cli.command("sync-blog")
@click.argument("articles_map", type=click.STRING, required=True)
@click.argument("local_path", type=click.STRING, required=True)
@click.argument("source_url", type=click.STRING, required=True)
@click.argument("api_key", type=click.STRING, required=True)
@click.argument("published", type=click.STRING, required=True, default=False)
def sync_blog(articles_map: str, local_path: str, source_url: str, api_key: str, published: str) -> None:

    articles_id_map: dict[str, list[str]] = json.loads(articles_map)

    added_paths: list[str] = articles_id_map["added"]
    updated_paths: list[str] = articles_id_map["updated"]
    removed_paths: list[str] = articles_id_map["removed"]

    published_convert: bool = True if published.lower() == "true" else False

    if added_paths and added_paths[0]:
        for file_path in added_paths:
            logger.info(f"Creating new article {file_path}")

            file_path: str = Path(file_path).name
            gh_pages_url: str = f"{source_url.rstrip('/')}/{file_path.strip('.md')}"
            slug: str = blog_logic.extract_front_matter(Path(local_path, file_path)).get("slug", "")

            if slug:
                gh_pages_url = f"{source_url.rstrip('/')}/{slug}"

            local_md_file_path: Path = Path(local_path, Path(file_path).name)
            blog_article = blog_logic.BlogArticle(local_md_file_path.read_text(), gh_pages_url)
            blog_article.create_new_blog(api_key=api_key, published=published_convert)

    if updated_paths and updated_paths[0]:
        for file_path in updated_paths:
            logger.info(f"Updating existing article {file_path}")

            file_path: str = Path(file_path).name
            gh_pages_url: str = f"{source_url.rstrip('/')}/{file_path.strip('.md')}"
            slug: str = blog_logic.extract_front_matter(Path(local_path, file_path)).get("slug", "")

            if slug:
                gh_pages_url = f"{source_url.rstrip('/')}/{slug}"

            published_blogs: list[dict[str, str]] = blog_logic.get_articles(api_key=api_key, published=published_convert)
            id: str = [published_blog["id"] for published_blog in published_blogs if published_blog["canonical_url"] == gh_pages_url][0]

            local_md_file_path: Path = Path(local_path, Path(file_path).name)
            blog_article = blog_logic.BlogArticle(local_md_file_path.read_text(), gh_pages_url)
            blog_article.update_existing_blog(api_key=api_key, id=id, published=published_convert)

    if removed_paths and removed_paths[0]:
        for file_path in removed_paths:
            logger.info(f"Unpublishing article {file_path}")

            file_path: str = Path(file_path).name
            gh_pages_url: str = f"{source_url.rstrip('/')}/{file_path.strip('.md')}"
            slug: str = blog_logic.extract_front_matter(Path(local_path, file_path)).get("slug", "")

            if slug:
                gh_pages_url = f"{source_url.rstrip('/')}/{slug}"

            published_blogs: list[dict[str, str]] = blog_logic.get_articles(api_key=api_key, published=published_convert)
            id: str = [published_blog["id"] for published_blog in published_blogs if published_blog["canonical_url"] == gh_pages_url][0]

            title: str = (
                blog_logic.get_unpublished_title(api_key=api_key, article_id=int(id))
                if not published_convert
                else blog_logic.get_published_title(article_id=int(id))
            )
            blog_logic.unpublish_blog(api_key=api_key, id=id, title=title)


if __name__ == "__main__":
    cli()