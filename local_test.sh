articles_map='{"added": ["test_create_article.md"], "updated": ["test_update_article.md"], "removed": ["test_update_article.md"]}'
markdown_files_dir="tmp/"
gh_pages_repo="https://philnewm.github.io/"
key=""
publish=false

cat > tmp/test_create_article.md <<EOF
---
slug: test-update
---
# Smoke some test create article

## Introduction
This is a test markdown file for smoke testing article creations.

## Code Example
\`\`\`python
def hello():
    print("Hello, Markdown!")
\`\`\`

## Quote
> "Technology is best when it brings people together."

## List of Topics
- Bash Scripting
- Python Development
- DevOps
EOF

cat > tmp/test_update_article.md <<EOF
---
slug: test-update
---
# Smoke test a update article

## Introduction
This is a test markdown file for smoke testing article updates.

## Code Example
\`\`\`python
def hello():
    print("Hello, Updater!")
\`\`\`

## Quote
> "I was updated."
EOF

python3.11 main.py sync-blog "$articles_map" "$markdown_files_dir" "$gh_pages_repo" "$key" "$publish"
