import requests

api_url = "https://dev.to/api/articles/me/unpublished"
headers: dict[str, str] = {"api-key": "<key>"}

# Make the request
response = requests.get(api_url, headers=headers)

# Check if the request was successful
if response.status_code == 200:
    articles = response.json()  # Parse JSON response

    # Find the article with ID 2179805
    article = next((a for a in articles if a["id"] == 2179805), None)

    # Print the title if found
    if article:
        print("Title:", article["title"])
    else:
        print("Article not found.")

else:
    print(f"Error: {response.status_code}, {response.text}")
