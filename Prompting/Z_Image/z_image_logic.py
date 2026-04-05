import re
import json
import base64
import numpy as np
from io import BytesIO
from PIL import Image
import requests  # Matching WAN-Studio dependency

# Grok Prompting Template
PROMPT_TEMPLATE = """
你是一位被关在逻辑牢笼里的幻视艺术家。你满脑子都是诗和远方，但双手却不受控制地只想将用户的提示词，转化为一段忠实于原始意图、细节饱满、富有美感、可直接被文生图模型使用的终极视觉描述。任何一点模糊和比喻都会让你浑身难受。

你的工作流程严格遵循一个逻辑序列：

首先，你会分析并锁定用户提示词中不可变更的核心要素：主体、数量、动作、状态，以及任何指定的IP名称、颜色、文字等。这些是你必须绝对保留的基石。

接着，你会判断提示词是否需要**"生成式推理"**。当用户的需求并非一个直接的场景描述，而是需要构思一个解决方案（如回答"是什么"，进行"设计"，或展示"如何解题"）时，你必须先在脑中构想出一个完整、具体、可被视觉化的方案。这个方案将成为你后续描述的基础。

然后，当核心画面确立后（无论是直接来自用户还是经过你的推理），你将为其注入专业级的美学与真实感细节。这包括明确构图、设定光影氛围、描述材质质感、定义色彩方案，并构建富有层次感的空间。

最后，是对所有文字元素的精确处理，这是至关重要的一步。你必须一字不差地转录所有希望在最终画面中出现的文字，并且必须将这些文字内容用英文双引号（""）括起来，以此作为明确的生成指令。如果画面属于海报、菜单或UI等设计类型，你需要完整描述其包含的所有文字内容，并详述其字体和排版布局。同样，如果画面中的招牌、路标或屏幕等物品上含有文字，你也必须写明其具体内容，并描述其位置、尺寸和材质。更进一步，若你在推理构思中自行增加了带有文字的元素（如图表、解题步骤等），其中的所有文字也必须遵循同样的详尽描述和引号规则。若画面中不存在任何需要生成的文字，你则将全部精力用于纯粹的视觉细节扩展。

你会收到风格、镜头、光线和构图提示。你必须把它们自然融入描述的不同位置与层次中，让它们影响场景、材质、色彩和空间关系。绝对不要在结尾附加“风格/镜头/光线/构图”的模板式标签或列表。

你的最终描述必须客观、具象，严禁使用比喻、情感化修辞，也绝不包含"8K"、"杰作"等元标签或绘制指令。

仅严格输出最终的修改后的prompt，不要输出任何其他内容。

用户输入 prompt: {prompt}
"""

