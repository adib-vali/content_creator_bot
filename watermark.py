#!/usr/bin/env python3
"""
Watermark module for adding business logo to images
"""

import os
import requests
import io
from PIL import Image, ImageEnhance
import logging

logger = logging.getLogger(__name__)

class WatermarkProcessor:
    def __init__(self, logo_path="logo.png"):
        """
        Initialize watermark processor with business logo
        
        Args:
            logo_path (str): Path to the business logo file
        """
        self.logo_path = logo_path
        self.logo = None
        self.load_logo()
    
    def load_logo(self):
        """Load and prepare the business logo"""
        try:
            if os.path.exists(self.logo_path):
                # Load logo and preserve original color space
                self.logo = Image.open(self.logo_path)
                
                # Convert to RGBA only if it's not already
                if self.logo.mode != 'RGBA':
                    self.logo = self.logo.convert("RGBA")
                
                logger.info(f"Logo loaded successfully: {self.logo_path} (mode: {self.logo.mode})")
            else:
                logger.error(f"Logo file not found: {self.logo_path}")
                self.logo = None
        except Exception as e:
            logger.error(f"Error loading logo: {e}")
            self.logo = None
    
    def download_image(self, image_url):
        """
        Download image from URL or load from local file
        
        Args:
            image_url (str): URL of the image to download or local file path
            
        Returns:
            PIL.Image: Downloaded image or None if failed
        """
        try:
            # Check if it's a local file
            if image_url.startswith('file://'):
                file_path = image_url[7:]  # Remove 'file://' prefix
                image = Image.open(file_path)
            elif os.path.exists(image_url):
                # Direct file path
                image = Image.open(image_url)
            else:
                # Download from URL
                response = requests.get(image_url, timeout=30)
                response.raise_for_status()
                
                image_data = io.BytesIO(response.content)
                image = Image.open(image_data)
            
            # Convert to RGB for better compatibility
            if image.mode in ('RGBA', 'LA', 'P'):
                # Create white background for transparent images
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            elif image.mode != 'RGB':
                image = image.convert('RGB')
            
            return image
        except Exception as e:
            logger.error(f"Error loading image: {e}")
            return None
    
    def calculate_watermark_size(self, base_image, watermark_ratio=0.3):
        """
        Calculate appropriate watermark size based on base image
        
        Args:
            base_image (PIL.Image): Base image to watermark
            watermark_ratio (float): Ratio of watermark size to image size
            
        Returns:
            tuple: (width, height) for watermark
        """
        base_width, base_height = base_image.size
        
        # Calculate watermark size (15% of the smaller dimension)
        min_dimension = min(base_width, base_height)
        watermark_size = int(min_dimension * watermark_ratio)
        
        # Maintain aspect ratio
        logo_width, logo_height = self.logo.size
        aspect_ratio = logo_width / logo_height
        
        if aspect_ratio > 1:  # Logo is wider than tall
            watermark_width = watermark_size
            watermark_height = int(watermark_size / aspect_ratio)
        else:  # Logo is taller than wide
            watermark_height = watermark_size
            watermark_width = int(watermark_size * aspect_ratio)
        
        return (watermark_width, watermark_height)
    
    def add_watermark(self, image_url, position="bottom-right", opacity=1.0):
        """
        Add watermark to image from URL
        
        Args:
            image_url (str): URL of the image to watermark
            position (str): Position of watermark ('bottom-right', 'bottom-left', 'top-right', 'top-left', 'center')
            opacity (float): Opacity of watermark (0.0 to 1.0)
            
        Returns:
            bytes: Watermarked image as bytes or None if failed
        """
        if self.logo is None:
            logger.error("Logo not loaded, cannot add watermark")
            return None
        
        try:
            # Download the image
            base_image = self.download_image(image_url)
            if base_image is None:
                return None
            
            # Resize logo to appropriate size
            watermark_size = self.calculate_watermark_size(base_image)
            watermark = self.logo.resize(watermark_size, Image.Resampling.LANCZOS)
            
            # Apply opacity while preserving colors
            if opacity < 1.0:
                # Create a new alpha channel with the desired opacity
                alpha = watermark.split()[-1]  # Get the alpha channel
                alpha = alpha.point(lambda x: int(x * opacity))
                watermark.putalpha(alpha)
            
            # Ensure watermark is in RGBA mode
            if watermark.mode != 'RGBA':
                watermark = watermark.convert('RGBA')
            
            # Calculate position
            base_width, base_height = base_image.size
            watermark_width, watermark_height = watermark.size
            
            if position == "bottom-right":
                x = base_width - watermark_width - 20
                y = base_height - watermark_height - 20
            elif position == "bottom-left":
                x = 20
                y = base_height - watermark_height - 20
            elif position == "top-right":
                x = base_width - watermark_width - 20
                y = 20
            elif position == "top-left":
                x = 20
                y = 20
            elif position == "center":
                x = (base_width - watermark_width) // 2
                y = base_height - watermark_height - 30
            else:
                # Default to bottom-right
                x = base_width - watermark_width - 20
                y = base_height - watermark_height - 20
            
            # Create a copy of the base image
            result_image = base_image.copy()
            
            # Convert base image to RGBA for watermarking
            if result_image.mode != 'RGBA':
                result_image = result_image.convert('RGBA')
            
            # Paste watermark
            result_image.paste(watermark, (x, y), watermark)
            
            # Convert back to RGB for JPEG compatibility
            background = Image.new('RGB', result_image.size, (255, 255, 255))
            background.paste(result_image, mask=result_image.split()[-1])  # Use alpha channel as mask
            result_image = background
            
            # Save to bytes
            output_buffer = io.BytesIO()
            result_image.save(output_buffer, format='JPEG', quality=95)
            output_buffer.seek(0)
            
            logger.info(f"Watermark added successfully to image")
            return output_buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Error adding watermark: {e}")
            return None
    
    def get_watermark_positions(self):
        """Get available watermark positions"""
        return [
            "bottom-right",
            "bottom-left", 
            "top-right",
            "top-left",
            "center"
        ] 