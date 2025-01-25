import pytest

@pytest.fixture
def obsidian_markdown() -> str:
    return "---\ntags:\n  - tag01\n  - tag02\n  - tag03\n---\n# Title\n\n## First Header\n\nMain content section.\n"


@pytest.fixture
def obsidian_markdown_missing_tags() -> str:
    return "# Title\n\n## First Header\n\nMain content section.\n"


@pytest.fixture
def obsidian_markdown_content_only() -> str:
    return "## First Header\n\nMain content section.\n"