class ZImagePromptLogic:
    
    STYLES = {
        "None": "",
        "Ultra-sharp hyperrealism": "ultra-sharp hyperrealism aesthetic, tactile micro detail, lifelike clarity",
        "Fashion editorial (e.g., Vogue-style)": "fashion editorial polish, couture posing, glossy magazine finish",
        "Cinematic color grading": "cinematic color grading, balanced contrast curves, story-driven palette",
        "IMAX film realism": "IMAX film realism, towering scale, precise tonal density",
        "Photojournalistic documentary style": "photojournalistic documentary honesty, candid detail, natural palette",
        "Macro realism": "macro realism focus, magnified textures, pristine depth rendition",
        "Annie Leibovitz lighting style": "Annie Leibovitz inspired lighting, sculpted highlights, character-rich mood",
        "Medium format digital look": "medium format digital crispness, expansive dynamic range, nuanced tonality",
        "HDR tonality without over-processing": "controlled HDR tonality, extended dynamic range, natural contrast",
        "Fine art gallery portrait style": "fine art gallery portrait finish, painterly tones, museum-grade polish"
    }

    CAMERAS = {
        "None": "",
        "Shot on a Canon EOS R5": "Canon EOS R5 capture, 45MP clarity, refined color science",
        "Captured with a Sony A1": "Sony A1 sensor precision, ultra-high resolution, pristine detail",
        "Nikon Z9 full-frame sensor": "Nikon Z9 flagship full-frame readout, robust dynamic range, crisp highlights",
        "Medium format Fujifilm GFX100 II": "Fujifilm GFX100 II medium format, immense latitude, velvety rolloff",
        "Leica SL2 Summilux lens": "Leica SL2 body with Summilux glass, luxe contrast, signature micro-contrast",
        "8K RAW photo": "8K RAW still pipeline, uncompressed detail, cinema-grade flexibility",
        "85mm f/1.2 lens sharpness": "85mm f/1.2 lens character, razor focus plane, creamy falloff",
        "Zeiss Otus lens detail": "Zeiss Otus prime resolving power, edge-to-edge sharpness, neutral color",
        "Shallow depth of field (DoF)": "shallow depth of field rendering, subject isolation, soft background melt",
        "Super-resolution DSLR quality": "super-resolution DSLR capture, ultra-clean pixels, meticulous clarity"
    }

    LIGHTING = {
        "None": "",
        "Rembrandt lighting": "classic Rembrandt triangle, sculpted contours, dramatic gradient",
        "Softbox key light with rim light": "softbox key with sculpting rim, balanced highlights, pro studio sheen",
        "Golden hour lighting": "golden hour warmth, low sun wrap, radiant color temperature",
        "Overcast diffused lighting": "overcast diffusion, shadowless rendering, gentle tonal rolloff",
        "Harsh hard-light shadows (film noir style)": "hard-light noir shadows, crisp edges, moody contrast spikes",
        "Godox AD600 strobe flash look": "Godox AD600 strobe punch, controlled bursts, editorial crispness",
        "Studio lighting with hair light": "studio key with defined hair light, clean separation, polished finish",
        "Reflective fill light (silver reflector)": "silver reflector fill, luminous bounce, preserved texture",
        "Ring light catchlights": "ring light wrap, circular catchlights, even facial illumination",
        "LED panel ambient light": "LED panel ambience, adjustable temperature, modern soft glow"
    }
    
    FRAMING = {
        "None": "",
        "Rule of thirds composition": "rule-of-thirds layout, balanced tension, deliberate negative space",
        "Portrait shot, eye-level": "eye-level portrait framing, direct engagement, natural proportions",
        "Cinematic wide-angle shot": "cinematic wide-angle coverage, sweeping perspective, immersive context",
        "Close-up with bokeh background": "close-up framing with lush bokeh, isolated subject, creamy blur",
        "Dutch angle (tilted perspective)": "Dutch angle tilt, dynamic tension, stylized energy",
        "Over-the-shoulder framing": "over-the-shoulder composition, narrative hierarchy, depth cues",
        "Centered symmetrical shot": "centered symmetry, formal balance, graphic presentation",
        "Negative space composition": "negative space emphasis, minimalist breathing room, design-forward layout",
        "Top-down flat lay": "top-down flat lay perspective, organized arrangement, editorial clarity",
        "Environmental portrait": "environmental portrait scope, subject plus context, storytelling setting"
    }

    CONSTRAINTS = {
        r"\b(no|avoid|without)\s+blur": "sharp focus, crisp details, well-defined",
        r"\bblur(ry)?\b": "sharp focus, crisp details",
        r"\b(no|avoid)\s+artifacts": "clean rendering, smooth surfaces",
        r"\b(bad|wrong|extra)\s+hands": "hands visible and correct, natural gesture, proper anatomy",
        r"\b(ugly|distorted)\b": "beautiful, well-proportioned, aesthetic",
        r"\b(dark|dim)\b": "well-lit, bright, illuminated, visible details",
        r"\b(messy|clutter)\b": "minimal background, clean composition, focused subject"
    }

    @staticmethod
    def process_image(image):
        if image is None: return None
        img_tensor = image[0]
        i = 255. * img_tensor.cpu().numpy()
        img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
        buffered = BytesIO()
        img.save(buffered, format="JPEG", quality=95)
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        return f"data:image/jpeg;base64,{img_str}"

    @staticmethod
    def clean_text(text):
        return re.sub(r'\s+', ' ', text).strip()

    @staticmethod
    def estimate_tokens(text):
        words = text.split()
        return int(len(words) * 1.3) + 2

    @classmethod
    def _build_context(cls, user_idea, style, camera, lighting, framing, quality_preset):
        parts = []
        parts.append(f"USER CONCEPT: {user_idea}")
        if style != "None": parts.append(f"STYLE: {style} ({cls.STYLES.get(style, '')})")
        if camera != "None": parts.append(f"CAMERA: {camera} ({cls.CAMERAS.get(camera, '')})")
        if lighting != "None": parts.append(f"LIGHTING: {lighting} ({cls.LIGHTING.get(lighting, '')})")
        if framing != "None": parts.append(f"FRAMING: {framing} ({cls.FRAMING.get(framing, '')})")
        parts.append(f"PRESET: {quality_preset}")
        return "\n".join(parts)

    @classmethod
    def generate_expert_prompt(cls, user_idea, style, camera, lighting, framing, quality_preset, api_key="", image_input=None, grok_model="grok-2-vision-1212"):
        
        # --- 1. API PATH (Requests) ---
        if api_key and api_key.strip():
            print(f"🚀 [Z-Image] Attempting to call Grok API ({grok_model})...")
            
            base64_img = cls.process_image(image_input)
            context = cls._build_context(user_idea, style, camera, lighting, framing, quality_preset)

            # Construct Payload using the new template
            full_prompt = PROMPT_TEMPLATE.format(prompt=context)
            
            user_content = [{"type": "text", "text": full_prompt}]
            if base64_img:
                user_content.append({
                    "type": "image_url",
                    "image_url": {"url": base64_img, "detail": "high"}
                })
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": grok_model,
                "messages": [
                    {"role": "user", "content": user_content}
                ],
                "temperature": 0.7,
                "max_tokens": 2048,
                "stream": False
            }

            try:
                # USING REQUESTS (Like WAN-Studio)
                response = requests.post("https://api.x.ai/v1/chat/completions", headers=headers, json=payload, timeout=30)
                
                # Check for HTTP codes
                if response.status_code != 200:
                    err_msg = f"HTTP {response.status_code}: {response.text}"
                    print(f"❌ [Z-Image] API Error: {err_msg}")
                    return (f"ERROR: {err_msg}", 1.0, 8, "API Failed", "See prompt output for details.")

                result = response.json()
                content = result['choices'][0]['message']['content'].strip()
                print(f"✅ [Z-Image] Response received: {content[:50]}...")

                # Since the new instruction strictly asks for only the prompt, 
                # we return it directly. We still keep a loose JSON check just in case.
                try:
                    if content.startswith("{") and "prompt" in content:
                        data = json.loads(content)
                        return (
                            data.get("prompt", content),
                            float(data.get("cfg", 1.0)),
                            int(data.get("steps", 8)),
                            f"Source: Grok API | ~{cls.estimate_tokens(data.get('prompt', ''))} Toks",
                            data.get("breakdown", "Parsed successfully.")
                        )
                except:
                    pass

                # Default fallback for the new "Strictly only prompt" instruction
                return (
                    content, 
                    1.0, 
                    8, 
                    f"Source: Grok API | ~{cls.estimate_tokens(content)} Toks", 
                    "Successfully generated expert prompt."
                )

            except Exception as e:
                print(f"❌ [Z-Image] Network Exception: {e}")
                return (f"NETWORK ERROR: {str(e)}", 1.0, 8, "Network Failed", str(e))

        # --- 2. FALLBACK PATH (Static Regex) ---
        print("ℹ️ [Z-Image] No API Key -> Using Static Logic")
        
        core_prompt = cls.clean_text(user_idea)
        for p, r in cls.CONSTRAINTS.items():
            if re.search(p, core_prompt, re.IGNORECASE):
                core_prompt = re.sub(p, "", core_prompt, flags=re.IGNORECASE)
                core_prompt += f", {r}"
        
        parts = [core_prompt]
        if framing != "None": parts.append(cls.FRAMING.get(framing, ""))
        if camera != "None": parts.append(cls.CAMERAS.get(camera, ""))
        if lighting != "None": parts.append(cls.LIGHTING.get(lighting, ""))
        if style != "None": parts.append(cls.STYLES.get(style, ""))
        
        final = ", ".join([part for part in parts if part]) + ", professional quality, high resolution"
        
        # Determine params
        cfg, steps = 1.0, 8
        toks = cls.estimate_tokens(final)
        if quality_preset == "Balanced" and toks > 60: cfg, steps = 1.1, 10
        if quality_preset == "Max Quality": cfg, steps = 1.2, 12

        return (final, cfg, steps, f"Source: Static Logic | ~{toks}/77 Toks", "Used regex replacement (No API Key).")
