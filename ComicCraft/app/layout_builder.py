def build_comic_layout(panels: list[dict]) -> list[dict]:
    required = {"panel_number", "title", "scene_description", "image_prompt", "image_path"}
    result = []
    for panel in sorted(panels, key=lambda p: p["panel_number"]):
        missing = required - set(panel)
        if missing:
            raise ValueError(f"Panel is missing fields: {', '.join(sorted(missing))}")
        result.append({
            "panel_number": panel["panel_number"],
            "title": panel["title"],
            "scene_description": panel["scene_description"],
            "image_prompt": panel["image_prompt"],
            "image_path": panel["image_path"],
            "caption": panel.get("caption", ""),
            "narration": panel.get("narration", ""),
            "dialogue": panel.get("dialogue", ""),
        })
    if len(result) != 5:
        raise ValueError("Comic layout must contain exactly 5 panels.")
    return result
