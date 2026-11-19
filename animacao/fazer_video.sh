#!/usr/bin/env bash
# Gera o vídeo completo: vozes -> áudio (trilha + efeitos) -> quadros -> MP4 final.
# Requer: python3 (piper-tts, pycairo, numpy, scipy), ffmpeg, fontes Patrick Hand e Luckiest Guy instaladas,
# e os modelos de voz pt_BR (faber, cadu, jeff) em $VOZES_DIR.
set -euo pipefail
cd "$(dirname "$0")"
python3 linha_do_tempo.py
python3 audio.py
python3 render.py
mkdir -p ../video
ffmpeg -loglevel error -y -i build/video_mudo.mp4 -i build/audio.wav \
  -af "loudnorm=I=-14:TP=-1.5:LRA=11" -c:v copy -c:a aac -b:a 192k -ar 44100 -ac 2 \
  -movflags +faststart -shortest "../video/A_Cidade_que_Apaga_as_6.mp4"
python3 render.py --png 2.6 && mv build/quadro_*.png ../video/capa.png
echo "pronto: video/A_Cidade_que_Apaga_as_6.mp4"
