#!/usr/bin/env python3
"""
Debug script to test Fal AI API connection
"""

import asyncio
import os
from dotenv import load_dotenv
from api_client import FalAPIClient

load_dotenv()

async def debug_api():
    """Debug the API connection"""
    
    print("🔍 Debugging Fal AI API Connection")
    print("=" * 50)
    
    # Check environment variables
    print(f"FAL_KEY present: {'Yes' if os.getenv('FAL_KEY') else 'No'}")
    if os.getenv('FAL_KEY'):
        print(f"FAL_KEY starts with: {os.getenv('FAL_KEY')[:10]}...")
    
    print(f"TELEGRAM_TOKEN present: {'Yes' if os.getenv('TELEGRAM_TOKEN') else 'No'}")
    
    # Test API client initialization
    print("\n📡 Testing API Client Initialization...")
    api_client = FalAPIClient()
    
    # Test with a sample image URL
    sample_image_url = "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500"
    
    print(f"\n🧪 Testing with sample image: {sample_image_url}")
    
    # Test text content generation first (simpler)
    print("\n1. Testing Text Content Generation...")
    try:
        result = await api_client.generate_text_content(
            image_url=sample_image_url,
            prompt="Generate a product description for this product"
        )
        print(f"Text generation result: {result}")
    except Exception as e:
        print(f"Text generation error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test product image generation
    print("\n2. Testing Product Image Generation...")
    try:
        result = await api_client.generate_product_image(
            image_url=sample_image_url,
            shot_type="generate The On-Model Portrait of this product"
        )
        print(f"Image generation result: {result}")
    except Exception as e:
        print(f"Image generation error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("🏁 Debug Complete")

if __name__ == "__main__":
    asyncio.run(debug_api()) 