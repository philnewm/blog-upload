from src import blog_logic


API_KEY = ""
gh_pages_url = "https://philnewm.github.io/molecule-start"

published_blogs: list[dict[str, str]] = blog_logic.get_articles(api_key=API_KEY)
id: int = int([published_blog["id"] for published_blog in published_blogs if published_blog["canonical_url"] == gh_pages_url][0])

print(id)