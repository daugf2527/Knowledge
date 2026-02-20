"""
侦察阶段 Demo v2 — 融合 Techackz 设计 + 防作弊专项签名库
改进点（对比 Techackz）：
  ✅ 正则匹配（headers/html/cookies）
  ✅ 置信度评分（0-100）
  ✅ URL 主动探测（确认路径存在）
  ✅ async 并发（curl_cffi + asyncio）
  ✅ TLS/JA3 指纹伪装（Techackz 用 aiohttp，无此能力）
  ✅ 防作弊专项签名库（Techackz 无）

依赖：
    pip install curl_cffi beautifulsoup4 python-Wappalyzer colorama

用法：
    python recon_demo.py https://目标网站.com
    python recon_demo.py https://目标网站.com -o result.json
"""

import sys
import json
import re
import asyncio
import argparse
import warnings
from urllib.parse import urlparse
from dataclasses import dataclass, field
from typing import Optional

from curl_cffi.requests import AsyncSession
from bs4 import BeautifulSoup
from colorama import Fore, Style, init as colorama_init

warnings.filterwarnings("ignore", category=UserWarning)

try:
    from Wappalyzer import Wappalyzer, WebPage
    HAS_WAPPALYZER = True
except ImportError:
    HAS_WAPPALYZER = False

colorama_init(autoreset=True)

