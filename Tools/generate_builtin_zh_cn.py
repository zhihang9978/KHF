from __future__ import annotations

import html
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Dict, List
from xml.sax.saxutils import escape


SECTIONS = [
    "login",
    "general",
    "settings",
    "chat_list",
    "private_chats",
    "groups_and_channels",
    "camera_and_media",
    "profile",
    "bots_and_payments",
    "stories",
    "passport",
    "unsorted",
    "unused",
]

ROOT = Path(__file__).resolve().parents[1]
SOURCE_STRINGS = ROOT / "TMessagesProj" / "src" / "main" / "res" / "values" / "strings.xml"
TARGET_DIR = ROOT / "TMessagesProj" / "src" / "main" / "res" / "values-zh-rCN"
TARGET_STRINGS = TARGET_DIR / "strings.xml"
MISSING_REPORT = ROOT / "Tools" / "generated_builtin_zh_cn_missing.txt"

BRAND_NAME = "安卫通"
BRAND_NAME_BETA = "安卫通"

DIRECT_OVERRIDES = {
    "AppName": BRAND_NAME,
    "AppNameBeta": BRAND_NAME_BETA,
    "LanguageName": "简体中文",
    "English": "英语",
    "LanguageNameInEnglish": "Chinese (Simplified)",
    "LanguageCode": "zh_cn",
    "ContinueOnThisLanguage": "使用简体中文继续",
    "Page1Title": BRAND_NAME,
}

PLURAL_SUFFIXES = ("_zero", "_one", "_two", "_few", "_many", "_other")


def fetch_url(url: str, data: bytes | None = None, retries: int = 4) -> str:
    headers = {"User-Agent": "Mozilla/5.0"}
    if data is not None:
        headers["X-Requested-With"] = "XMLHttpRequest"
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, data=data, headers=headers)
            with urllib.request.urlopen(req, timeout=90) as resp:
                return resp.read().decode("utf-8", "ignore")
        except Exception as exc:
            last_error = exc
            if attempt == retries - 1:
                raise
            time.sleep(1.0 + attempt * 1.5)
    assert last_error is not None
    raise last_error


def normalize_site_value(value: str) -> str:
    value = html.unescape(value)
    value = value.replace("<br/>", r"\n").replace("<br />", r"\n").replace("<br>", r"\n")
    value = value.replace('<mark class="token">', "").replace("</mark>", "")
    value = re.sub(r"</?mark\b[^>]*>", "", value)
    return value.strip()


def replace_branding(value: str) -> str:
    replacements = [
        ("Telegram Premium", f"{BRAND_NAME} Premium"),
        ("Teamgram Premium", f"{BRAND_NAME} Premium"),
        ("Telegram Business", f"{BRAND_NAME} Business"),
        ("Teamgram Business", f"{BRAND_NAME} Business"),
        ("Telegram Passport", f"{BRAND_NAME} Passport"),
        ("Teamgram Passport", f"{BRAND_NAME} Passport"),
        ("Telegram Stars", f"{BRAND_NAME} Stars"),
        ("Teamgram Stars", f"{BRAND_NAME} Stars"),
        ("Telegram Beta", f"{BRAND_NAME} Beta"),
        ("Teamgram Beta", f"{BRAND_NAME} Beta"),
        ("Telegram", BRAND_NAME),
        ("Teamgram", BRAND_NAME),
    ]
    for source, target in replacements:
        value = value.replace(source, target)
    return value


def parse_source_strings() -> Dict[str, str]:
    text = SOURCE_STRINGS.read_text(encoding="utf-8")
    values: Dict[str, str] = {}
    for match in re.finditer(r'<string name="([^"]+)">(.*?)</string>', text, re.S):
        values[match.group(1)] = match.group(2).strip()
    return values


def parse_section_entries(html_text: str) -> Dict[str, str]:
    entries: Dict[str, str] = {}
    pattern = re.compile(
        r'<div class="tr-key".*?data-key="([^"]+)".*?<div class="tr-val tr-val-current">(.*?)</div>',
        re.S,
    )
    for key, value in pattern.findall(html_text):
        cleaned = normalize_site_value(value)
        if cleaned:
            entries[key] = cleaned
    return entries


def parse_offset_data(html_text: str) -> str | None:
    match = re.search(r'data-offset-data="([^"]+)"', html_text)
    return html.unescape(match.group(1)) if match else None


def load_section_translations(section: str) -> Dict[str, str]:
    url = f"https://translations.telegram.org/zh-hans/android/{section}/"
    page = fetch_url(url)
    entries = parse_section_entries(page)
    offset = 200
    offset_data = parse_offset_data(page)
    while 'class="tr-load-more load-more"' in page:
        payload = {"offset": str(offset), "more": "1"}
        if offset_data:
            payload["offset_data"] = offset_data
        page = fetch_url(url, urllib.parse.urlencode(payload).encode("utf-8"))
        entries.update(parse_section_entries(page))
        offset += 200
        offset_data = parse_offset_data(page)
    return entries


def xml_text(value: str) -> str:
    if "<a " in value or "</a>" in value:
        return f"<![CDATA[{value}]]>"
    return escape(value, {'"': "&quot;"})


def build_translations(source_strings: Dict[str, str], site_strings: Dict[str, str]) -> Dict[str, str]:
    translations: Dict[str, str] = {}
    missing: List[str] = []
    for key, source in source_strings.items():
        translated = DIRECT_OVERRIDES.get(key)
        if translated is None:
            translated = site_strings.get(key)
        if translated is None:
            for suffix in PLURAL_SUFFIXES:
                if key.endswith(suffix):
                    translated = site_strings.get(key[: -len(suffix)])
                    if translated is not None:
                        break
        if translated is None:
            translated = source
            missing.append(key)
        translations[key] = replace_branding(translated)
    MISSING_REPORT.write_text("\n".join(missing) + ("\n" if missing else ""), encoding="utf-8")
    return translations


def write_target_strings(translations: Dict[str, str]) -> None:
    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    lines = ['<?xml version="1.0" encoding="utf-8"?>', "<resources>"]
    for key, value in translations.items():
        lines.append(f'    <string name="{key}">{xml_text(value)}</string>')
    lines.append("</resources>")
    TARGET_STRINGS.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    source_strings = parse_source_strings()
    site_strings: Dict[str, str] = {}
    for section in SECTIONS:
        site_strings.update(load_section_translations(section))
    translations = build_translations(source_strings, site_strings)
    write_target_strings(translations)
    print(f"generated {len(translations)} strings -> {TARGET_STRINGS}")
    print(f"missing report -> {MISSING_REPORT}")


if __name__ == "__main__":
    main()
