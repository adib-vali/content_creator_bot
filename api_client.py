import asyncio
import fal_client
from config import FAL_KEY, CONTENT_CREATOR_WORKFLOW, VISION_SPECIALIST_WORKFLOW

class FalAPIClient:
    def __init__(self):
        if FAL_KEY:
            # Set the API key for fal_client
            fal_client.key = FAL_KEY
        else:
            print("❌ FAL_KEY not found in environment variables!")
            print("Please set your Fal AI API key in the .env file")
    
    async def generate_product_image(self, image_url: str, shot_type: str, model: str = "sd15"):
        """
        Generate product image using the content creator workflow
        """
        try:
            stream = fal_client.stream_async(
                CONTENT_CREATOR_WORKFLOW,
                arguments={
                    "image_url": image_url,
                    "prompt": shot_type,
                    "reasoning": True,
                    "model": model
                },
            )
            
            result = None
            async for event in stream:
                if event.get("type") == "output":
                    result = event.get("output", {})
                    break
                elif event.get("type") == "error":
                    return None
            
            return result
        except Exception as e:
            print(f"Error generating product image: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def generate_text_content(self, image_url: str, prompt: str):
        """
        Generate text content using the vision specialist workflow
        """
        try:
            stream = fal_client.stream_async(
                VISION_SPECIALIST_WORKFLOW,
                arguments={
                    "image_url": image_url,
                    "prompt": prompt
                },
            )
            
            result = None
            async for event in stream:
                if event.get("type") == "output":
                    result = event.get("output", {})
                    break
                elif event.get("type") == "error":
                    return None
            
            return result
        except Exception as e:
            print(f"Error generating text content: {e}")
            import traceback
            traceback.print_exc()
            return None 