# ══════════════════════════════════════════════════════════
# 防作弊签名库：headers/cookies/html 全用正则；weight=置信度权重
# ══════════════════════════════════════════════════════════
ANTIBOT = {
    # ── 国际 CDN / WAF ──────────────────────────────────────
    "Cloudflare":         {"h": {"cf-ray": r".+", "server": r"cloudflare"}, "c": {"cf_clearance": r".+", "__cfduid": r".+"}, "p": [r"challenges\.cloudflare\.com", r"cf-challenge"], "probe": [], "tier": "tier2", "w": 40},
    "Cloudflare Turnstile":{"h": {}, "c": {"cf_turnstile_token": r".+"}, "p": [r"challenges\.cloudflare\.com/turnstile/v0/api\.js", r"class=['\"]cf-turnstile", r"data-cf-turnstile-response"], "probe": [], "tier": "tier2+captcha", "w": 40},
    "Akamai":             {"h": {"x-akamai-transformed": r".+", "akamai-request-id": r".+"}, "c": {"abck": r".+", "bm_sz": r".+"}, "p": [r"akamaiedge\.net", r"_abck\s*="], "probe": [], "tier": "tier3", "w": 40},  # _abck/bm_sz 需 JS 生成，curl_cffi 无法伪造
    "DataDome":           {"h": {"server": r"(?i)datadome", "x-datadome-cid": r".+"}, "c": {"datadome": r".+"}, "p": [r"datadome\.co/tags\.js", r"interstitial\.datadome"], "probe": [], "tier": "tier3", "w": 45},
    "PerimeterX/HUMAN":   {"h": {}, "c": {"_pxvid": r".+", "_px2": r".+", "pxcts": r".+"}, "p": [r"perimeterx\.net", r"px-cdn\.net", r"human\.security"], "probe": [], "tier": "tier3", "w": 45},
    "Kasada":             {"h": {"x-kpsdk-ct": r".+", "x-kpsdk-r": r".+"}, "c": {"x-kpsdk-": r".+"}, "p": [r"149e9513-[\w-]+\.js", r"kpsdk"], "probe": [], "tier": "tier3", "w": 50},
    "Imperva":            {"h": {"x-cdn": r"(?i)incapsula", "x-iinfo": r".+"}, "c": {"visid_incap_": r".+", "incap_ses_": r".+", "nlbi_": r".+"}, "p": [r"incapdns\.net"], "probe": [], "tier": "tier2", "w": 35},
    "F5/Shape":           {"h": {"x-wa-info": r".+"}, "c": {"TS01": r".+", "BIGipServer": r".+"}, "p": [r"shape\.io"], "probe": [], "tier": "tier3", "w": 45},
    "Sucuri":             {"h": {"x-sucuri-id": r".+", "x-sucuri-cache": r".+", "server": r"Sucuri(\-Cloudproxy)?"}, "c": {}, "p": [r"sucuri\.net/privacy-policy", r"cdn\.sucuri\.net", r"cloudproxy@sucuri\.net"], "probe": [], "tier": "tier2", "w": 35},
    "Radware AppWall":    {"h": {"x-sl-compstate": r".+"}, "c": {}, "p": [r"CloudWebSec\.radware\.com", r"Unauthorized Request Blocked"], "probe": [], "tier": "tier2", "w": 35},
    "AWS WAF":            {"h": {"x-amz-id": r".+", "x-amz-request-id": r".+", "x-blocked-by-waf": r".+"}, "c": {"aws-alb": r".+", "awsalb": r".+"}, "p": [r"Request blocked.*?AWS WAF", r"aws-managed-rules"], "probe": [], "tier": "tier2", "w": 35},
    "Fastly Shield":      {"h": {"fastly-debug-digest": r".+", "x-served-by": r"cache-.+"}, "c": {}, "p": [r"fastly\.net/beacon"], "probe": [], "tier": "tier1", "w": 20},
    "Vercel WAF":         {"h": {}, "c": {}, "p": [r"Vercel Security Checkpoint", r"/vercel/security/", r"vercel\.com/security"], "probe": [], "tier": "tier2", "w": 30},  # x-vercel-id 仅是 CDN 路由头，不代表 WAF；只靠 HTML checkpoint 特征
    # ── CAPTCHA 服务 ────────────────────────────────────────
    "reCAPTCHA":          {"h": {}, "c": {"_GRECAPTCHA": r".+"}, "p": [r"google\.com/recaptcha", r"recaptcha\.net/recaptcha", r"grecaptcha\.execute"], "probe": [], "tier": "tier2+captcha", "w": 30},
    "hCaptcha":           {"h": {}, "c": {}, "p": [r"hcaptcha\.com/1/api\.js", r"h-captcha", r"data-hcaptcha-sitekey"], "probe": [], "tier": "tier2+captcha", "w": 30},
    "Arkose/FunCaptcha":  {"h": {}, "c": {"fc-": r".+"}, "p": [r"arkoselabs\.com", r"funcaptcha\.com", r"arkoselabs_public_key"], "probe": [], "tier": "tier3+captcha", "w": 40},
    # ── 国内防作弊 ───────────────────────────────────────────
    "极验GeeTest":        {"h": {}, "c": {}, "p": [r"static\.geetest\.com", r"gcaptcha4\.geetest\.com", r"api\.geetest\.com", r"initGeetest"], "probe": [], "tier": "tier2+captcha", "w": 35},
    "网易易盾":           {"h": {}, "c": {"ne_": r".+"}, "p": [r"cstaticdun\.126\.net", r"dun\.163\.com", r"NECaptchaValidate"], "probe": [], "tier": "tier2+captcha", "w": 35},
    "数美Shumei":         {"h": {}, "c": {"smidV2": r".+"}, "p": [r"static\.portal101\.cn", r"fp-it\.portal101\.cn", r"smSdk"], "probe": [], "tier": "tier2", "w": 30},
    "腾讯验证码":         {"h": {}, "c": {}, "p": [r"captcha\.gtimg\.com", r"t\.captcha\.qq\.com", r"TencentCaptcha"], "probe": [], "tier": "tier2+captcha", "w": 35},
    "腾讯T-Sec天御":      {"h": {"x-client-verify": r".+"}, "c": {"ptcz": r".+", "skey": r".+"}, "p": [r"lib\.qq\.com/security", r"t\.captcha\.qq\.com/TCaptcha"], "probe": [], "tier": "tier2", "w": 30},
    "阿里云验证码":       {"h": {}, "c": {}, "p": [r"cfca\.aliyundoc\.com", r"nc\.aliyun\.com", r"NoCaptcha", r"aliwangwang"], "probe": [], "tier": "tier2+captcha", "w": 35},
    "阿里云WAF":          {"h": {"x-safe-info": r".+", "x-riskd-info": r".+"}, "c": {"acw_tc": r".+", "acw_sc__v2": r".+"}, "p": [r"aliyun-waf\.com"], "probe": [], "tier": "tier2", "w": 35},
    "瑞数RiskRain":       {"h": {}, "c": {"RSKTOKEN": r".+", "SESSIONID": r"[A-Za-z0-9]{32,}"}, "p": [r"common\.builtit\.cn", r"_\$_[a-zA-Z]", r"jsl\.org\.cn"], "probe": [], "tier": "tier3", "w": 50},
    "顶象Dingxiang":      {"h": {}, "c": {}, "p": [r"static\.dingxiang-inc\.com", r"dx\.dingxiang-inc\.com", r"dingxiang_session"], "probe": [], "tier": "tier2+captcha", "w": 35},
    "百度云盾":           {"h": {"x-bd-logid": r".+", "x-bd-traceid": r".+"}, "c": {"BAIDUID": r".+", "BDORZ": r".+"}, "p": [r"anti\.baidu\.com", r"yunjiasu-cdn\.net"], "probe": [], "tier": "tier2", "w": 30},
    "360网站卫士":        {"h": {"x-cache": r"HIT from .+360"}, "c": {"360sdk": r".+"}, "p": [r"qiniu\.com/360websafe", r"webscan\.360\.cn"], "probe": [], "tier": "tier2", "w": 25},
    "同盾TongDun":        {"h": {}, "c": {"tdid": r".+", "td_": r".+"}, "p": [r"static\.tongdun\.net", r"ac\.tongdun\.net", r"fm\.tongdun\.net", r"blackbox"], "probe": [], "tier": "tier2", "w": 35},
}

