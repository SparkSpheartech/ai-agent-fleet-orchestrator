#!/bin/bash
pkill -f sd_xl_base 2>/dev/null
sleep 1
rm -f /mnt/pve/Storage1/comfyui/models/checkpoints/sd_xl_base_1.0.safetensors
systemd-run --unit=comfyui-sdxl-dl bash -c 'curl -L -o /mnt/pve/Storage1/comfyui/models/checkpoints/sd_xl_base_1.0.safetensors "https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors" > /mnt/pve/Storage1/comfyui/sdxl_dl.log 2>&1'
echo "launched unit rc=$?"
