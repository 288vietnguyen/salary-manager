import os
import re
import json
import imaplib
import email
from email.header import decode_header
from html.parser import HTMLParser
from typing import Optional

BASE_DIR     = os.path.dirname(__file__)
_DATA_DIR    = os.environ.get("SM_DATA_DIR",   BASE_DIR)
_BUNDLE_DIR  = os.environ.get("SM_BUNDLE_DIR", BASE_DIR)
CONFIG_FILE  = os.path.join(_DATA_DIR, "gmail_config.json")

# ── Config ────────────────────────────────────────────────────────────────────

def load_config() -> dict:
    if not os.path.exists(CONFIG_FILE):
        return {"email": "", "app_password": "", "sender_filter": "", "amount_regex": ""}
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)


def save_config(gmail_email: str, app_password: str, sender_filter: str, amount_regex: str) -> None:
    with open(CONFIG_FILE, "w") as f:
        json.dump({
            "email": gmail_email,
            "app_password": app_password,
            "sender_filter": sender_filter,
            "amount_regex": amount_regex,
        }, f, indent=2)


def is_connected() -> bool:
    cfg = load_config()
    return bool(cfg.get("email") and cfg.get("app_password"))


# ── IMAP connection ───────────────────────────────────────────────────────────

def _connect() -> imaplib.IMAP4_SSL:
    from fastapi import HTTPException
    cfg = load_config()
    if not cfg.get("email") or not cfg.get("app_password"):
        raise HTTPException(status_code=401, detail="Gmail credentials not configured.")
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
        mail.login(cfg["email"], cfg["app_password"])
        return mail
    except imaplib.IMAP4.error as e:
        raise HTTPException(status_code=401, detail=f"Gmail login failed: {e}")


# ── Email parsing helpers ─────────────────────────────────────────────────────

def _decode_header_value(value: str) -> str:
    parts = decode_header(value)
    result = []
    for part, charset in parts:
        if isinstance(part, bytes):
            result.append(part.decode(charset or "utf-8", errors="replace"))
        else:
            result.append(part)
    return "".join(result)


def _html_to_text(html: str) -> str:
    """Convert HTML to plain text, preserving table row boundaries as newlines."""
    class _P(HTMLParser):
        def __init__(self):
            super().__init__()
            self.lines, self._cur = [], []

        def handle_starttag(self, tag, attrs):
            if tag in ("tr", "br", "p", "div", "li", "h1", "h2", "h3", "h4"):
                if self._cur:
                    self.lines.append(" ".join(self._cur))
                    self._cur = []
            elif tag in ("td", "th"):
                self._cur.append("\t")

        def handle_data(self, data):
            s = data.strip()
            if s:
                self._cur.append(s)

        def get_text(self):
            if self._cur:
                self.lines.append(" ".join(self._cur))
            return "\n".join(self.lines)

    p = _P()
    p.feed(html)
    return p.get_text()


_KPI_BONUS_KEYWORDS      = ["thưởng đánh giá kpi", "thưởng kpi", "kpi bonus", "kpis bonus"]
_KPI_DEDUCTION_KEYWORDS  = ["trừ đánh giá kpi", "trừ kpi", "kpi deduction", "kpi penalty"]


def _number_from_line(line: str) -> Optional[float]:
    """Return the rightmost valid number (≥5 digits) from a single line."""
    nums = re.findall(r"-?\d[\d.,]*\d", line)
    for n in reversed(nums):
        cleaned = re.sub(r"[.,]", "", n.lstrip("-"))
        if cleaned.isdigit() and len(cleaned) >= 5:
            return float(cleaned)
    return None


def _extract_kpi(text: str) -> dict:
    """Return {'kpi_bonus': float|None, 'kpi_deduction': float|None}."""
    bonus      = None
    deduction  = None
    lines      = text.splitlines()
    for i, line in enumerate(lines):
        ll = line.lower()
        if bonus is None and any(kw in ll for kw in _KPI_BONUS_KEYWORDS):
            # Try same line first, then next line
            for sl in lines[i:i + 2]:
                v = _number_from_line(sl)
                if v is not None:
                    bonus = v
                    break
        if deduction is None and any(kw in ll for kw in _KPI_DEDUCTION_KEYWORDS):
            for sl in lines[i:i + 2]:
                v = _number_from_line(sl)
                if v is not None:
                    deduction = v
                    break
    return {"kpi_bonus": bonus, "kpi_deduction": deduction}


def _amount_from_text(text: str, compiled_re) -> Optional[float]:
    """Try regex first, then keyword proximity search on multiline text."""
    # 1. Regex match
    if compiled_re:
        match = compiled_re.search(text)
        if match:
            try:
                raw = match.group("amount").replace(",", "").replace(".", "")
                return float(raw)
            except (IndexError, ValueError):
                pass

    # 2. Keyword proximity: find the line with a net-salary keyword,
    #    then grab the rightmost number on that line or the next line.
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if any(kw in line.lower() for kw in _NET_KEYWORDS):
            search_lines = lines[i:i + 3]
            for sl in search_lines:
                nums = re.findall(r"\d[\d.,]*\d", sl)
                for n in reversed(nums):
                    cleaned = re.sub(r"[.,]", "", n)
                    if cleaned.isdigit() and len(cleaned) >= 5:
                        return float(cleaned)
    return None


def _extract_images(msg) -> list:
    images = []
    for part in msg.walk():
        if part.get_content_maintype() == "image":
            payload = part.get_payload(decode=True)
            if payload:
                images.append(payload)
    return images


