"""API 구조 탐색용: 응답의 '구조(키/타입)'와 오류 메시지만 출력하고 실제 데이터 값은 출력하지 않는다."""
import json, os, sys, urllib.request

RAW = os.environ.get("KALODATA_API_KEY", "")
KEY = RAW.strip()
# 키 값은 출력하지 않고 형태만 점검
print(f"[key check] length={len(KEY)}, ascii={KEY.isascii()}, had_whitespace={RAW != KEY}, inner_space={' ' in KEY}")
if not KEY.isascii() or any(c.isspace() for c in KEY):
    sys.exit("키에 한글/공백 등 허용되지 않는 문자가 있습니다. Secret에 키 값만 넣어주세요.")
BASE = "https://www.kalodata.com/openapi/v1/tiktok/"
EPS = ["product/rank","product/detail","shop/rank","shop/detail","creator/rank","creator/detail",
       "creator/avatar-images","video/rank","video/detail","video/url","livestream/rank","livestream/detail"]
bodies = json.loads(os.environ.get("PROBE_BODIES") or "{}")

def shape(v, d=0):
    if d > 4: return "…"
    if isinstance(v, dict): return {k: shape(x, d+1) for k, x in v.items()}
    if isinstance(v, list): return [shape(v[0], d+1)] if v else []
    return type(v).__name__

def call(ep, body):
    req = urllib.request.Request(BASE+ep, data=json.dumps(body).encode(), method="POST",
        headers={"Content-Type":"application/json","X-API-KEY":KEY})
    try:
        with urllib.request.urlopen(req, timeout=30) as r: return json.load(r)
    except urllib.error.HTTPError as e:
        try: return json.load(e)
        except Exception: return {"http_error": e.code}

for ep in EPS:
    body = bodies.get(ep, {})
    r = call(ep, body)
    out = {k: r.get(k) for k in ("success","code","message","errorCategory","cached") if k in r}
    out["data_shape"] = shape(r.get("data"))
    print(f"### {ep}  body={json.dumps(body)}")
    print(json.dumps(out, ensure_ascii=False, indent=1)[:3000])
