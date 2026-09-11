from __future__ import annotations

import base64
import csv
import io
import os
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import cv2
import numpy as np
import pandas as pd
import pytesseract
import httpx
from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image

app = FastAPI(title="Forestfit Direct OCR Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SIZE_ORDER = ["XS", "S", "M", "L", "XL", "2XL", "3XL", "4XL", "5XL", "FREE"]


def txt(v) -> str:
    if v is None:
        return ""
    return str(v).strip()


def norm(v) -> str:
    return re.sub(r"\s+", " ", txt(v).replace("\u00a0", " ")).strip()


def clean(v) -> str:
    return re.sub(r"[^가-힣a-zA-Z0-9]", "", norm(v)).lower()


def normalize_size(s: str) -> str:
    s = txt(s).upper()
    return {"F1": "S", "F2": "M", "F3": "L", "F": "FREE"}.get(s, s)


def add_one_day(date: datetime) -> datetime:
    return date + timedelta(days=1)


def fmt_date(date: Optional[datetime]) -> str:
    return date.strftime("%Y-%m-%d") if date else ""


def date_from_text(s: str) -> Optional[datetime]:
    s = txt(s)
    now = datetime.now()
    if "금일" in s or "재고 보유" in s:
        return now

    m = re.search(r"(\d{1,2})\s*[/.월]\s*(\d{1,2})", s)
    if m:
        return datetime(now.year, int(m.group(1)), int(m.group(2)))

    m = re.search(r"(\d{1,2})\s*일", s)
    if m:
        return datetime(now.year, now.month, int(m.group(1)))

    return None


def forestfit_date_from_text(s: str) -> str:
    d = date_from_text(s)
    return fmt_date(add_one_day(d)) if d else ""


def expand_sizes(expr: str) -> List[str]:
    expr = txt(expr).upper().replace(" ", "")
    expr = expr.replace("F1", "S").replace("F2", "M").replace("F3", "L")
    out: List[str] = []

    for part in expr.split(","):
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            if a in SIZE_ORDER and b in SIZE_ORDER:
                ia, ib = SIZE_ORDER.index(a), SIZE_ORDER.index(b)
                start, end = sorted([ia, ib])
                out.extend(SIZE_ORDER[start : end + 1])
        else:
            out.append(normalize_size(part))

    return sorted(set(out), key=lambda x: SIZE_ORDER.index(x) if x in SIZE_ORDER else 999)


def parse_option(option: str) -> Dict[str, str]:
    parts = [p.strip() for p in re.split(r"[,/|]", txt(option)) if p.strip()]
    color, length, size = "", "", ""

    for p in parts:
        up = p.upper()
        if not size and normalize_size(up) in SIZE_ORDER:
            size = normalize_size(up)
        elif not length and p in ["숏", "기본", "롱"]:
            length = p
        elif not color:
            color = p

    return {"color": color, "length": length, "size": size}


def normalize_code_for_match(v: str) -> str:
    s = txt(v).upper()
    s = re.sub(r"^1\.?YP\.?", "", s)
    s = re.sub(r"^YP\.?", "", s)
    s = re.sub(r"^[A-Z가-힣]+[-_.\s]*(?=\d)", "", s)
    s = re.sub(r"^S\.A\.", "", s)
    s = re.sub(r"[^A-Z0-9-]", "", s)
    return s


def code_base(s: str, vendor: str) -> Dict[str, str]:
    original = txt(s).upper()
    c = normalize_code_for_match(original)
    length = "기본"

    if vendor == "리자드":
        liz = re.sub(r"[^A-Z0-9-]", "", original)
        if re.search(r"[A-Z0-9]S$", liz):
            length = "숏"
            liz = liz[:-1]
        elif re.search(r"[A-Z0-9]L$", liz):
            length = "롱"
            liz = liz[:-1]
        liz = re.sub(r"^[A-Z]+-?(?=\d)", "", liz)
        c = normalize_code_for_match(liz)
    else:
        if c.endswith("SH"):
            length = "숏"
            c = c[:-2]
        elif c.endswith("LO"):
            length = "롱"
            c = c[:-2]

    return {"code": c, "length": length}


def code_match(a: str, b: str) -> bool:
    ca, cb = clean(normalize_code_for_match(a)), clean(normalize_code_for_match(b))
    if not ca or not cb:
        return False
    if ca == cb or ca in cb or cb in ca:
        return True
    return ca.split("-")[0] == cb.split("-")[0]


def choose_vendor(row: Dict[str, str]) -> str:
    s = f"{row.get('codeColor','')} {row.get('buyName','')} {row.get('product','')}".upper()
    if re.search(r"LC-|LS-", s):
        return "리자드"
    if "YP" in s or "9056" in s:
        return "노른자"
    if "5508" in s or "리마인드" in s or "REMIND" in s:
        return "리마인드"
    return "케이디지"


def preprocess_image(file_bytes: bytes) -> np.ndarray:
    pil = Image.open(io.BytesIO(file_bytes)).convert("RGB")
    img = np.array(pil)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    scale = 2.0
    img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 5, 75, 75)

    # 표 이미지 OCR 안정화
    th = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 11
    )
    return th


