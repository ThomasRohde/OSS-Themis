import os

from fastapi import APIRouter

from bcm.models import SettingsModel, TemplateSettings
from bcm.settings import Settings

# Create router instance with prefix and tags
router = APIRouter(
    prefix="/settings",
    tags=["settings"],
)

@router.get("", response_model=SettingsModel)
async def get_settings():
    """Get current application settings."""
    settings = Settings()
    
    # Get available templates from templates directory
    templates_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
    available_templates = [f for f in os.listdir(templates_dir) if f.endswith('.j2')]
    
    # Create template settings objects
    first_level_template = TemplateSettings(
        selected=settings.get("first_level_template"),
        available=available_templates
    )
    normal_template = TemplateSettings(
        selected=settings.get("normal_template"),
        available=available_templates
    )
    
    return SettingsModel(
        max_ai_capabilities=settings.get("max_ai_capabilities"),
        first_level_range=settings.get("first_level_range"),
        first_level_template=first_level_template,
        normal_template=normal_template,
        context_include_parents=settings.get("context_include_parents"),
        context_include_siblings=settings.get("context_include_siblings"),
        context_first_level=settings.get("context_first_level"),
        context_tree=settings.get("context_tree"),
        layout_algorithm=settings.get("layout_algorithm"),
        root_font_size=settings.get("root_font_size"),
        box_min_width=settings.get("box_min_width"),
        box_min_height=settings.get("box_min_height"),
        horizontal_gap=settings.get("horizontal_gap"),
        vertical_gap=settings.get("vertical_gap"),
        padding=settings.get("padding"),
        top_padding=settings.get("top_padding"),
        target_aspect_ratio=settings.get("target_aspect_ratio"),
        max_level=settings.get("max_level"),
        color_0=settings.get("color_0"),
        color_1=settings.get("color_1"),
        color_2=settings.get("color_2"),
        color_3=settings.get("color_3"),
        color_4=settings.get("color_4"),
        color_5=settings.get("color_5"),
        color_6=settings.get("color_6"),
        color_leaf=settings.get("color_leaf")
    )

@router.put("", response_model=SettingsModel)
async def update_settings(settings_update: SettingsModel):
    """Update application settings."""
    settings = Settings()
    
    # Update each setting
    settings.set("max_ai_capabilities", settings_update.max_ai_capabilities)
    settings.set("first_level_range", settings_update.first_level_range)
    settings.set("first_level_template", 
                settings_update.first_level_template.selected 
                if isinstance(settings_update.first_level_template, TemplateSettings) 
                else settings_update.first_level_template)
    settings.set("normal_template", 
                settings_update.normal_template.selected 
                if isinstance(settings_update.normal_template, TemplateSettings) 
                else settings_update.normal_template)
    settings.set("context_include_parents", settings_update.context_include_parents)
    settings.set("context_include_siblings", settings_update.context_include_siblings)
    settings.set("context_first_level", settings_update.context_first_level)
    settings.set("context_tree", settings_update.context_tree)
    settings.set("layout_algorithm", settings_update.layout_algorithm)
    settings.set("root_font_size", settings_update.root_font_size)
    settings.set("box_min_width", settings_update.box_min_width)
    settings.set("box_min_height", settings_update.box_min_height)
    settings.set("horizontal_gap", settings_update.horizontal_gap)
    settings.set("vertical_gap", settings_update.vertical_gap)
    settings.set("padding", settings_update.padding)
    settings.set("top_padding", settings_update.top_padding)
    settings.set("target_aspect_ratio", settings_update.target_aspect_ratio)
    settings.set("max_level", settings_update.max_level)
    settings.set("color_0", settings_update.color_0)
    settings.set("color_1", settings_update.color_1)
    settings.set("color_2", settings_update.color_2)
    settings.set("color_3", settings_update.color_3)
    settings.set("color_4", settings_update.color_4)
    settings.set("color_5", settings_update.color_5)
    settings.set("color_6", settings_update.color_6)
    settings.set("color_leaf", settings_update.color_leaf)
    
    return settings_update