# 通用技术栈（借鉴 Techackz CUSTOM_TECH_PATTERNS：regex + probe_urls）
TECH = {
    "WordPress":  {"h": {"x-powered-by": r"WordPress"}, "c": {"wordpress_": r".+"}, "p": [r"/wp-content/", r"/wp-includes/", r"wp-json"], "probe": ["/wp-login.php", "/wp-admin/"]},
    "Shopify":    {"h": {"server": r"(?i)Shopify"}, "c": {"_shopify_": r".+"}, "p": [r"cdn\.shopify\.com", r"myshopify\.com"], "probe": ["/cart"]},
    "Django":     {"h": {}, "c": {"csrftoken": r".+"}, "p": [r"csrfmiddlewaretoken"], "probe": ["/admin/"]},
    "Next.js":    {"h": {"x-powered-by": r"Next\.js"}, "c": {}, "p": [r"__NEXT_DATA__", r"/_next/static/", r"/_next/chunks/"], "probe": []},
    "React":      {"h": {}, "c": {}, "p": [r"__REACT_DEVTOOLS_GLOBAL_HOOK__", r"react-dom(?:\.min)?\.js"], "probe": []},
    "Vue.js":     {"h": {}, "c": {}, "p": [r"__VUE__", r"vue(?:\.min)?\.js"], "probe": []},
    "Nginx":      {"h": {"server": r"(?i)nginx"}, "c": {}, "p": [], "probe": []},
    "Apache":     {"h": {"server": r"(?i)Apache/[\d.]+"}, "c": {}, "p": [], "probe": []},
    "PHP":        {"h": {"x-powered-by": r"PHP/[\d.]+"}, "c": {"PHPSESSID": r".+"}, "p": [], "probe": []},
    "ASP.NET":    {"h": {"x-aspnet-version": r".+", "x-powered-by": r"ASP\.NET"}, "c": {"ASP.NET_SessionId": r".+"}, "p": [r"__VIEWSTATE", r"__EVENTVALIDATION"], "probe": []},
    "CloudFront": {"h": {"x-amz-cf-id": r".+"}, "c": {}, "p": [], "probe": []},
    "Vercel":     {"h": {"x-vercel-id": r".+", "server": r"(?i)vercel"}, "c": {}, "p": [r"vercel\.app", r"/_vercel/"], "probe": []},
    "Fastly CDN": {"h": {"x-served-by": r"cache-.+", "x-cache": r"HIT"}, "c": {}, "p": [], "probe": []},
    "GA4":        {"h": {}, "c": {"_ga": r".+"}, "p": [r"gtag\(", r"G-[A-Z0-9]{6,}"], "probe": []},
    "Segment":    {"h": {}, "c": {"ajs_anonymous_id": r".+", "ajs_user_id": r".+"}, "p": [r"cdn\.segment\.com", r"analytics\.js"], "probe": []},
    "Mixpanel":   {"h": {}, "c": {"mp_": r".+"}, "p": [r"cdn\.mxpnl\.com", r"cdn4\.mxpnl\.com"], "probe": []},
    "Intercom":   {"h": {}, "c": {"intercom-": r".+"}, "p": [r"widget\.intercom\.io", r"intercomcdn\.com"], "probe": []},
    "Stripe":     {"h": {}, "c": {"__stripe_mid": r".+", "__stripe_sid": r".+"}, "p": [r"js\.stripe\.com", r"stripe\.com/v3"], "probe": []},
}


