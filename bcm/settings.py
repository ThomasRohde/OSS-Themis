import json
from pathlib import Path

BOX_MIN_WIDTH_DEFAULT = 120
BOX_MIN_HEIGHT_DEFAULT = 80
HORIZONTAL_GAP_DEFAULT = 20
VERTICAL_GAP_DEFAULT = 20
PADDING_DEFAULT = 30
TOP_PADDING_DEFAULT = 40  # Slightly larger than standard padding by default
DEFAULT_TARGET_ASPECT_RATIO_DEFAULT = 1.0

DEFAULT_SETTINGS = {
    # General settings
    "max_ai_capabilities": 10,  # Default max number of AI-generated capabilities
    "first_level_range": "5-10",  # Default range for first level capabilities
    "first_level_template": "first_level_prompt.j2",  # Default first level template
    "normal_template": "expansion_prompt.j2",  # Default normal template
    "font_size": 10,  # Default font size for main text content
    # Context settings
    "context_include_parents": True,  # Include parent nodes in context
    "context_include_siblings": True,  # Include sibling nodes in context
    "context_first_level": True,  # Include first level nodes in context
    "context_tree": True,  # Include full tree structure in context
    # Layout
    "layout_algorithm": "Simple - fast",  # Layout algorithm to use
    "root_font_size": 20,  # Default root font size for layout
    "box_min_width": BOX_MIN_WIDTH_DEFAULT,
    "box_min_height": BOX_MIN_HEIGHT_DEFAULT,
    "horizontal_gap": HORIZONTAL_GAP_DEFAULT,
    "vertical_gap": VERTICAL_GAP_DEFAULT,
    "padding": PADDING_DEFAULT,
    "top_padding": TOP_PADDING_DEFAULT,  # New setting for vertical padding between parent and first child
    "target_aspect_ratio": DEFAULT_TARGET_ASPECT_RATIO_DEFAULT,
    "max_level": 6,  # Add default max level
    # Color settings for hierarchy levels + leaf nodes
    "color_0": "#5B8C85",  # Muted teal
    "color_1": "#6B5B95",  # Muted purple
    "color_2": "#806D5B",  # Muted brown
    "color_3": "#5B7065",  # Muted sage
    "color_4": "#8B635C",  # Muted rust
    "color_5": "#707C8C",  # Muted steel blue
    "color_6": "#7C6D78",  # Muted mauve
    "color_leaf": "#E0E0E0",  # Light grey
}


class Settings:
    def __init__(self):
        self.settings_dir = Path.home() / ".pybcm"
        self.settings_file = self.settings_dir / "settings.json"
        self.settings = self._load_settings()

    def _load_settings(self):
        """Load settings from file or create with defaults if not exists."""
        try:
            self.settings_dir.mkdir(exist_ok=True)
            if self.settings_file.exists():
                with open(self.settings_file, "r") as f:
                    # Merge loaded settings with DEFAULT_SETTINGS
                    return {**DEFAULT_SETTINGS, **json.load(f)}
            return DEFAULT_SETTINGS.copy()
        except Exception as e:
            print(f"Error loading settings: {e}")
            return DEFAULT_SETTINGS.copy()

    def save_settings(self):
        """Save current settings to file."""
        try:
            with open(self.settings_file, "w") as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def get(self, key, default=None):
        """Get a setting value."""
        return self.settings.get(key, default)

    def set(self, key, value):
        """Set a setting value and save."""
        self.settings[key] = value
        self.save_settings()
