from src.blog_logic import BlogArticle

def test_BlogArticle(obsidian_markdown: str) -> None:
    blog_article: BlogArticle = BlogArticle(obsidian_markdown, source_url="philnewm-github.io")
    assert blog_article.tags == ["tag01", "tag02", "tag03"]
    assert blog_article.title == "Title"
    assert blog_article.description == ""
    assert blog_article.content == "## First Header\n\nMain content section.\n"


def test_BlogArticle_missing_tags(obsidian_markdown_missing_tags: str) -> None:
    blog_article: BlogArticle = BlogArticle(obsidian_markdown_missing_tags, source_url="philnewm-github.io")
    assert blog_article.tags == [""]
    assert blog_article.title == "Title"
    assert blog_article.description == ""
    assert blog_article.content == "## First Header\n\nMain content section.\n"


def test_BlogArticle_content_only(obsidian_markdown_content_only: str) -> None:
    blog_article: BlogArticle = BlogArticle(obsidian_markdown_content_only, source_url="philnewm-github.io")
    assert blog_article.tags == [""]
    assert blog_article.title == None
    assert blog_article.description == ""
    assert blog_article.content == "## First Header\n\nMain content section.\n"
