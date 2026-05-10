import os
import csv
import uuid
import asyncio
import sys
from typing import List
from utils.chat import call_llm
from dotenv import load_dotenv

load_dotenv()

# --- Configuration ---
IS_VERCEL = os.environ.get("VERCEL") == "1" or os.environ.get("VERCEL_REGION") is not None

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PLUGIN_DIR = os.path.dirname(__file__)
LIB_DIR = os.path.abspath(os.path.join(PLUGIN_DIR, "..", "speadyanimation"))

if IS_VERCEL:
    SCRIPTS_DIR = "/tmp/scripts"
    ANIMATION_OUTPUT_DIR = "/tmp/animations"
else:
    SCRIPTS_DIR = os.path.join(PLUGIN_DIR, "scripts")
    ANIMATION_OUTPUT_DIR = os.path.join(PROJECT_ROOT, "static", "animations")


os.makedirs(SCRIPTS_DIR, exist_ok=True)
os.makedirs(ANIMATION_OUTPUT_DIR, exist_ok=True)

# Load library context for the AI
CONTEXT_PATH = os.path.join(LIB_DIR, "context.txt")
try:
    with open(CONTEXT_PATH, "r") as f:
        SPEADY_CONTEXT = f.read()
except:
    SPEADY_CONTEXT = "No context file found. Use standard SpeadyAnimation/Manim syntax."

class AnimationPlugin:
    """Handles the full lifecycle of AI-generated animations."""
    
    @staticmethod
    async def _get_direct_code(prompt: str) -> str:
        system_prompt = (
            "You are a SpeadyAnimation Engineer. Write Python code using the speadyanimation library.\n"
            f"Library Rules:\n{SPEADY_CONTEXT}\n"
            "CREATIVE STANDARDS (GyanDeep Reference):\n"
            "1. Geometry before Algebra: Show shapes/visuals first, equations second.\n"
            "2. Breathing Room: Add self.wait(2.0) after every major reveal.\n"
            "3. 3B1B Palette: BG: #1C1C1C, BLUE: #58C4DD, GREEN: #83C167, YELLOW: #FFFF00.\n"
            "4. Monospace: Use mono fonts for text.\n"
            "Task: Generate a script for the user's request.\n"
            "IMPORTANT: Use '{output_path}' as the filename in your render() call.\n"
            "Output ONLY raw Python code."
        )
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}]
        code = await call_llm(messages)
        
        # Clean markdown
        lines = code.splitlines()
        clean = []
        in_block = False
        for line in lines:
            if line.strip().startswith("```"):
                in_block = not in_block
                continue
            if in_block or (not line.strip().startswith("#") and line.strip()):
                clean.append(line)
        return "\n".join(clean).strip()

    @staticmethod
    async def _get_fallback_data(prompt: str, script_id: str) -> List[str]:
        system_prompt = (
            "Analyze the user's request and provide high-quality educational metadata.\n"
            "Output exactly one line of CSV with these 4 fields:\n"
            "1. Explanation: A concise, high-impact summary (max 15 words).\n"
            "2. Equation: A relevant LaTeX mathematical formula.\n"
            "3. GraphType: One of [line, scatter, circle, rect, none].\n"
            "4. Points: If line/scatter, provide 5-10 points as x1:y1,x2:y2... (range 0-10).\n"
            "DO NOT include any extra text, quotes, or markdown. ONLY THE CSV LINE."
        )
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}]
        csv_line = await call_llm(messages)
        csv_line = csv_line.strip().replace('"', '').replace('`', '')
        
        # Log for user inspection
        # Always prioritize /tmp in production environments
        if IS_VERCEL or os.path.exists("/var/task"):
            log_dir = "/tmp/logs"
        else:
            log_dir = os.path.join(PROJECT_ROOT, "data", "fallback_logs")

        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, f"log_{script_id}.txt")
        
        with open(log_path, "w") as f:
            f.write(f"PROMPT: {prompt}\n")
            f.write(f"GENERATED CSV: {csv_line}\n")

            
        try:
            return next(csv.reader([csv_line]))
        except:
            return ["Animation", "", "none", ""]

    @classmethod
    async def run_animation(cls, prompt: str) -> str:
        script_id = uuid.uuid4().hex[:8]
        output_filename = f"animation_{script_id}.mp4"
        output_path = os.path.join(ANIMATION_OUTPUT_DIR, output_filename)
        
        # 1. Try Direct
        code = await cls._get_direct_code(prompt)
        if code:
            script_path = os.path.join(SCRIPTS_DIR, f"gen_{script_id}.py")
            final_code = code.replace("{output_path}", output_path)
            
            # Inject pathing
            inject = f"import sys, os\nsys.path.insert(0, r'{LIB_DIR}')\nsys.path.insert(0, r'{PROJECT_ROOT}')\n"
            if "import os" not in final_code:
                final_code = "import os\n" + inject + final_code
            else:
                final_code = final_code.replace("import os", "import os\n" + inject)
            
            with open(script_path, "w") as f:
                f.write(final_code)
            
            env = os.environ.copy()
            env["SDL_VIDEODRIVER"] = "dummy"
            # Crucial: inherit the full path for Vercel
            env["PYTHONPATH"] = os.pathsep.join(sys.path)
            
            proc = await asyncio.create_subprocess_exec(
                sys.executable, script_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=PROJECT_ROOT, # Run from project root
                env=env
            )

            _, stderr = await proc.communicate()
            
            if proc.returncode == 0:
                return output_path
            print(f"Direct animation failed: {stderr.decode()}")

        # 2. Fallback
        print("Falling back to structured renderer...")
        data = await cls._get_fallback_data(prompt, script_id)
        explanation, equation, g_type, g_points = (data + ["", "", "none", ""])[:4]
        
        try:
            from core.plugin.fallback_renderer import FallbackScene
            os.environ["SDL_VIDEODRIVER"] = "dummy"
            
            # Run in a separate thread if it's blocking, but speady is relatively fast for fallback
            scene = FallbackScene(explanation, equation, g_type, g_points, output_path)
            scene.render(preview=False, export=True, filename=output_path)
            
            if os.path.exists(output_path):
                return output_path
        except Exception as e:
            print(f"Fallback render error: {e}")
            
        raise RuntimeError(f"Animation generation failed completely.")


async def generate_animation(prompt: str, user_id: str = None):
    """Bridge for the main application."""
    return await AnimationPlugin.run_animation(prompt)
