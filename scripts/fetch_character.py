import requests
import re
import json
import os

def fetch_character_page(title: str) -> str:
    url = "https://genshin-impact.fandom.com/api.php"

    params = {
        "action": "query",
        "titles": title,
        "prop": "revisions",
        "rvprop": "content",
        "rvslots": "main",
        "format": "json"
    }

    response = requests.get(url, params=params)
    data = response.json()

    pages = data["query"]["pages"]
    page = next(iter(pages.values()))

    return page["revisions"][0]["slots"]["main"]["*"]


def extract_infobox(content: str) -> dict:
    infobox_match = re.search(r"\{\{Character Infobox(.*?)\}\}", content, re.DOTALL)

    if not infobox_match:
        print("Infobox not found.")
        return {}

    infobox = infobox_match.group(1)

    fields = {}

    for line in infobox.split("\n"):
        if line.strip().startswith("|"):
            parts = line.split("=", 1)
            if len(parts) == 2:
                key = parts[0].replace("|", "").strip()
                value = parts[1].strip()
                value = re.sub(r"<.*?>", "", value)  # remove HTML tags
                fields[key] = value

    return fields


def extract_section(content: str, section_title: str) -> str:
    pattern = rf"=+\s*{re.escape(section_title)}\s*=+(.*?)(?=\n=+)"
    match = re.search(pattern, content, re.DOTALL)

    if match:
        section_text = match.group(1).strip()

        # Remove wiki links [[...]]
        section_text = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]+)\]\]", r"\1", section_text)

        # Remove templates {{...}}
        section_text = re.sub(r"\{\{.*?\}\}", "", section_text, flags=re.DOTALL)

        # Remove HTML tags
        section_text = re.sub(r"<.*?>", "", section_text)

        return section_text.strip()

    return ""


def build_character_schema(title: str) -> dict:
    content = fetch_character_page(title)
    fields = extract_infobox(content)

    # Build affiliations list (affiliation, affiliation2, affiliation3, etc.)
    affiliations = []
    for key, value in fields.items():
        if key.startswith("affiliation") and value:
            affiliations.append(value)

    # Extract character stories into array of objects
    character_stories = []
    for i in range(1, 6):
        story_text = extract_section(content, f"Character Story {i}")
        if story_text:
            character_stories.append({
                "title": f"Character Story {i}",
                "text": story_text
            })

    # Extract description
    description_text = extract_section(content, "Character Description")

    # Determine power source
    if fields.get("group") == "Gods":
        power_source = "Gnosis"
    elif fields.get("element"):
        power_source = "Vision"
    else:
        power_source = "Unknown"

    # Extract aliases from infobox titles
    aliases = []
    for key, value in fields.items():
        if key.startswith("title") and value:
            aliases.append(value)


    character_data = {
        "name": fields.get("name", title),
        "entity_type": "character",
        "status": "active",
        "region": fields.get("region", "Unknown"),
        "affiliations": affiliations,
        "power_source": power_source,
        "element": fields.get("element", "Unknown"),
        "constellation": fields.get("constellation", "Unknown"),
        "aliases": aliases,
        "lore": {
            "descriptions": [description_text] if description_text else [],
            "character_stories": character_stories,
            "additional_lore": []
        }
    }

    return character_data



def save_character_json(character_data: dict):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(base_dir, "lore-data", "characters")

    os.makedirs(output_dir, exist_ok=True)

    filename = os.path.join(
        output_dir,
        f"{character_data['name'].lower().replace(' ', '_')}.json"
    )

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(character_data, f, indent=4, ensure_ascii=False)

    print(f"Saved {filename}")


if __name__ == "__main__":
    character_name = "Venti"
    character_data = build_character_schema(character_name)
    save_character_json(character_data)