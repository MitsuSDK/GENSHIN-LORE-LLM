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
    infobox_match = re.search(r"\{\{Character Infobox(.*?)\n\}\}", content, re.DOTALL)

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
    pattern = rf"(?ms)^=+\s*{re.escape(section_title)}\s*=+\s*(.*?)(?=^=+\s*[^=]|\Z)"
    match = re.search(pattern, content)

    if not match:
        return ""

    section_text = match.group(1)

    # Remove external links [http...]
    section_text = re.sub(r"\[https?://[^\]]+\]", "", section_text)

    # Remove wiki links but keep visible text
    section_text = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]+)\]\]", r"\1", section_text)

    # Replace templates {{...}} but keep their inner content
    section_text = re.sub(r"\{\{([^{}]*?)\}\}", r"\1", section_text)

    # Remove HTML tags
    section_text = re.sub(r"<.*?>", "", section_text)

    # Remove reference markers like [1], [2]
    section_text = re.sub(r"\[\d+\]", "", section_text)

    return section_text.strip()


def extract_official_introduction(content: str) -> dict:
    intro_pattern = r"=+\s*Official Introduction\s*=+(.*?)(?=\n=+[^=])"
    match = re.search(intro_pattern, content, re.DOTALL)

    if not match:
        return {}

    section_text = match.group(1)

    # 1️⃣ Extract subtitle from template
    subtitle = ""
    template_match = re.search(r"\{\{Official Introduction(.*?)\}\}", section_text, re.DOTALL)
    if template_match:
        template_block = template_match.group(1)
        title_match = re.search(r"\|\s*title\s*=\s*(.+)", template_block)
        if title_match:
            subtitle = title_match.group(1).strip()

    # 2️⃣ Clean full section text for body
    # First remove the Official Introduction template specifically
    cleaned_text = re.sub(r"\{\{Official Introduction.*?\}\}", "", section_text, flags=re.DOTALL)

    # Then remove remaining templates like {{Quote|...}}
    cleaned_text = re.sub(r"\{\{.*?\}\}", "", cleaned_text, flags=re.DOTALL)

    cleaned_text = re.sub(r"<.*?>", "", cleaned_text)
    cleaned_text = re.sub(r"\[https?://[^\]]+\]", "", cleaned_text)
    cleaned_text = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]+)\]\]", r"\1", cleaned_text)
    cleaned_text = re.sub(r"\[\d+\]", "", cleaned_text)
    # Remove stray words ending with .facebook (e.g., flowers.Facebook)
    cleaned_text = re.sub(r"\b\S+\.facebook\b", "", cleaned_text, flags=re.IGNORECASE)

    lines = [line.strip() for line in cleaned_text.split("\n") if line.strip()]
    text = "\n".join(lines).strip()

    return {
        "title": "Official Introduction",
        "subtitle": subtitle,
        "text": text
    }


def build_character_schema(title: str) -> dict:
    # Fetch main page (for infobox)
    main_content = fetch_character_page(title)
    fields = extract_infobox(main_content)

    # Fetch Profile subpage (for descriptions & stories)
    profile_content = fetch_character_page(f"{title}/Profile")

    # Fetch Voice-Overs subpage (for additional lore like Hello, About..., etc.)
    voice_content = fetch_character_page(f"{title}/Voice-Overs")

    # Build affiliations list (affiliation, affiliation2, affiliation3, etc.)
    affiliations = []
    for key, value in fields.items():
        if key.startswith("affiliation") and value:
            affiliations.append(value)

    # Extract Official Introduction
    official_intro = extract_official_introduction(profile_content)

    character_stories = []

    # Insert Official Introduction first if exists
    if official_intro:
        character_stories.append(official_intro)

    # Extract Character Stories template block
    template_match = re.search(r"\{\{Character Story(.*?)\n\}\}", profile_content, re.DOTALL)

    if template_match:
        template_block = template_match.group(1)

        # Extract titleX and textX pairs
        titles = re.findall(r"\|title\d+\s*=\s*(.*)", template_block)
        texts = re.findall(
            r"\|text\d+\s*=\s*(.*?)(?=\n\|title|\n\|mention|\Z)",
            template_block,
            re.DOTALL
        )

        for title_value, text_value in zip(titles, texts):
            clean_text = re.sub(r"<.*?>", "", text_value)
            clean_text = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]+)\]\]", r"\1", clean_text)
            clean_text = clean_text.replace("&mdash;", "—").strip()

            character_stories.append({
                "title": title_value.strip(),
                "text": clean_text
            })

    # Extract description blocks (quotes BEFORE Official Introduction section)
    description_blocks = []

    # Find where Official Introduction starts
    intro_heading = re.search(r"=+\s*Official Introduction\s*=+", profile_content)

    if intro_heading:
        description_section = profile_content[:intro_heading.start()]
    else:
        description_section = profile_content

    # Extract all {{Quote|text|...}} templates from that top section
    quote_matches = re.findall(r"\{\{Quote\|(.*?)(?:\|.*?)?\}\}", description_section, re.DOTALL)

    for quote in quote_matches:
        clean_quote = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]+)\]\]", r"\1", quote)
        clean_quote = re.sub(r"<.*?>", "", clean_quote)
        clean_quote = clean_quote.strip()

        if clean_quote:
            description_blocks.append(clean_quote)

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

    # Extract additional lore from Voice-Overs page (template-based parsing)
    additional_lore = []

    voice_entries = re.findall(
        r"\|vo_(\d+_\d+)_title\s*=\s*(.*?)\n.*?\|vo_\1_tx\s*=\s*(.*?)(?=\n\|vo_|\Z)",
        voice_content,
        re.DOTALL
    )

    for _, title_value, text_value in voice_entries:

        # Clean title
        title_clean = title_value.strip()

        # Remove wiki links in titles: [[Diona]] -> Diona
        title_clean = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]+)\]\]", r"\1", title_clean)

        # Replace {name} with actual character name (e.g., Venti)
        title_clean = title_clean.replace("{name}", title)

        clean_text = re.sub(r"<.*?>", "", text_value)
        clean_text = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]+)\]\]", r"\1", clean_text)
        clean_text = clean_text.replace("&mdash;", "—").strip()

        if (
            title_clean == "Hello"
            or "About" in title_clean
            or title_clean == "Something to Share"
            or title_clean == "Interesting Things"
        ):
            additional_lore.append({
                "title": title_clean,
                "text": clean_text
            })

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
            "descriptions": description_blocks,
            "character_stories": character_stories,
            "additional_lore": additional_lore
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