# ── OCR ───────────────────────────────────────────────────────────────────────

_ocr_reader = None
MODELS_DIR  = os.path.join(_BUNDLE_DIR, "models")

_NET_KEYWORDS = [
    # New format (row VI)
    "số tiền thực lĩnh",
    "thực lĩnh",
    # Common Vietnamese payslip terms
    "lương net",
    "thực nhận",
    "lươngnet",
    "thực tế nhận",
    # English equivalents
    "net salary",
    "take home",
    "net pay",
    "amount payable",
]

def _get_ocr_reader():
    global _ocr_reader
    if _ocr_reader is None:
        import easyocr
        _ocr_reader = easyocr.Reader(
            ["vi", "en"],
            gpu=False,
            model_storage_directory=MODELS_DIR,
            download_enabled=False,
        )
    return _ocr_reader


def _amount_from_image(image_bytes: bytes) -> Optional[float]:
    try:
        import numpy as np
        from PIL import Image
        import io

        reader  = _get_ocr_reader()
        img     = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        results = reader.readtext(np.array(img), detail=1)

        items = []
        for bbox, text, _ in results:
            xs = [p[0] for p in bbox]
            ys = [p[1] for p in bbox]
            items.append((sum(ys) / 4, sum(xs) / 4, text.strip()))

        net_y = None
        for y, x, text in items:
            if any(kw in text.lower() for kw in _NET_KEYWORDS):
                net_y = y
                break

        if net_y is None:
            for _, _, text in reversed(items):
                cleaned = re.sub(r"[.,\s]", "", text)
                if cleaned.isdigit() and len(cleaned) >= 6:
                    return float(cleaned)
            return None

        row_numbers = []
        for y, x, text in items:
            if abs(y - net_y) <= 15:
                cleaned = re.sub(r"[.,\s]", "", text)
                if cleaned.isdigit() and len(cleaned) >= 5:
                    row_numbers.append((x, float(cleaned)))

        if row_numbers:
            return max(row_numbers, key=lambda t: t[0])[1]
        return None
    except Exception as e:
        print(f"[OCR] error: {e}", flush=True)
        return None


# ── Scan ──────────────────────────────────────────────────────────────────────

def scan_emails(year: Optional[int] = None, month: Optional[int] = None) -> list:
    cfg           = load_config()
    sender_filter = cfg.get("sender_filter", "")
    amount_regex  = cfg.get("amount_regex", "")
    compiled_re   = re.compile(amount_regex) if amount_regex else None

    mail = _connect()
    mail.select("inbox")

    # Build IMAP search criteria
    criteria = []
    if sender_filter:
        criteria.append(f'FROM "{sender_filter}"')
    if year and month:
        import calendar
        # IMAP date format: DD-Mon-YYYY
        months_abbr = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        last_day    = calendar.monthrange(year, month)[1]
        since_date  = f"01-{months_abbr[month-1]}-{year}"
        before_date = f"{last_day:02d}-{months_abbr[month-1]}-{year}"
        criteria.append(f'SINCE "{since_date}" BEFORE "{before_date}"')

    search_query = " ".join(criteria) if criteria else "ALL"
    _, data = mail.search(None, search_query)
    msg_ids = data[0].split()[-50:]  # last 50 messages

    results = []
    for mid in reversed(msg_ids):
        _, raw = mail.fetch(mid, "(RFC822)")
        msg = email.message_from_bytes(raw[0][1])

        subject   = _decode_header_value(msg.get("Subject", ""))
        from_addr = _decode_header_value(msg.get("From", ""))
        date_str  = msg.get("Date", "")

        try:
            dt        = email.utils.parsedate_to_datetime(date_str)
            msg_year  = dt.year
            msg_month = dt.month
        except Exception:
            continue

        # Collect plain text and HTML bodies
        plain_text = ""
        html_text  = ""
        for part in msg.walk():
            ct = part.get_content_type()
            payload = part.get_payload(decode=True)
            if not payload:
                continue
            charset = part.get_content_charset() or "utf-8"
            decoded = payload.decode(charset, errors="replace")
            if ct == "text/plain" and not plain_text:
                plain_text = decoded
            elif ct == "text/html" and not html_text:
                html_text = _html_to_text(decoded)

        amount     = None
        unresolved = True
        kpi        = {"kpi_bonus": None, "kpi_deduction": None}

        # 1. Try plain text
        if plain_text:
            result = _amount_from_text(plain_text, compiled_re)
            if result is not None:
                amount, unresolved = result, False
            kpi = _extract_kpi(plain_text)

        # 2. Try HTML table text
        if unresolved and html_text:
            result = _amount_from_text(html_text, compiled_re)
            if result is not None:
                amount, unresolved = result, False
        if html_text and kpi["kpi_bonus"] is None and kpi["kpi_deduction"] is None:
            kpi = _extract_kpi(html_text)

        # 3. Fall back to OCR on image attachments
        if unresolved:
            for img_bytes in _extract_images(msg):
                extracted = _amount_from_image(img_bytes)
                if extracted is not None:
                    amount, unresolved = extracted, False
                    break

        results.append({
            "year":          msg_year,
            "month":         msg_month,
            "amount":        amount,
            "subject":       subject,
            "from":          from_addr,
            "date":          date_str,
            "unresolved":    unresolved,
            "kpi_bonus":     kpi["kpi_bonus"],
            "kpi_deduction": kpi["kpi_deduction"],
        })

    mail.logout()
    results.sort(key=lambda r: (r["year"], r["month"]), reverse=True)
    return results
