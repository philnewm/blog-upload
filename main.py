from src import blog_logic
import click


@click.group()
def cli() -> None:
    pass

@cli.command("create-devto-blog")
@click.argument("md_file", type=click.Path(exists=True))
@click.argument("api_key", type=str, required=True)
@click.argument("canonical_url", type=str, required=True)
@click.argument("description", type=str, required=True)
@click.argument("published", type=bool, default=False)
def create_blog(
    md_content: str,
    api_key: str,
    canonical_url: str,
    description: str,
    published: bool
    ) -> None:
    blog_article = blog_logic.BlogArticle(md_content)
    blog_article.upload_devto(
        api_key=api_key,
        canonical_url=canonical_url,
        description=description,
        published=published,
        )