def _tier_level(t: str) -> int:
    return 3 if "tier3" in t else (2 if "tier2" in t else 1)


def _match(pat: dict, headers: dict, cookies: dict, html: str):
    """正则匹配，返回 (置信度, 证据列表)"""
    score, ev = 0, []
    h = {k.lower(): v for k, v in headers.items()}
    c = {k.lower(): v for k, v in cookies.items()}
    for hk, hr in pat.get("h", {}).items():
        val = h.get(hk.lower(), "")
        if val and re.search(hr, val, re.I):
            score += 25
            ev.append(f"hdr:{hk}={val[:40]}")
    for ck, cr in pat.get("c", {}).items():
        for k, v in c.items():
            if k.startswith(ck.lower()) and re.search(cr, v, re.I):
                score += 20
                ev.append(f"cookie:{k}")
                break
    for hp in pat.get("p", []):
        if re.search(hp, html, re.I):
            # 高确定性 pattern（官方 API/SDK URL）给 40 分；普通 pattern 给 15 分
            HIGH_CONF = (
                "turnstile/v0/api",      # Cloudflare Turnstile API script
                "google\\.com/recaptcha", # reCAPTCHA API script
                "recaptcha\\.net/recapt", # reCAPTCHA alternate domain
                "hcaptcha\\.com/1/api",  # hCaptcha API script
                "arkoselabs\\.com",      # Arkose/FunCaptcha
                "funcaptcha\\.com",
                "datadome\\.co/tags",    # DataDome SDK
                "perimeterx\\.net",      # PerimeterX
                "px-cdn\\.net",
                "149e9513-",             # Kasada
                "static\\.geetest\\.com",# GeeTest
                "gcaptcha4\\.geetest",
                "cstaticdun\\.126\\.net",# 网易易盾
                "captcha\\.gtimg\\.com", # 腾讯验证码
            )
            pts = 40 if any(k in hp for k in HIGH_CONF) else 15
            score += pts
            ev.append(f"html:/{hp[:30]}/ +{pts}")
    return min(score, 100), ev


def _classify_error(e: Exception) -> str:
    """把 curl_cffi / asyncio 异常分类为可读的错误码"""
    msg = str(e).lower()
    if isinstance(e, asyncio.TimeoutError) or "timeout" in msg or "timed out" in msg:
        return "TIMEOUT"
    if "ssl" in msg or "certificate" in msg or "tls" in msg:
        return "SSL_ERROR"
    if "too many redirect" in msg or "redirect" in msg:
        return "TOO_MANY_REDIRECTS"
    if "cookie" in msg:
        return "COOKIE_PARSE_ERROR"
    if "connect" in msg or "refused" in msg or "unreachable" in msg:
        return "CONNECTION_ERROR"
    if "proxy" in msg:
        return "PROXY_ERROR"
    return f"ERR_{type(e).__name__}"


