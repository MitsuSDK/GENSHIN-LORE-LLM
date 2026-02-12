Character Schema v1

Required:
- name (string)
- entity_type (string)
- status (string)
- region (string)
- affiliations (array[string])
- power_source (string)  # cannot be null
- element (string)       # cannot be null
- constellation (string) # cannot be null
- aliases (array[string])
- lore (object)

Lore contains:
- descriptions (array[string])
- character_stories (array[object])
- additional_lore (array[object])