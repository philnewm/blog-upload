import json
from pathlib import Path
from src import blog_logic
import click


@click.group()
def cli() -> None:
    pass

@cli.command("create-devto-blog")
@click.argument("articles_map", type=click.STRING, required=True)
@click.argument("local_path", type=click.STRING, required=True)
@click.argument("source_url", type=click.STRING, required=True)
@click.argument("api_key", type=str, required=True)
@click.argument("published", type=bool, required=True, default=False)
def sync_blog(articles_map: str, local_path: str, source_url: str, api_key: str, published: bool) -> None:

    articles_id_map: dict[str, str] = json.loads(articles_map)
    for file_path, id in articles_id_map:
        if file_path and id:
            local_md_file_path: Path = Path(local_path, Path(file_path).name)
            blog_article = blog_logic.BlogArticle(local_md_file_path.read_text(), source_url)
            blog_article.update_existing_blog(api_key=api_key, id=id, published=published)
            continue

        if file_path and not id:
            local_md_file_path: Path = Path(local_path, Path(file_path).name)
            blog_article = blog_logic.BlogArticle(local_md_file_path.read_text(), source_url)
            blog_article.create_new_blog(api_key=api_key, published=published)
            continue

        if not file_path and id:
            blog_logic.unpublish_existing_blog(api_key=api_key, id=id)
            continue