async def _fetch(url: str) -> dict:
    """始终返回 dict；失败时含 error_type 字段"""
    try:
        async with AsyncSession(impersonate="chrome124") as s:
            r = await s.get(url, timeout=15, allow_redirects=True,
                            headers={"Accept": "text/html,*/*;q=0.8",
                                     "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"})
            return {"status": r.status_code, "headers": dict(r.headers),
                    "cookies": dict(r.cookies), "html": r.text, "error_type": None}
    except Exception as e:
        etype = _classify_error(e)
        print(f"{Fore.RED}  ✗ fetch 失败 [{etype}]：{str(e)[:100]}{Style.RESET_ALL}")
        return {"status": 0, "headers": {}, "cookies": {}, "html": "", "error_type": etype}


async def _probe(base: str, paths: list) -> list:
    if not paths:
        return []
    origin = f"{urlparse(base).scheme}://{urlparse(base).netloc}"
    found = []
    try:
        async with AsyncSession(impersonate="chrome124") as s:
            results = await asyncio.gather(
                *[s.get(f"{origin}{p}", timeout=6, allow_redirects=False) for p in paths],
                return_exceptions=True,
            )
            for path, r in zip(paths, results):
                if not isinstance(r, Exception) and r.status_code in (200, 301, 302, 403):
                    found.append(f"{path}[{r.status_code}]")
    except Exception:
        pass
    return found


