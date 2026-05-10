import os
import subprocess
import sys
import uuid
import asyncio

IS_VERCEL = os.environ.get("VERCEL") == "1"
PROJECT_ROOT = os.getcwd()

if IS_VERCEL:
    ANIMATION_OUTPUT_DIR = "/tmp/animations"
else:
    ANIMATION_OUTPUT_DIR = os.path.join(PROJECT_ROOT, "static/animations")

os.makedirs(ANIMATION_OUTPUT_DIR, exist_ok=True)

async def run_animation_script(prompt: str) -> str:
    """
    Executes animScript.py to generate an animation.
    Returns the path to the generated video.
    """
    script_id = uuid.uuid4().hex[:8]
    output_filename = f"animation_{script_id}.mp4"
    output_path = os.path.join(ANIMATION_OUTPUT_DIR, output_filename)
    
    script_path = os.path.join(PROJECT_ROOT, "animScript.py")
    
    if not os.path.exists(script_path):
        return None # Script doesn't exist yet
        
    # Execute the script
    # We pass the output path as an argument so the script knows where to save
    try:
        env = os.environ.copy()
        env["SDL_VIDEODRIVER"] = "dummy" # Headless
        env["PYTHONPATH"] = PROJECT_ROOT
        
        proc = await asyncio.create_subprocess_exec(
            sys.executable, script_path,
            "--output", output_path,
            "--prompt", prompt,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env
        )
        await proc.communicate()
        
        if os.path.exists(output_path):
            # Return the URL relative to static
            return f"/static/animations/{output_filename}"
    except Exception as e:
        print(f"Animation execution error: {e}")
        
    return None
