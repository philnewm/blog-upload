articles_map='{"ansible/molecule_getting_started/ansible_molecule_using_vagrant_and_virtualbox.md": "", "ansible/some_actions/ci_in_github_actions.md": "", "": 2180598}'
markdown_files_dir="tmp/"
gh_pages_repo="https://philnewm.github.io/"
key=""
publish=false

python3.11 main.py sync-blog "$articles_map" "$markdown_files_dir" "$gh_pages_repo" "$key" "$publish"