async def scan(url: str, output_path: Optional[str] = None):
    print(f"\n{Fore.CYAN}{'═'*60}")
    print(f"  Anti-Sybil Recon v2  →  {url}")
    print(f"{'═'*60}{Style.RESET_ALL}")

    print(f"\n{Fore.YELLOW}[Pass 1]{Style.RESET_ALL} HTTP 请求（TLS Chrome124 指纹）")
    data = await _fetch(url)

    # ── Fetch 失败：写最小化 JSON 后退出 ──
    if data["error_type"]:
        print(f"  ✗ 无法获取页面，原因：{Fore.RED}{data['error_type']}{Style.RESET_ALL}")
        out = {
            "url": url, "error_type": data["error_type"],
            "intercept_suspected": True,
            "antibot": {}, "tech": {}, "wappalyzer": {},
            "tier_verdict": "tier3",
            "need_captcha_solver": False,
        }
        path = output_path or "recon_result.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=2)
        print(f"  {Fore.YELLOW}[完成] 错误信息已保存 → {path}{Style.RESET_ALL}\n")
        return

    H, C, HTML = data["headers"], data["cookies"], data["html"]
    html_bytes = len(HTML.encode("utf-8"))
    print(f"  status:{data['status']}  headers:{len(H)}  cookies:{len(C)}  html:{html_bytes}字节")

    # ── Pass 2b：隐藏字段扫描（框架文档要求）──
    # 扫描 <input type="hidden"> name 属性，识别极验/同盾/顶象等在表单中注入的隐藏字段
    HIDDEN_FIELDS = {
        "极验GeeTest":   ["geetest_challenge", "geetest_validate", "geetest_seccode"],
        "网易易盾":     ["NECaptchaValidate"],
        "阿里云验证码": ["nc_csessionid", "nc_token"],
        "腾讯验证码":   ["ticket", "randstr"],
        "同盾TongDun":   ["blackbox"],
        "顶象Dingxiang": ["_data_"],
    }
    try:
        from bs4 import BeautifulSoup as _BS
        _soup = _BS(HTML, "html.parser")
        _hidden_names = " ".join(
            (tag.get("name") or "") for tag in _soup.find_all("input", {"type": "hidden"})
        ).lower()
        for _tool, _fields in HIDDEN_FIELDS.items():
            if any(f.lower() in _hidden_names for f in _fields):
                # 如果已在 ANTIBOT 中有该工具则加分，否则直接添加
                if _tool in results_antibot:
                    results_antibot[_tool]["confidence"] = min(results_antibot[_tool]["confidence"] + 20, 100)
                    results_antibot[_tool]["evidence"].append(f"hidden_field:{_fields[0]}")
    except Exception:
        pass

    # ── Pass 2c：瑞数 eval 密文检测（框架文档要求）──
    # 瑞数无固定域名，页面主体为大段 eval(...) 密文是唯一可靠特征
    def _is_ruishu(html_text: str) -> bool:
        try:
            from bs4 import BeautifulSoup as _BS2
            _s2 = _BS2(html_text, "html.parser")
            for sc in _s2.find_all("script"):
                if sc.string and len(sc.string) > 2000 and sc.string.strip().startswith("eval("):
                    return True
        except Exception:
            pass
        return False

    if _is_ruishu(HTML) and "瑞数RiskRain" not in results_antibot:
        results_antibot["瑞数RiskRain"] = {
            "confidence": 80, "tier": "tier3",
            "evidence": ["html:eval(...)密文超2000字符(瑞数RASP特征)"]
        }
        print(f"  {Fore.RED}⚠ 检测到瑞数 RASP：页面主体为 eval(...) 密文，静态扫描失效{Style.RESET_ALL}")

    # ── P0：拦截页检测 ──
    # 硬拦截：4xx/5xx + html<8KB（防作弊JS未注入）
    # 软警告：200 但 html<2KB（可能是空壳挑战页）
    intercept_flag = False
    if data["status"] in (403, 429, 503) and html_bytes < 8192:
        intercept_flag = True
        print(f"  {Fore.RED}⚠ P0 硬拦截：status={data['status']} html={html_bytes}B < 8KB{Style.RESET_ALL}")
    elif data["status"] == 200 and html_bytes < 2048:
        intercept_flag = True
        print(f"  {Fore.YELLOW}⚠ P0 软警告：status=200 但 html 仅 {html_bytes}B（疑似空壳挑战页）{Style.RESET_ALL}")

    results_antibot = {}
    results_tech = {}

    print(f"\n{Fore.YELLOW}[Pass 2]{Style.RESET_ALL} 防作弊签名匹配（regex + 置信度）")
    for name, pat in ANTIBOT.items():
        score, ev = _match(pat, H, C, HTML)
        if score > 0:
            results_antibot[name] = {"confidence": score, "tier": pat["tier"], "evidence": ev}

    print(f"\n{Fore.YELLOW}[Pass 3]{Style.RESET_ALL} 通用技术栈识别（regex）")
    for name, pat in TECH.items():
        score, ev = _match(pat, H, C, HTML)
        if score > 0:
            results_tech[name] = {"confidence": score, "evidence": ev}

    print(f"\n{Fore.YELLOW}[Pass 4]{Style.RESET_ALL} URL 主动探测（确认路径存在）")
    probe_jobs = {n: pat["probe"] for n, pat in {**ANTIBOT, **TECH}.items()
                  if pat.get("probe") and (n in results_antibot or n in results_tech)}
    if probe_jobs:
        probe_results = await asyncio.gather(
            *[_probe(url, paths) for paths in probe_jobs.values()]
        )
        for name, found in zip(probe_jobs, probe_results):
            if found:
                print(f"  {Fore.GREEN}✔ {name}: {found}{Style.RESET_ALL}")
                target = results_antibot if name in results_antibot else results_tech
                target[name]["confidence"] = min(target[name]["confidence"] + 20, 100)
                target[name]["evidence"].extend([f"probe:{p}" for p in found])
    else:
        print(f"  {Fore.LIGHTBLACK_EX}(无需探测路径){Style.RESET_ALL}")

    print(f"\n{Fore.YELLOW}[Pass 5]{Style.RESET_ALL} Wappalyzer 技术栈")
    wapp = {}
    if HAS_WAPPALYZER:
        try:
            w = Wappalyzer.latest()
            pg = WebPage(url, HTML, H)
            wapp = w.analyze_with_categories(pg)
            print(f"  识别到 {len(wapp)} 项技术")
        except Exception as e:
            print(f"  {Fore.RED}✗ {e}{Style.RESET_ALL}")
    else:
        print(f"  {Fore.LIGHTBLACK_EX}(未安装 python-Wappalyzer，跳过){Style.RESET_ALL}")

    # ── 打印报告 ──
    netloc = urlparse(url).netloc
    print(f"\n{Fore.CYAN}{'═'*60}")
    print(f"  侦察报告 — {netloc}")
    print(f"{'═'*60}{Style.RESET_ALL}")

    if results_antibot:
        print(f"\n{Fore.RED}【防作弊工具检测结果】{Style.RESET_ALL}")
        tier_votes = []
        for name, r in sorted(results_antibot.items(), key=lambda x: -x[1]["confidence"]):
            conf = r["confidence"]
            bar = "█" * (conf // 10) + "░" * (10 - conf // 10)
            color = Fore.RED if conf >= 60 else Fore.YELLOW
            print(f"  {color}✦ {name:<22} [{bar}] {conf:>3}%  → {r['tier']}{Style.RESET_ALL}")
            print(f"    {Fore.LIGHTBLACK_EX}{' | '.join(r['evidence'][:3])}{Style.RESET_ALL}")
            tier_votes.append(r["tier"])

        final_tier = max(tier_votes, key=_tier_level)
        need_captcha = any("captcha" in t for t in tier_votes)
        print(f"\n  {Fore.GREEN}▶ 综合推荐 Tier：{final_tier.upper()}{Style.RESET_ALL}", end="")
        if need_captcha:
            print(f"  {Fore.YELLOW}⚠ 需要 CAPTCHA Solver{Style.RESET_ALL}", end="")
        print()
    else:
        print(f"\n  {Fore.GREEN}✔ 未检测到已知防作弊工具 → 推荐 TIER1（纯协议）{Style.RESET_ALL}")
        final_tier = "tier1"

    if results_tech:
        print(f"\n{Fore.BLUE}【技术栈识别结果】{Style.RESET_ALL}")
        for name, r in sorted(results_tech.items(), key=lambda x: -x[1]["confidence"]):
            print(f"  · {name:<18} {r['confidence']:>3}%   {Fore.LIGHTBLACK_EX}{r['evidence'][0] if r['evidence'] else ''}{Style.RESET_ALL}")

    if wapp:
        print(f"\n{Fore.BLUE}【Wappalyzer 补充识别（前10项）】{Style.RESET_ALL}")
        for tech, cats in list(wapp.items())[:10]:
            cat_str = ", ".join(cats) if isinstance(cats, (list, set)) else str(cats)
            print(f"  · {tech:<25} {Fore.LIGHTBLACK_EX}{cat_str}{Style.RESET_ALL}")

    print(f"\n{Fore.CYAN}{'═'*60}{Style.RESET_ALL}")

    # ── 保存 JSON ──
    out = {
        "url": url,
        "error_type": None,
        "intercept_suspected": intercept_flag,
        "antibot": results_antibot,
        "tech": results_tech,
        "wappalyzer": {k: list(v) if isinstance(v, set) else v for k, v in wapp.items()},
        "tier_verdict": final_tier,
        "need_captcha_solver": any("captcha" in t for t in
                                   [r["tier"] for r in results_antibot.values()]),
    }
    path = output_path or "recon_result.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"  {Fore.GREEN}[完成] 结果已保存 → {path}{Style.RESET_ALL}\n")


def main():
    parser = argparse.ArgumentParser(description="Anti-Sybil 侦察工具 v2")
    parser.add_argument("url", nargs="?", default="https://app.galxe.com", help="目标 URL")
    parser.add_argument("-o", "--output", help="输出 JSON 文件路径（默认 recon_result.json）")
    parser.add_argument("--no-probe", action="store_true", help="跳过 URL 主动探测")
    args = parser.parse_args()

    target = args.url if args.url.startswith("http") else f"https://{args.url}"
    asyncio.run(scan(target, args.output))


if __name__ == "__main__":
    main()
