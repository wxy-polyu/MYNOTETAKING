from flask import Blueprint, jsonify, request
from src.services.llm import translate_text

translate_bp = Blueprint("translate", __name__)


@translate_bp.route("/translate", methods=["POST"])
def translate():
    try:
        data = request.get_json(silent=True) or {}
        target_language = (data.get("target_language") or "en").strip()
        source_language = data.get("source_language") or "auto"
        title = (data.get("title") or "").strip()
        content = (data.get("content") or "").strip()
        text = (data.get("text") or "").strip()

        if not target_language:
            return jsonify({"error": "target_language is required"}), 400

        if title or content:
            translated_title = (
                translate_text(title, target_language, source_language) if title else ""
            )
            translated_content = (
                translate_text(content, target_language, source_language) if content else ""
            )
            return jsonify(
                {
                    "translated_title": translated_title,
                    "translated_content": translated_content,
                    "translated_text": translated_content or translated_title,
                    "target_language": target_language,
                }
            )

        translated = translate_text(text, target_language, source_language)
        return jsonify(
            {
                "translated_title": "",
                "translated_content": translated,
                "translated_text": translated,
                "target_language": target_language,
            }
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 502
    except Exception as e:
        return jsonify({"error": str(e)}), 500
