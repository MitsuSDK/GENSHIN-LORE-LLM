import requests
from fetch_character import build_character_schema, save_character_json


def fetch_playable_characters():
    """
    Fetch all playable characters from the wiki category using MediaWiki API.
    """
    url = "https://genshin-impact.fandom.com/api.php"
    params = {
        "action": "query",
        "format": "json",
        "list": "categorymembers",
        "cmtitle": "Category:Playable Characters",
        "cmlimit": "max"
    }

    response = requests.get(url, params=params)
    data = response.json()

    members = data.get("query", {}).get("categorymembers", [])

    # Extract only page titles (character names)
    characters = [member["title"] for member in members]

    return characters


def batch_generate(characters: list):
    print("Starting batch generation...\n")

    for name in characters:
        print(f"Processing: {name}")

        try:
            character_data = build_character_schema(name)
            save_character_json(character_data)
            print(f"✔ Successfully generated {name}\n")

        except Exception as e:
            print(f"✘ Failed for {name}")
            print(f"Error: {e}\n")

    print("Batch generation complete.")


if __name__ == "__main__":
    print("Fetching playable characters from API...\n")

    all_characters = fetch_playable_characters()

    # Remove reference character
    excluded = {"Albedo", "Columbina"}
    characters_to_generate = [c for c in all_characters if c not in excluded]

    print(f"Total playable characters found: {len(all_characters)}")
    print(f"Generating {len(characters_to_generate)} characters (excluding Albedo)\n")

    batch_generate(characters_to_generate)