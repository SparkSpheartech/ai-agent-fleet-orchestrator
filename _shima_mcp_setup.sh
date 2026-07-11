#!/bin/bash
set -e
cd /home/shima/comfyui-mcp-server
# install deps (try break-system-packages, fallback)
pip install --break-system-packages -q "requests>=2.31.0" "mcp>=1.2.0" "Pillow>=10.0.0" 2>&1 | tail -2 || pip install -q "requests" "mcp" "Pillow" 2>&1 | tail -2
# config: model defaults (URL comes from COMFYUI_URL env in the service)
mkdir -p /home/shima/.config/comfy-mcp
cat > /home/shima/.config/comfy-mcp/config.json <<'JSON'
{
  "defaults": {
    "image": {
      "model": "sd_xl_base_1.0.safetensors",
      "width": 1024,
      "height": 1024,
      "steps": 25,
      "cfg": 7.0,
      "sampler_name": "euler",
      "scheduler": "normal",
      "negative_prompt": "text, watermark, blurry, low quality"
    },
    "video": {
      "duration": 5,
      "fps": 16
    }
  }
}
JSON
chown -R shima:shima /home/shima/.config/comfy-mcp
echo "deps + config done"
python3 -c "import mcp, requests, PIL; print('imports OK')" 2>&1 | tail -1
