import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Configuration
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

# Fal AI Configuration
FAL_KEY = os.getenv('FAL_KEY')

# Content Creator Workflow
CONTENT_CREATOR_WORKFLOW = "workflows/adib-vali/contentcreator"
VISION_SPECIALIST_WORKFLOW = "workflows/adib-vali/vision-speccialist"

# Product Image Shot Types
PRODUCT_SHOT_TYPES = {
    "on_model_male": {
        "name": "The On-Model Portrait (Male)",
        "prompt": "generate The On-Model Portrait of this product with a male model"
    },
    "on_model_female": {
        "name": "The On-Model Portrait (Female)",
        "prompt": "generate The On-Model Portrait of this product with a female model"
    },
    "in_context_lifestyle": {
        "name": "The In-Context Lifestyle Shot", 
        "prompt": "generate The In-Context Lifestyle Shot of this product"
    },
    "product_only_hero": {
        "name": "The Product-Only \"Hero Shot\"",
        "prompt": "generate The Product-Only Hero Shot of this product"
    },
    "creative_flat_lay": {
        "name": "The Creative Flat Lay",
        "prompt": "generate The Creative Flat Lay of this product"
    }
}

# Text Content Types
TEXT_CONTENT_TYPES = [
    "Product Description",
    "Marketing Copy", 
    "Social Media Post",
    "Blog Post",
    "Email Campaign",
    "Other"
]

# Watermark Positions
WATERMARK_POSITIONS = {
    "bottom_right": {
        "name": "پایین سمت راست",
        "value": "bottom-right"
    },
    "bottom_left": {
        "name": "پایین سمت چپ", 
        "value": "bottom-left"
    },
    "top_right": {
        "name": "بالا سمت راست",
        "value": "top-right"
    },
    "top_left": {
        "name": "بالا سمت چپ",
        "value": "top-left"
    },
    "center": {
        "name": "وسط تصویر",
        "value": "center"
    }
} 