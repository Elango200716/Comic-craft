from app.layout_builder import build_comic_layout

def test_layout_requires_five_panels():
    panels = [{
        "panel_number": i,
        "title": f"Panel {i}",
        "scene_description": "Scene",
        "image_prompt": "Prompt",
        "image_path": f"/static/panels/{i}.png",
    } for i in range(1, 6)]
    result = build_comic_layout(panels)
    assert len(result) == 5
    assert result[0]["panel_number"] == 1