def image_to_text(file_bytes: Optional[bytes]) -> str:
    if not file_bytes:
        return ""
    img = preprocess_image(file_bytes)
    config = "--psm 6 --oem 3"
    return pytesseract.image_to_string(img, lang="kor+eng", config=config)


def schedule_from_text_for_size(line: str, size: str) -> Dict[str, str]:
    if re.search(r"문의\s*시|재고표\s*안내", line):
        return {"status": "확인필요", "date": "", "note": line}
    if re.search(r"판매\s*종료|재고\s*소진", line):
        return {"status": "품절/종료", "date": "", "note": line}

    chunks = [norm(c) for c in re.split(r"[/\n]+", txt(line)) if norm(c)]
    wanted = normalize_size(size)

    for ch in chunks:
        d = forestfit_date_from_text(ch)
        if not d:
            continue

        parens = re.findall(r"\(([^()]*)\)", ch)
        if not parens:
            return {"status": "매칭완료", "date": d, "note": ch}

        for p in parens:
            if wanted in expand_sizes(p):
                return {"status": "매칭완료", "date": d, "note": ch}

    return {"status": "확인필요", "date": "", "note": "일정 확인 필요"}


def parse_vendor_text(text: str, vendor: str) -> List[Dict[str, str]]:
    lines = [norm(x) for x in txt(text).splitlines() if norm(x)]
    out: List[Dict[str, str]] = []

    if vendor == "리자드":
        code_rx = re.compile(r"(?:LC|LS)-\d{3,5}-[A-Z0-9]+[SL]?", re.I)
    elif vendor == "노른자":
        code_rx = re.compile(r"(?:1\.?\s*)?(?:YP\.?)?\s*\d{4,5}-\d+(?:SH|LO)?", re.I)
    else:
        code_rx = re.compile(r"\d{4,5}-\d+(?:SH|LO)?", re.I)

    for line in lines:
        m = code_rx.search(line)
        if not m:
            continue

        base = code_base(m.group(0), vendor)
        for size0 in ["XS", "S", "M", "L", "XL", "2XL", "3XL", "4XL", "5XL", "F", "F2", "F3", "FREE"]:
            size = normalize_size(size0)
            # 라인에 사이즈 또는 날짜가 있으면 후보로 평가
            if size0 not in line.upper() and not date_from_text(line) and "재고 보유" not in line:
                continue
            sch = schedule_from_text_for_size(line, size)
            out.append({
                "vendor": vendor,
                "code": base["code"],
                "length": base["length"],
                "size": size,
                "status": sch["status"],
                "date": sch["date"],
                "note": sch["note"],
                "raw": line,
            })

    return out


def read_base_excel(file_bytes: bytes) -> List[Dict[str, str]]:
    df = pd.read_excel(io.BytesIO(file_bytes), header=None, dtype=str).fillna("")
    rows = df.values.tolist()

    start = 1
    for i, r in enumerate(rows[:30]):
        if "옵션" in txt(r[6]) or "주문" in txt(r[8]) or "품번" in txt(r[9]) or "상품" in txt(r[9]):
            start = i + 1
            break

    out: List[Dict[str, str]] = []
    for r in rows[start:]:
        order_qty = int(float(txt(r[8]).replace(",", "") or 0))
        received_qty = int(float(txt(r[11]).replace(",", "") or 0))
        shortage = order_qty - received_qty
        if shortage < 1:
            continue

        out.append({
            "supplier": txt(r[0]),
            "buyName": txt(r[4]),
            "product": txt(r[5]),
            "option": txt(r[6]),
            "codeColor": txt(r[9]),
            "barcode": txt(r[10]),
            "orderQty": order_qty,
            "receivedQty": received_qty,
            "shortage": shortage,
        })

    return out


