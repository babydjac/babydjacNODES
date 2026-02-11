import torch
import base64
import io
import json
import requests
from PIL import Image
import numpy as np


class GrokFluxPromptOptimizer:
    CATEGORY = "babydjacNODES/Analyze"
    NODE_NAME = "GrokFluxPromptOptimizer"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("optimized_prompt",)
    FUNCTION = "optimize_prompt"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {}),
                "user_instruction": ("STRING", {
                    "default": "Make this image more vibrant and colorful",
                    "multiline": True,
                    "placeholder": "Describe what changes you want to make to the image..."
                }),
                "api_key": ("STRING", {
                    "default": "",
                    "placeholder": "Enter your Grok API key"
                }),
            },
            "optional": {
                "style_preference": (["photorealistic", "artistic", "cinematic", "portrait", "landscape", "abstract", "anime", "concept_art"], {
                    "default": "photorealistic"
                }),
                "detail_level": (["basic", "detailed", "very_detailed"], {
                    "default": "detailed"
                }),
            }
        }

    @classmethod
    def IS_CHANGED(cls, image, user_instruction, api_key, style_preference="photorealistic", detail_level="detailed"):
        return hash((user_instruction, api_key, style_preference, detail_level, str(image.shape) if hasattr(image, 'shape') else str(image)))

    def image_to_base64(self, image_tensor, max_pixels=1024*1024, quality=85):
        """Convert ComfyUI image tensor to base64 string for API with compression"""
        # Convert from [B,H,W,C] to PIL Image
        if len(image_tensor.shape) == 4:
            image_tensor = image_tensor[0]  # Take first image from batch
        
        # Convert from float [0,1] to uint8 [0,255]
        image_np = (image_tensor.cpu().numpy() * 255).astype(np.uint8)
        
        # Convert to PIL Image
        pil_image = Image.fromarray(image_np)
        
        # Downscale if too large (similar to grok_chat implementation)
        w, h = pil_image.size
        current_pixels = w * h
        if current_pixels > max_pixels:
            scale = (max_pixels / float(current_pixels)) ** 0.5
            new_w = max(1, int(w * scale))
            new_h = max(1, int(h * scale))
            pil_image = pil_image.resize((new_w, new_h), Image.LANCZOS)
        
        # Convert to base64 using JPEG for better compression
        buffer = io.BytesIO()
        pil_image.save(buffer, format="JPEG", quality=quality, optimize=True)
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return image_base64

    def call_grok_api(self, image_base64, user_instruction, api_key, style_preference, detail_level):
        """Call Grok API to analyze image and optimize prompt"""
        
        # Construct the system prompt for Grok
        system_prompt = f"""You are an expert AI image analysis and prompt optimization assistant. Your task is to:

1. Analyze the provided image in detail, identifying:
   - Main subjects and objects
   - Composition and layout
   - Colors, lighting, and mood
   - Style and artistic elements
   - Technical aspects (depth of field, perspective, etc.)

2. Understand the user's requested changes: "{user_instruction}"

3. Generate an optimized prompt for Flux Kontext that:
   - Preserves the successful elements of the original image
   - Implements the requested changes effectively
   - Uses specific, descriptive language suitable for AI image generation
   - Follows the {style_preference} style preference
   - Provides {detail_level} level of detail

4. IMPORTANT: Respond with ONLY the optimized prompt text. No JSON, no headers, no explanations, no additional text. Just the raw prompt that can be directly used with Flux Kontext.

Focus on creating a prompt that will generate high-quality results with Flux Kontext while maintaining the essence of what works in the original image."""

        user_prompt = f"""Please analyze this image and optimize the prompt based on the user's instruction: "{user_instruction}"

Style preference: {style_preference}
Detail level: {detail_level}

Remember: output ONLY the optimized prompt text, nothing else."""

        try:
            # xAI Grok API endpoint (use the working one from other nodes)
            url = "https://api.x.ai/v1/chat/completions"
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            # Try vision-specific payload first
            payload = {
                "model": "grok-2-vision-1212",
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": user_prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 1000,
                "temperature": 0.7
            }
            
            # Make the API call
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code != 200:
                # Fallback: try text-only analysis
                try:
                    fallback_prompt = f"""Based on the user instruction: "{user_instruction}"
                    
Style preference: {style_preference}
Detail level: {detail_level}

Generate an optimized prompt for Flux Kontext that implements the requested changes in the specified style and detail level."""

                    fallback_payload = {
                        "model": "grok-2-1212",
                        "messages": [
                            {"role": "system", "content": "You are an expert prompt optimizer for AI image generation models, specifically Flux Kontext."},
                            {"role": "user", "content": fallback_prompt}
                        ],
                        "max_tokens": 1000,
                        "temperature": 0.7
                    }
                    
                    fallback_response = requests.post(url, headers=headers, json=fallback_payload, timeout=30)
                    if fallback_response.status_code == 200:
                        result = fallback_response.json()
                        return f"[Text-only mode] {result['choices'][0]['message']['content']}"
                except:
                    pass
                
                return f"API Error: {response.status_code} - {response.text}. Please check your API key and try again."
            
            response.raise_for_status()
            
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            # Return the content directly (should be just the prompt now)
            return content.strip()
                
        except requests.exceptions.RequestException as e:
            return f"API Error: {str(e)}"
        except Exception as e:
            return f"Error processing request: {str(e)}"

    def optimize_prompt(self, image, user_instruction, api_key, style_preference="photorealistic", detail_level="detailed"):
        """Main function to optimize the prompt"""
        
        if not api_key or api_key.strip() == "":
            return ("Error: Please provide a valid Grok API key",)
        
        if not user_instruction or user_instruction.strip() == "":
            return ("Error: Please provide user instructions for the optimization",)
        
        try:
            # Convert image to base64
            image_base64 = self.image_to_base64(image)
            
            # Call Grok API
            optimized_prompt = self.call_grok_api(
                image_base64, 
                user_instruction, 
                api_key, 
                style_preference, 
                detail_level
            )
            
            return (optimized_prompt,)
            
        except Exception as e:
            return (f"Error: {str(e)}",)

NODE_CLASS_MAPPINGS = {
    "GrokFluxPromptOptimizer": GrokFluxPromptOptimizer,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "GrokFluxPromptOptimizer": "Grok Flux Prompt Optimizer",
}
