#!/usr/bin/env python3
"""Convert a1_vocab_master_988_final_tts_semantic_confirmed.csv → vocab.json"""

import csv
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
CSV_PATH = ROOT / "a1_vocab_master_988_final_tts_semantic_confirmed.csv"
OUT_PATH = ROOT / "vocab.json"

CATEGORY_EMOJI = {
    '數字': '🔢', '時間': '⏰', '一天': '🌅', '星期': '📅',
    '年月': '📆', '時間段': '🕐', '季節': '🍂', '時間線': '⏳',
    '證件': '🪪', '自介': '👋',
    '家庭': '👨‍👩‍👧', '人': '👤', '職業': '💼', '告示牌': '🪧',
    '活動': '🎉', '節日': '🎊', '運動': '⚽', '遊戲': '🎮',
    '興趣': '🎨', '樂器': '🎵', '學業': '📚', '科目': '📖',
    '書': '📕', '考試': '📝', '語言': '💬', '發音': '🗣️',
    '國家': '🌍', '文件': '📄', '商業': '💰', '銀行': '🏦',
    '資訊': '💻', '文具': '✏️', '身體': '🫀', '顏色': '🌈',
    '天空天氣': '☁️', '方位': '🧭', '地區': '📍', '地理': '🗾',
    '四大洋': '🌊', '七大洲': '🌍', '測量': '📏', '交通': '🚗',
    '地圖': '🗺️', '地方': '🏘️', '郵寄': '📮', '旅行': '✈️',
    '購物': '🛒', '旅館': '🏨', '電影': '🎬', '店鋪': '🏪',
    '吃店': '🍽️', '公設': '🏛️', '街道': '🛣️', '建廳': '🏢',
    '樓層': '🏗️', '家事': '🧹', '傢俱': '🪑', '房間': '🛏️',
    '浴室': '🚿', '藝擺': '🖼️', '電器': '🔌', '材質': '🧱',
    '尺寸': '📐', '飾品': '💍', '頭飾': '👒', '腳飾': '👟',
    '包包': '👜', '衣服': '👕', '保暖': '🧣', '褲子': '👖',
    '化妝保養': '💄', '醫藥': '💊',
    '數量單位': '⚖️', '廚具餐具': '🍳', '餐': '🍱', '飲料': '🥤',
    '主食': '🍚', '鹹食': '🧂', '甜食': '🍰', '調料香料': '🧄',
    '水果': '🍎', '青菜': '🥦', '動物': '🐾', '鳥禽': '🐦',
    '海鮮': '🦐', '植物': '🌿',
    '意見': '💭', '信念情緒': '❤️', '生活': '🏡', '其他': '💡',
}


def main():
    section_order: dict[str, int] = {}
    category_order: dict[tuple[str, str], str] = {}

    vocab: list[dict] = []

    with open(CSV_PATH, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            section = row["大分類"].strip()
            category = row["小分類"].strip()

            # assign section number on first sight
            if section not in section_order:
                section_order[section] = len(section_order) + 1
            sec_no = section_order[section]

            # assign categoryNo "secNo.catIdx" on first sight
            key = (section, category)
            if key not in category_order:
                cat_idx = sum(1 for k in category_order if k[0] == section) + 1
                category_order[key] = f"{sec_no}.{cat_idx}"
            cat_no = category_order[key]

            num = int(row["編號"].strip())
            word_id = f"A1-{num:04d}"
            emoji = CATEGORY_EMOJI.get(category, '📌')
            vocab.append({
                "id": word_id,
                "section": section,
                "sectionNo": sec_no,
                "category": category,
                "categoryEmoji": emoji,
                "categoryNo": cat_no,
                "localNo": int(row["分類內序號"].strip()),
                "zh_cn": row["中文_簡體"].strip(),
                "en": row["English"].strip(),
                "fr": row["Français"].strip(),
                "de": row["Deutsch"].strip(),
                "audio": {
                    "fr": f"assets/audio/fr/{word_id}.mp3",
                    "de": f"assets/audio/de/{word_id}.mp3",
                },
            })

    OUT_PATH.write_text(json.dumps(vocab, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Written {len(vocab)} entries → {OUT_PATH}")


if __name__ == "__main__":
    main()