def make_cellmate_csv(rows: List[Dict[str, str]]) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["입고예정번호", "상품명", "옵션내용", "바코드번호", "입고예정일", "입고예정수량", "삭제여부"])
    for r in rows:
        if r.get("date") and r.get("barcode") and r.get("status") == "매칭완료":
            writer.writerow(["", "", "", r["barcode"], r["date"], "", ""])
    return output.getvalue()


@app.post("/analyze")
async def analyze(
    base_file: UploadFile = File(...),
    kdg_image: Optional[UploadFile] = File(None),
    lizard_image: Optional[UploadFile] = File(None),
    noreunja_image: Optional[UploadFile] = File(None),
    remind_image: Optional[UploadFile] = File(None),
):
    base_bytes = await base_file.read()
    base_rows = read_base_excel(base_bytes)

    image_map = {
        "케이디지": await kdg_image.read() if kdg_image else None,
        "리자드": await lizard_image.read() if lizard_image else None,
        "노른자": await noreunja_image.read() if noreunja_image else None,
        "리마인드": await remind_image.read() if remind_image else None,
    }

    ocr_texts: Dict[str, str] = {}
    schedules: List[Dict[str, str]] = []

    for vendor, img_bytes in image_map.items():
        text = image_to_text(img_bytes) if img_bytes else ""
        ocr_texts[vendor] = text
        schedules.extend(parse_vendor_text(text, vendor))

    result_rows: List[Dict[str, str]] = []
    for row in base_rows:
        vendor = choose_vendor(row)
        base_code = code_base(row.get("codeColor", ""), vendor)
        opt = parse_option(row.get("option", ""))
        size = normalize_size(opt.get("size", ""))
        length = opt.get("length") or base_code["length"]

        candidates = [
            s for s in schedules
            if s["vendor"] == vendor
            and code_match(base_code["code"], s["code"])
            and s["size"] == size
            and (not s["length"] or not length or s["length"] == length)
        ]

        chosen = next((c for c in candidates if c.get("date")), None) or (candidates[0] if candidates else None)

        result = dict(row)
        result["vendor"] = vendor
        if chosen:
            result["status"] = chosen.get("status", "")
            result["date"] = chosen.get("date", "")
            result["note"] = chosen.get("note", "")
        else:
            result["status"] = ""
            result["date"] = ""
            result["note"] = ""

        result_rows.append(result)

    cellmate_csv = make_cellmate_csv(result_rows)
    cellmate_csv_b64 = base64.b64encode(cellmate_csv.encode("utf-8-sig")).decode("ascii")

    return {
        "result_rows": result_rows,
        "ocr_texts": ocr_texts,
        "schedule_count": len(schedules),
        "cellmate_csv_base64": cellmate_csv_b64,
    }

# ============================================================
# Sellmate API integration
# - Existing OCR endpoints remain unchanged.
# - Sellmate credentials are read ONLY from environment variables.
# ============================================================

SELLMATE_BASE_URL = "https://c-api.sellmate.co.kr/external"
SELLMATE_DOMAIN = os.getenv("SELLMATE_DOMAIN", "").strip()
SELLMATE_ACCESS_TOKEN = os.getenv("SELLMATE_ACCESS_TOKEN", "").strip()

def sellmate_headers() -> Dict[str, str]:
    if not SELLMATE_DOMAIN:
        raise HTTPException(
            status_code=500,
            detail="SELLMATE_DOMAIN 환경변수가 설정되지 않았습니다."
        )
    if not SELLMATE_ACCESS_TOKEN:
        raise HTTPException(
            status_code=500,
            detail="SELLMATE_ACCESS_TOKEN 환경변수가 설정되지 않았습니다."
        )
    return {
        "Authorization": f"Bearer {SELLMATE_ACCESS_TOKEN}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

async def sellmate_get(interface_path: str, params: Optional[Dict[str, str]] = None):
    path = interface_path if interface_path.startswith("/") else f"/{interface_path}"
    url = f"{SELLMATE_BASE_URL}/{SELLMATE_DOMAIN}{path}"

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                url,
                headers=sellmate_headers(),
                params=params or {},
            )
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"셀메이트 API 연결 실패: {exc}"
        )

    # Do not expose the access token or Authorization header in errors.
    if response.status_code >= 400:
        detail = response.text[:1000]
        raise HTTPException(
            status_code=response.status_code,
            detail=f"셀메이트 API 오류 ({response.status_code}): {detail}"
        )

    try:
        return response.json()
    except ValueError:
        raise HTTPException(
            status_code=502,
            detail="셀메이트 API가 JSON이 아닌 응답을 반환했습니다."
        )

