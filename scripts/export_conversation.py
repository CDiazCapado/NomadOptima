"""
scripts/export_conversation.py
Exporta los archivos .jsonl de conversaciones de Claude Code a HTML legible.

Uso:
    python scripts/export_conversation.py

Genera un HTML por cada .jsonl encontrado en la carpeta del proyecto Claude.
"""

import json
import os
from pathlib import Path
from datetime import datetime

CLAUDE_PROJECTS_DIR = Path("C:/Users/cri/.claude/projects/D--Proyectos-4geeks-Proyecto-Final-nomadoptima")
OUTPUT_DIR = Path("data/processed/conversations")

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>{title}</title>
<style>
  body {{ font-family: 'Segoe UI', sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; background: #f5f5f5; }}
  h1 {{ color: #333; border-bottom: 2px solid #ccc; padding-bottom: 10px; }}
  .stats {{ background: #e8f4f8; padding: 10px 15px; border-radius: 6px; margin-bottom: 20px; font-size: 14px; }}
  .message {{ margin: 12px 0; padding: 12px 16px; border-radius: 8px; line-height: 1.6; }}
  .user {{ background: #d1e7dd; border-left: 4px solid #0f5132; }}
  .assistant {{ background: #fff; border-left: 4px solid #0d6efd; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
  .tool {{ background: #fff3cd; border-left: 4px solid #ffc107; font-family: monospace; font-size: 12px; }}
  .role {{ font-weight: bold; font-size: 11px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px; color: #555; }}
  .user .role {{ color: #0f5132; }}
  .assistant .role {{ color: #0d6efd; }}
  .tool .role {{ color: #856404; }}
  .text {{ white-space: pre-wrap; word-break: break-word; }}
  .interrupted {{ background: #f8d7da; border-left: 4px solid #dc3545; padding: 6px 12px; font-style: italic; color: #842029; border-radius: 4px; margin: 8px 0; font-size: 13px; }}
  .index {{ position: sticky; top: 0; background: #343a40; color: white; padding: 8px 15px; border-radius: 6px; margin-bottom: 20px; font-size: 13px; }}
</style>
</head>
<body>
<h1>💬 {title}</h1>
<div class="stats">{stats}</div>
<div class="index">📋 Conversación exportada — {count} mensajes | Usa Ctrl+F para buscar</div>
{messages}
</body>
</html>"""


def extract_text(content):
    """Extrae texto legible de un bloque de contenido."""
    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        parts = []
        for block in content:
            if not isinstance(block, dict):
                continue
            btype = block.get("type", "")

            if btype == "text":
                text = block.get("text", "").strip()
                if text:
                    parts.append(("text", text))

            elif btype == "thinking":
                # Pensamiento interno — opcional mostrarlo
                pass

            elif btype == "tool_use":
                name = block.get("name", "?")
                inp  = block.get("input", {})
                # Mostrar solo info clave del tool
                if name == "Bash":
                    cmd = inp.get("command", "")[:200]
                    parts.append(("tool", f"🔧 Bash: {cmd}"))
                elif name in ("Read", "Write", "Edit"):
                    fp = inp.get("file_path", "")
                    parts.append(("tool", f"📄 {name}: {fp}"))
                elif name == "Write":
                    fp = inp.get("file_path", "")
                    parts.append(("tool", f"✏️ Write: {fp}"))
                elif name == "TodoWrite":
                    parts.append(("tool", f"📝 TodoWrite"))
                else:
                    parts.append(("tool", f"🔧 {name}"))

            elif btype == "tool_result":
                result = block.get("content", "")
                if isinstance(result, str) and result.strip():
                    preview = result.strip()[:300]
                    parts.append(("tool", f"↩ Resultado: {preview}"))

        return parts

    return []


def escape_html(text):
    return (text
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;"))


def process_jsonl(filepath):
    """Lee un .jsonl y devuelve lista de mensajes procesados."""
    messages = []
    with open(filepath, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                msg = json.loads(line)
            except:
                continue

            m = msg.get("message", {})
            role    = m.get("role", "")
            content = m.get("content", [])

            # Mensajes interrumpidos
            if isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "text":
                        text = block.get("text", "")
                        if "[Request interrupted by user]" in text:
                            messages.append({"role": "interrupted", "parts": []})
                            break

            if role not in ("user", "assistant"):
                continue

            parts = extract_text(content)
            if parts:
                messages.append({"role": role, "parts": parts if isinstance(parts, list) else [("text", parts)]})

    return messages


def render_messages(messages):
    html_parts = []
    for i, msg in enumerate(messages):
        role = msg["role"]

        if role == "interrupted":
            html_parts.append('<div class="interrupted">⚠️ [Mensaje interrumpido por el usuario]</div>')
            continue

        parts = msg.get("parts", [])
        if not parts:
            continue

        css = "user" if role == "user" else "assistant"
        label = "👤 Carlos" if role == "user" else "🤖 Claude"

        inner = []
        for ptype, ptext in parts:
            escaped = escape_html(ptext)
            if ptype == "tool":
                inner.append(f'<div class="message tool"><span class="role">Tool</span><div class="text">{escaped}</div></div>')
            else:
                inner.append(f'<div class="text">{escaped}</div>')

        html_parts.append(
            f'<div class="message {css}">'
            f'<div class="role">{label}</div>'
            + "\n".join(inner) +
            f'</div>'
        )

    return "\n".join(html_parts)


MEMORY_DIR = Path("C:/Users/cri/.claude/projects/D--Proyectos-4geeks-Proyecto-Final-nomadoptima/memory")

# Palabras clave que marcan decisiones importantes en los mensajes del usuario
DECISION_KEYWORDS = [
    'decidimos', 'decision', 'decisión', 'vamos a', 'quiero que', 'no quiero',
    'confirmo', 'aprobado', 'adelante', 'hazlo', 'feature', 'arquetipo',
    'idioma', 'presupuesto', 'filtro', 'escala', 'categoria', 'categoría',
    'modelo', 'clustering', 'ciudad', 'notebook', 'importante', 'critico',
    'crítico', 'cambia', 'elimina', 'añade', 'nuevo', 'rediseño', 'rediseno'
]


def is_decision_message(text):
    """Detecta si un mensaje del usuario contiene una decisión relevante."""
    low = text.lower()
    return any(kw in low for kw in DECISION_KEYWORDS)


def export_decisions_md(jsonl_path, messages):
    """
    Genera un markdown condensado con solo las decisiones importantes.
    Solo incluye mensajes del usuario que contengan decisiones,
    más la respuesta inmediata de Claude.
    Destino: memory/decisions_log_<id>.md — para que Claude lo lea en futuras sesiones.
    """
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)

    size_mb = jsonl_path.stat().st_size / (1024 * 1024)
    lines_md = [
        f"# Decisiones — Conversación {jsonl_path.stem[:8]}",
        f"*Archivo original: {jsonl_path.name} ({size_mb:.1f} MB)*",
        f"*Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}*",
        "",
        "---",
        "",
        "> Este archivo contiene solo los mensajes con decisiones de diseño,",
        "> arquitectura o funcionalidad. Generado automáticamente para contexto",
        "> en futuras sesiones de Claude Code.",
        "",
        "---",
        ""
    ]

    decision_count = 0
    i = 0
    while i < len(messages):
        msg = messages[i]
        if msg["role"] != "user":
            i += 1
            continue

        # Extraer texto del mensaje de usuario
        user_text = ""
        for ptype, ptext in msg.get("parts", []):
            if ptype == "text":
                user_text += ptext + " "
        user_text = user_text.strip()

        if not user_text or not is_decision_message(user_text):
            i += 1
            continue

        # Incluir este mensaje y la siguiente respuesta de Claude
        lines_md.append(f"### 👤 Carlos")
        lines_md.append(user_text)
        lines_md.append("")

        # Buscar la siguiente respuesta de Claude (texto, no tool)
        j = i + 1
        while j < len(messages):
            next_msg = messages[j]
            if next_msg["role"] == "assistant":
                assistant_text = ""
                for ptype, ptext in next_msg.get("parts", []):
                    if ptype == "text":
                        assistant_text += ptext + " "
                assistant_text = assistant_text.strip()
                if assistant_text:
                    lines_md.append(f"### 🤖 Claude")
                    lines_md.append(assistant_text[:800] + ("..." if len(assistant_text) > 800 else ""))
                    lines_md.append("")
                break
            j += 1

        lines_md.append("---")
        lines_md.append("")
        decision_count += 1
        i += 1

    out_path = MEMORY_DIR / f"decisions_log_{jsonl_path.stem[:8]}.md"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines_md))

    return out_path, decision_count


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    jsonl_files = sorted(CLAUDE_PROJECTS_DIR.glob("*.jsonl"))
    if not jsonl_files:
        print(f"No se encontraron archivos .jsonl en {CLAUDE_PROJECTS_DIR}")
        return

    print(f"Encontrados {len(jsonl_files)} archivos de conversacion\n")

    for jsonl_path in jsonl_files:
        size_mb = jsonl_path.stat().st_size / (1024 * 1024)
        print(f"Procesando: {jsonl_path.name} ({size_mb:.1f} MB)...")

        messages = process_jsonl(jsonl_path)

        user_msgs      = sum(1 for m in messages if m["role"] == "user")
        assistant_msgs = sum(1 for m in messages if m["role"] == "assistant")
        interrupted    = sum(1 for m in messages if m["role"] == "interrupted")

        # — HTML completo para Carlos —
        title = f"Conversación NomadOptima — {jsonl_path.stem[:8]}"
        stats = (f"📊 Total mensajes: {len(messages)} | "
                 f"👤 Usuario: {user_msgs} | "
                 f"🤖 Claude: {assistant_msgs} | "
                 f"⚠️ Interrumpidos: {interrupted} | "
                 f"📁 Archivo: {jsonl_path.name} | "
                 f"💾 Tamaño: {size_mb:.1f} MB")

        rendered = render_messages(messages)
        html = HTML_TEMPLATE.format(
            title=title,
            stats=stats,
            count=len(messages),
            messages=rendered
        )

        html_path = OUTPUT_DIR / f"conversacion_{jsonl_path.stem[:8]}.html"
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"  OK HTML: {html_path} ({len(messages)} mensajes)")

        # — MD de decisiones para Claude —
        md_path, decision_count = export_decisions_md(jsonl_path, messages)
        print(f"  OK MD decisiones: {md_path} ({decision_count} decisiones)")
        print()

    print(f"Listo.")
    print(f"   HTMLs en:      {OUTPUT_DIR.resolve()}")
    print(f"   MD decisiones: {MEMORY_DIR.resolve()}")


if __name__ == "__main__":
    main()
