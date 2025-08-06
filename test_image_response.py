#!/usr/bin/env python3
"""
Test script to debug image generation response
"""

import asyncio
import os
from dotenv import load_dotenv
from api_client import FalAPIClient

load_dotenv()

async def test_image_response():
    """Test image generation and see the exact response format"""
    
    if not os.getenv('FAL_KEY'):
        print("❌ FAL_KEY not found in environment variables")
        return
    
    api_client = FalAPIClient()
    
    # Sample image URL
    sample_image_url = "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500"
    
    print("🧪 Testing Image Generation Response...")
    print("=" * 60)
    
    try:
        result = await api_client.generate_product_image(
            image_url=sample_image_url,
            shot_type="generate The On-Model Portrait of this product with a male model"
        )
        
        print(f"Raw API Result: {result}")
        print(f"Result type: {type(result)}")
        
        if result:
            print(f"Result keys: {list(result.keys())}")
            
            if "images" in result:
                print(f"Images: {result['images']}")
                if len(result['images']) > 0:
                    print(f"First image: {result['images'][0]}")
                    print(f"Image URL: {result['images'][0].get('url')}")
                else:
                    print("No images in result")
            else:
                print("No 'images' key in result")
        else:
            print("No result returned")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("=" * 60)
    print("🏁 Test Complete")

if __name__ == "__main__":
    asyncio.run(test_image_response()) 