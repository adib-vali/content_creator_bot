#!/usr/bin/env python3
"""
Test script for the Fal AI API integration
"""

import asyncio
import os
from dotenv import load_dotenv
from api_client import FalAPIClient

load_dotenv()

async def test_api_integration():
    """Test the API integration with sample data"""
    
    # Check if API key is set
    if not os.getenv('FAL_KEY'):
        print("❌ FAL_KEY not found in environment variables")
        print("Please set your Fal AI API key in the .env file")
        return
    
    api_client = FalAPIClient()
    
    # Sample image URL (you can replace with a real product image URL)
    sample_image_url = "https://example.com/sample-product.jpg"
    
    print("🧪 Testing API Integration...")
    print("=" * 50)
    
    # Test product image generation
    print("\n1. Testing Product Image Generation...")
    try:
        result = await api_client.generate_product_image(
            image_url=sample_image_url,
            shot_type="generate The On-Model Portrait of this product"
        )
        if result:
            print("✅ Product image generation API call successful")
            print(f"Result keys: {list(result.keys())}")
        else:
            print("❌ Product image generation returned no result")
    except Exception as e:
        print(f"❌ Product image generation failed: {e}")
    
    # Test text content generation
    print("\n2. Testing Text Content Generation...")
    try:
        result = await api_client.generate_text_content(
            image_url=sample_image_url,
            prompt="Generate Product Description content for this product. User request: Create a compelling product description"
        )
        if result:
            print("✅ Text content generation API call successful")
            print(f"Result keys: {list(result.keys())}")
        else:
            print("❌ Text content generation returned no result")
    except Exception as e:
        print(f"❌ Text content generation failed: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 API Integration Test Complete")

if __name__ == "__main__":
    asyncio.run(test_api_integration()) 