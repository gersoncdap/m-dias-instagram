# Ferramentas do agente Instagram (@gersononovo)

- conteudo.py: lista POSTS da semana (14 itens: carrossel às 10h e reel/post às 18h, de quarta a terça). Modelo da semana 1.
- gerar.py: gera as artes (PNG 1080x1350, paleta preto/vermelho/amarelo, assinatura "Gerson Santos | Executivo na Área da Saúde") e os Reels (MP4 1080x1920) em /home/claude/ig_agent/out e grava manifest.json.
  Requer Pillow, ffmpeg e a fonte Inter em /usr/share/fonts/opentype/inter/.

Fluxo semanal: escrever conteudo.py da semana -> python3 gerar.py -> copiar out/post* para semanaN/ neste repositório -> git push -> agendar no Metricool (brandId 7840682, America/Sao_Paulo) com media = https://raw.githubusercontent.com/gersoncdap/m-dias-instagram/main/semanaN/<arquivo>, draft = true.
