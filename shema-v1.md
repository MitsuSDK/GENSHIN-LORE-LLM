Character Schema v1

Required:
- name (string)
- entity_type (string)
- region (string)
- affiliation (string)
- status (string)
- gender (string)
- power_source (string | null)
- element (string | null)
- weapon (string | null)
- constellation (string | null)
- aliases (array)
- lore (object)

Lore contains:
- descriptions (array[string])
- character_stories (array[object])
- additional_lore (array[object])