@app.get("/api/sellmate/health")
async def sellmate_health():
    return {
        "ok": True,
        "sellmate_domain_configured": bool(SELLMATE_DOMAIN),
        "sellmate_token_configured": bool(SELLMATE_ACCESS_TOKEN),
        "message": (
            "환경변수 설정 완료. 실제 API 테스트가 가능합니다."
            if SELLMATE_DOMAIN and SELLMATE_ACCESS_TOKEN
            else "SELLMATE_DOMAIN / SELLMATE_ACCESS_TOKEN 설정이 필요합니다."
        ),
    }

@app.get("/api/sellmate/orders")
async def sellmate_orders(
    page: int = Query(1, ge=1),
    per_page: int = Query(100, ge=1, le=500),
):
    """
    Sellmate: GET /orders
    첫 실데이터 연결 테스트용.
    """
    data = await sellmate_get(
        "/orders",
        {"page": str(page), "per_page": str(per_page)},
    )
    return data

@app.get("/api/sellmate/stock-work-categories")
async def sellmate_stock_work_categories(
    page: int = Query(1, ge=1),
    per_page: int = Query(100, ge=1, le=500),
):
    """
    Sellmate: GET /stockWorkCategories
    재고/입출고 작업구분 확인용.
    """
    data = await sellmate_get(
        "/stockWorkCategories",
        {"page": str(page), "per_page": str(per_page)},
    )
    return data

@app.get("/api/sellmate/products")
async def sellmate_products(
    page: int = Query(1, ge=1),
    per_page: int = Query(100, ge=1, le=500),
):
    """
    Sellmate product endpoint.
    기본 경로는 /products로 두되, 실제 개발자 문서의 상품 엔드포인트가
    다른 경우 SELLMATE_PRODUCTS_PATH 환경변수로 변경할 수 있도록 구성.
    """
    product_path = os.getenv("SELLMATE_PRODUCTS_PATH", "/products").strip() or "/products"
    data = await sellmate_get(
        product_path,
        {"page": str(page), "per_page": str(per_page)},
    )
    return data

# ============================================================
# FLOW Open API
# ============================================================

FLOW_BASE_URL = "https://api.flow.team"
FLOW_API_KEY = os.getenv("FLOW_API_KEY", "").strip()


def flow_headers() -> Dict[str, str]:
    if not FLOW_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="FLOW_API_KEY 환경변수가 설정되지 않았습니다."
        )

    return {
        "Content-Type": "application/json",
        "x-flow-api-key": FLOW_API_KEY,
    }


async def flow_get(interface_path: str, params: Optional[Dict[str, str]] = None):
    path = interface_path if interface_path.startswith("/") else f"/{interface_path}"
    url = f"{FLOW_BASE_URL}{path}"

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                url,
                headers=flow_headers(),
                params=params or {},
            )
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"FLOW API 연결 실패: {exc}"
        )

    if response.status_code >= 400:
        detail = response.text[:1500]
        raise HTTPException(
            status_code=response.status_code,
            detail=f"FLOW API 오류 ({response.status_code}): {detail}"
        )

    try:
        return response.json()
    except ValueError:
        raise HTTPException(
            status_code=502,
            detail="FLOW API가 JSON이 아닌 응답을 반환했습니다."
        )


@app.get("/api/flow/health")
async def flow_health():
    return {
        "ok": True,
        "flow_api_key_configured": bool(FLOW_API_KEY),
        "message": (
            "FLOW API KEY가 정상적으로 설정되었습니다."
            if FLOW_API_KEY
            else "FLOW_API_KEY 환경변수가 설정되지 않았습니다."
        ),
    }


@app.get("/api/flow/projects")
async def flow_projects(cursor: str = Query("0")):
    """
    FLOW User API: GET /user/projects
    현재 API Key 사용자에게 접근 가능한 프로젝트 목록을 조회합니다.
    """
    data = await flow_get(
        "/user/projects",
        {"cursor": cursor},
    )
    return data
