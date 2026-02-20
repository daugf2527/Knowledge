# 自适应三级执行策略：Tier 技术解决方案

> 文档定位：对应《自适应三级执行策略框架》Phase 3 执行层，描述每个 Tier 的**完整可闭环技术方案**。  
> 数据来源：WebAutomation.io (Oct 2025)、Scrapfly (Feb 2026)、CapSolver 官方定价、camoufox GitHub。  
> 更新时间：2026-02-20

---

## Web3 任务平台防护体系深度分析

> 来源：Cloudflare 官方文档、Galxe Passport 技术文档、Scrapfly 2026、WebAutomation.io 2025

### Web3 防护的两个层次（必须分开理解）

Web3 平台的防护和传统 Web2 不同，分为**两个完全独立的层**：

```
第一层：前端入口防护（传统 anti-bot）
    ↓ 通过后才能访问页面
第二层：Web3 专属反女巫（链上身份验证）
    ↓ 这才是真正阻止批量账号的核心
```

**只破解第一层是不够的。** 很多 Web3 项目即使你能访问页面、提交任务，最终发放奖励时会用链上数据做女巫过滤，把批量账号全部剔除。

---

### 第一层：前端入口防护（我们侦察阶段覆盖的）

| 平台 | 防护类型 | 技术方案 |
|---|---|---|
| Uniswap | Cloudflare + **Turnstile** | Tier 2 + CAPTCHA Solver |
| Layer3 / Guild / Taskon / Questn / Intract | Cloudflare WAF | Tier 2 TLS 指纹 |
| Bilibili | **GeeTest v4** 滑块 | Tier 2 + CAPTCHA Solver |
| Galxe / Crew3 | 无前端 CAPTCHA | Tier 1 直打 API |
| Zealy | 连接级静默丢包 | Tier 3 Camoufox |
| Airbnb | **DataDome** 行为分析 | Tier 3 + 行为模拟 |

---

### 第二层：Web3 专属反女巫（前端 CAPTCHA 之外的核心防线）

#### 2.1 Galxe Passport（KYC 链上身份）

**机制**：用户通过 Sumsub KYC（上传身份证 + 自拍），验证通过后在链上 mint 一个 Soulbound Token（SBT，不可转让 NFT）。参与需要 Passport 的活动时，合约直接检查钱包是否持有该 SBT。

**技术细节**：
- KYC 由 Sumsub 完成，Galxe 不存储明文 PII
- 用户数据用 AES-256-GCM + 用户密码加密存储
- SBT 合约：`0xe84050261cb0a35982ea0f6f3d9dff4b8ed3c012`（BNB Chain）
- 一个真实身份只能对应一个 Passport

**能否绕过**：**不能**。需要真实身份证 + 活体检测。批量账号无法通过 KYC。

#### 2.2 Gitcoin Passport（链上行为评分）

**机制**：通过收集多个"Stamp"（社交账号、链上行为、ENS 域名等）累积人类证明分数，分数达到阈值才能参与。

**能否绕过**：**极难**。需要真实 Twitter/GitHub/Discord 账号 + 链上历史。

#### 2.3 链上行为分析（事后过滤）

很多项目（如 Hop Protocol、Arbitrum 空投）在发放奖励时，用链上数据做女巫识别：
- 同一 IP 发起的多个钱包
- 资金来源相同（同一 CEX 提款地址）
- 交互时间高度相似
- Gas 费用模式一致

**这层无法在前端绕过**，是事后链上分析。

---

### Cloudflare Turnstile 能否本地计算？

**结论：不能。** 这是最常被问到的问题，直接给出技术依据。

Cloudflare 官方文档明确说明 Turnstile 挑战包含：

| 挑战类型 | 说明 | 能否本地伪造 |
|---|---|---|
| **proof-of-work** | 算力证明，需要在浏览器内完成 | ❌ 结果绑定到浏览器环境 |
| **proof-of-space** | 存储证明 | ❌ 同上 |
| **Web API 探针** | 检测 `navigator`、`screen`、`WebGL`、`AudioContext` 等真实浏览器 API | ❌ Python 没有这些 API |
| **浏览器行为怪癖** | 检测各浏览器版本特有的 JS 执行差异 | ❌ 需要真实浏览器引擎 |

Token 在 **Cloudflare 服务端验证**，验证时会核对：
1. token 对应的浏览器环境信号是否与当前请求 IP 一致
2. token 是否在有效期内（约 120 秒）
3. token 是否已被使用过（一次性）

**本地用 Python 计算出任何值，服务端都会拒绝**，因为没有对应的浏览器环境信号。

**唯一可行的本地方案**：用 Camoufox/Playwright 在真实浏览器引擎内执行 Turnstile JS，让浏览器完成挑战，提取生成的 token。这本质上不是"本地计算"，而是"本地运行真实浏览器"。

---

### hCaptcha accessibility token 方案（已失效）

2021-2022 年曾有一个利用 hCaptcha 无障碍访问 token 的绕过方案（`MainSilent/hCaptcha-Bypass`），原理是：hCaptcha 为视障用户提供了一个特殊 token，可以跳过图像挑战。

**现状**：该仓库已于 2022-01-23 被 archive，作者标注 "mostly deprecated"。hCaptcha 在 2023 年修复了这个漏洞，现在**不可用**。

---

### 各平台实际可行方案汇总

| 平台 | 第一层防护 | 第二层防护 | 可行方案 | 成本 |
|---|---|---|---|---|
| **Galxe**（无 Passport 要求） | 无 | 链上行为分析 | Tier 1 直打 API | 极低 |
| **Galxe**（需要 Passport） | 无 | KYC SBT | **无法批量**，需真实 KYC | — |
| **Layer3** | Cloudflare WAF | 链上行为 | Tier 2 curl_cffi | 低 |
| **Guild.xyz** | Cloudflare WAF | 链上资产门槛 | Tier 2 + 购买对应资产 | 中 |
| **Taskon / Questn / Intract** | Cloudflare WAF | 链上行为 | Tier 2 curl_cffi | 低 |
| **Uniswap** | Cloudflare + Turnstile | 无（前端 DeFi） | Tier 2 + CapSolver | 中（$1.2/1000次） |
| **Zealy** | 连接级丢包 | 链上行为 | Tier 3 Camoufox | 高 |
| **Crew3** | 无 | 链上行为 | Tier 1 直打 API | 极低 |

---

## 总览：三级策略决策树

```
侦察结果（recon_demo.py）
        │
        ├─ 无防作弊 / Fastly / CloudFront / 纯 CDN
        │         → Tier 1：纯协议
        │
        ├─ Cloudflare WAF / Imperva / Sucuri / 阿里云WAF / 百度云盾
        │         → Tier 2：TLS 指纹伪装
        │
        ├─ Cloudflare Turnstile / reCAPTCHA / hCaptcha / GeeTest / 极验
        │         → Tier 2 + CAPTCHA Solver
        │
        ├─ Akamai / DataDome / PerimeterX(HUMAN) / Kasada / F5-Shape / 瑞数
        │         → Tier 3：Playwright 全 DOM
        │
        └─ Tier 3 + 上述 CAPTCHA
                  → Tier 3 + CAPTCHA Solver
```

---

## Tier 1：纯协议（curl_cffi）

### 适用场景

| 防护特征 | 典型站点（本次扫描） |
|---|---|
| 无防作弊工具 | Galxe、Crew3、GitHub、Reddit、Steam |
| 仅 CDN（CloudFront / Fastly） | Amazon、淘宝、163.com |
| 纯静态内容 | 知乎、豆瓣、微博 |

### 核心原理

目标站点不检测 TLS 指纹、不校验 JS 运行环境，标准 HTTP 请求即可通过。

### 技术方案

```python
# pip install curl_cffi
from curl_cffi.requests import Session

def fetch_tier1(url: str, proxy: str = None) -> str:
    with Session() as s:
        r = s.get(
            url,
            timeout=15,
            allow_redirects=True,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                              "AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/124.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
            },
            proxies={"https": proxy} if proxy else None,
        )
        r.raise_for_status()
        return r.text
```

### 关键参数

| 参数 | 推荐值 | 说明 |
|---|---|---|
| 并发数 | 10–50 | 无防护限制，可高并发 |
| 请求间隔 | 0–0.5s | 视目标 QPS 限制调整 |
| IP 类型 | 数据中心代理即可 | 无 IP 质量检测 |
| 重试策略 | 3 次，指数退避 | 应对偶发 5xx |

### 闭环验证

```python
# 验证：响应 status=200 且 HTML 包含目标内容
assert r.status_code == 200
assert "目标关键词" in r.text
```

---

## Tier 2：TLS 指纹伪装（curl_cffi Chrome 模拟）

### 适用场景

| 防护特征 | 典型站点（本次扫描） |
|---|---|
| Cloudflare WAF（无 Turnstile） | Layer3、Guild、Taskon、Questn、Intract |
| Imperva / Sucuri | 企业站点 |
| 阿里云 WAF / 百度云盾 | 国内电商、资讯 |
| AWS WAF（行为规则未触发） | 部分 Web2 站点 |

### 核心原理

Cloudflare 等 WAF 在 TLS 握手阶段检测 **JA3/JA4 指纹**：
- 标准 Python `requests` / `httpx` 的 TLS cipher suite 顺序与 Chrome 不同，立即被识别
- `curl_cffi` 内置真实 Chrome 的 TLS 握手参数（cipher 顺序、扩展列表、GREASE 值），通过 JA3 检测
- HTTP/2 帧顺序、SETTINGS 帧参数也被模拟，通过 ALPN 检测

### 技术方案

```python
# pip install curl_cffi
from curl_cffi.requests import AsyncSession
import asyncio

async def fetch_tier2(url: str, proxy: str = None) -> dict:
    """
    impersonate 可选值：
      chrome99 / chrome101 / chrome107 / chrome110 / chrome116 / chrome124 / chrome131
      safari15_3 / safari15_5 / safari17_0 / safari18_0
      firefox133
    推荐：chrome124（2024 Q2 主流版本，签名库最完整）
    """
    async with AsyncSession(impersonate="chrome124") as s:
        r = await s.get(
            url,
            timeout=15,
            allow_redirects=True,
            headers={
                "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "sec-ch-ua": '"Chromium";v="124", "Google Chrome";v="124"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "none",
                "sec-fetch-user": "?1",
                "upgrade-insecure-requests": "1",
            },
            proxies={"https": proxy} if proxy else None,
        )
        return {
            "status": r.status_code,
            "html": r.text,
            "cookies": dict(r.cookies),
            "headers": dict(r.headers),
        }
```

### 关键参数

| 参数 | 推荐值 | 说明 |
|---|---|---|
| `impersonate` | `chrome124` | 与 Cloudflare 签名库匹配最好 |
| 并发数 | 3–10 | Cloudflare 对同 IP 并发敏感 |
| 请求间隔 | 1–3s | 模拟人类浏览节奏 |
| IP 类型 | 住宅代理（Residential） | 数据中心 IP 被 Cloudflare IP 信誉库降分 |
| Cookie 复用 | 必须 | `cf_clearance` 有效期内复用，避免重复挑战 |

### Cloudflare `cf_clearance` Cookie 复用策略

```python
# 首次获取 cf_clearance（通过 Playwright，见 Tier 3）
# 之后在 Tier 2 中复用
session_cookies = {"cf_clearance": "获取到的值..."}

async with AsyncSession(impersonate="chrome124") as s:
    r = await s.get(url, cookies=session_cookies, ...)
    # cf_clearance 在同域名下有效期约 30 分钟
```

### 代理推荐

| 代理类型 | 推荐服务商 | 适用场景 |
|---|---|---|
| 住宅代理 | Bright Data、Oxylabs、Smartproxy | Cloudflare 高防站点 |
| 移动代理 | Bright Data Mobile、NetNut | PerimeterX IP 检测（Tier 3 用） |
| 数据中心 | 任意 | 仅 Tier 1 使用 |

### 闭环验证

```python
# 验证未被 Cloudflare 拦截
assert r.status_code != 403
assert "Just a moment" not in r.text      # CF 5s 挑战页
assert "cf-ray" in r.headers              # 正常 CF 响应头
assert len(r.text) > 5000                 # 非空壳拦截页
```

---

## Tier 2 + CAPTCHA Solver

### 适用场景

| 防护特征 | 典型站点（本次扫描） |
|---|---|
| Cloudflare Turnstile | Uniswap（API 脚本已确认） |
| reCAPTCHA v2/v3 | 部分 DeFi、企业站 |
| hCaptcha | 部分 Web3 任务平台 |
| 极验 GeeTest v4 | Bilibili、国内站 |

### 核心原理

CAPTCHA Solver 服务（如 CapSolver）在云端维护真实浏览器集群，代替用户完成挑战，返回可用的 token。

### CapSolver 定价参考（2026-02）

| CAPTCHA 类型 | 价格/1000次 | 平均耗时 |
|---|---|---|
| Cloudflare Turnstile | $1.20 | < 3s |
| Cloudflare Challenge (5s) | $1.20 | < 10s |
| reCAPTCHA v2 | $0.80 | < 15s |
| reCAPTCHA v3 | $1.00 | < 5s |
| hCaptcha | $1.00 | < 10s |
| AWS WAF CAPTCHA | $0.60 | < 5s |
| GeeTest v4 | $1.50 | < 10s |

### 技术方案：Cloudflare Turnstile

```python
# pip install capsolver
import capsolver
import asyncio
from curl_cffi.requests import AsyncSession

capsolver.api_key = "YOUR_CAPSOLVER_API_KEY"

async def solve_turnstile(page_url: str, site_key: str) -> str:
    """返回 Turnstile token，有效期约 120s"""
    solution = capsolver.solve({
        "type": "AntiTurnstileTaskProxyLess",
        "websiteURL": page_url,
        "websiteKey": site_key,
    })
    return solution["token"]

async def fetch_with_turnstile(url: str, site_key: str) -> dict:
    token = await asyncio.to_thread(solve_turnstile, url, site_key)

    async with AsyncSession(impersonate="chrome124") as s:
        # 方式一：token 注入表单提交
        r = await s.post(url, data={"cf-turnstile-response": token})
        # 方式二：部分站点通过 API 校验
        # r = await s.get(url, headers={"cf-turnstile-response": token})
        return {"status": r.status_code, "html": r.text}
```

### 技术方案：GeeTest v4（极验）

```python
async def solve_geetest(page_url: str, gt: str, challenge: str) -> dict:
    """
    gt: 极验 gt 值（从 HTML 或 API 获取）
    challenge: 每次请求动态生成的 challenge
    """
    solution = capsolver.solve({
        "type": "GeeTestTaskProxyLess",
        "websiteURL": page_url,
        "gt": gt,
        "challenge": challenge,
        "version": 4,
    })
    return {
        "lot_number": solution["lot_number"],
        "pass_token": solution["pass_token"],
        "gen_time": solution["gen_time"],
        "captcha_output": solution["captcha_output"],
    }
```

### 闭环验证

```python
# Turnstile token 有效性验证（服务端校验）
# 若提交后 status=200 且无错误提示，则 token 有效
assert r.status_code == 200
assert "error" not in r.text.lower()
```

---

## Tier 3：Playwright 全 DOM 渲染

### 适用场景

| 防护特征 | 典型站点（本次扫描） |
|---|---|
| Akamai Bot Manager | 大型电商、金融 |
| DataDome | Airbnb（本次检出） |
| PerimeterX / HUMAN | Zillow、Fiverr |
| Kasada | 部分票务、零售 |
| F5 / Shape Security | 银行、航空 |
| 瑞数 RiskRain | 国内金融、政务 |
| 连接级静默丢包（TIMEOUT） | Zealy（浏览器可访问） |

### 核心原理

上述防护系统在 **JS 运行时**采集指纹：
- Akamai：`_abck` cookie 由 `bm.js` 在浏览器内生成，包含 WebGL/Canvas/字体熵值
- DataDome：实时 ML 评分，分析鼠标轨迹、键盘节奏、滚动行为
- PerimeterX：行为基线对比，零交互即判定为 bot
- Kasada：`proof.js` 动态混淆，需在真实浏览器内执行才能生成有效 token

`curl_cffi` 不执行 JS，无论 TLS 指纹多完美都无法生成这些 token。

### 方案一：Camoufox（推荐，开源）

Camoufox 是基于 Firefox 的反检测浏览器，在 **C++ 层**注入指纹，不依赖 JS patch（JS patch 可被检测）。

```python
# pip install camoufox[geoip]
# python -m camoufox fetch  # 首次下载浏览器
from camoufox.async_api import AsyncCamoufox
import asyncio

async def fetch_tier3_camoufox(url: str, proxy: str = None) -> str:
    async with AsyncCamoufox(
        headless=True,
        geoip=True,                    # 自动匹配代理 IP 的地理位置
        proxy={"server": proxy} if proxy else None,
        os="windows",                  # 伪装 Windows 系统
        screen={"width": 1920, "height": 1080},
    ) as browser:
        page = await browser.new_page()

        # 模拟人类行为：随机延迟
        await page.goto(url, wait_until="networkidle")
        await asyncio.sleep(1.5 + __import__("random").random() * 2)

        # 模拟滚动（PerimeterX 行为检测必须）
        await page.mouse.wheel(0, 300)
        await asyncio.sleep(0.5)

        html = await page.content()
        cookies = await page.context.cookies()
        return html, {c["name"]: c["value"] for c in cookies}
```

**Camoufox 优势**：
- 开源免费，C++ 层指纹注入，JS 层无痕迹
- 内置 WebGL、Canvas、字体、AudioContext 随机化
- 支持 `geoip=True` 自动匹配代理地理位置（时区/语言/locale 一致）
- 通过 Playwright API，与现有代码兼容

### 方案二：playwright-stealth（轻量，JS patch）

```python
# pip install playwright playwright-stealth
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async

async def fetch_tier3_stealth(url: str, proxy: str = None) -> str:
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            proxy={"server": proxy} if proxy else None,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
            ],
        )
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/124.0.0.0 Safari/537.36",
            locale="zh-CN",
            timezone_id="Asia/Shanghai",
        )
        page = await context.new_page()
        await stealth_async(page)          # 注入 stealth patch

        await page.goto(url, wait_until="networkidle", timeout=30000)
        html = await page.content()
        await browser.close()
        return html
```

**注意**：`playwright-stealth` 是 JS 层 patch，对 Kasada 等强检测系统效果有限，推荐优先用 Camoufox。

### 方案三：cf_clearance Cookie 提取（Cloudflare 专用）

对于 Cloudflare 5s 挑战，可用 Playwright 一次性获取 `cf_clearance`，之后复用到 Tier 2：

```python
async def get_cf_clearance(url: str, proxy: str = None) -> str:
    """用 Playwright 通过 CF 挑战，提取 cf_clearance cookie"""
    async with AsyncCamoufox(headless=False, proxy=...) as browser:
        page = await browser.new_page()
        await page.goto(url, wait_until="networkidle")

        # 等待 CF 挑战完成（最多 30s）
        for _ in range(30):
            cookies = {c["name"]: c["value"]
                       for c in await page.context.cookies()}
            if "cf_clearance" in cookies:
                return cookies["cf_clearance"]
            await asyncio.sleep(1)

        raise TimeoutError("CF 挑战超时，未获取到 cf_clearance")
```

### 行为模拟最佳实践

```python
import random, asyncio

async def human_behavior(page):
    """模拟人类行为，降低 PerimeterX / DataDome bot 评分"""
    # 1. 随机滚动
    for _ in range(random.randint(2, 5)):
        await page.mouse.wheel(0, random.randint(100, 400))
        await asyncio.sleep(random.uniform(0.3, 1.2))

    # 2. 随机鼠标移动
    for _ in range(random.randint(3, 8)):
        x = random.randint(100, 1800)
        y = random.randint(100, 900)
        await page.mouse.move(x, y, steps=random.randint(5, 20))
        await asyncio.sleep(random.uniform(0.1, 0.5))

    # 3. 随机停留时间（模拟阅读）
    await asyncio.sleep(random.uniform(1.5, 4.0))
```

### 关键参数

| 参数 | 推荐值 | 说明 |
|---|---|---|
| 并发数 | 1–3 | 浏览器资源消耗大，且高并发触发行为检测 |
| 请求间隔 | 3–10s | DataDome/PerimeterX 对节奏极敏感 |
| IP 类型 | 住宅/移动代理 | 数据中心 IP 直接被 Akamai/DataDome 拒绝 |
| headless | `True`（Camoufox）| Camoufox 的 headless 不暴露 headless 特征 |
| 会话复用 | 必须 | 保留 localStorage / Cookie，避免重新挑战 |

---

## Tier 3 + CAPTCHA Solver

### 适用场景

Playwright 渲染后页面仍出现 CAPTCHA 弹窗（Arkose/FunCaptcha、DataDome 挑战页等）。

### 技术方案：Playwright + CapSolver 自动注入

```python
async def handle_captcha_in_browser(page, capsolver_key: str):
    """检测页面中的 CAPTCHA 并自动解题注入"""
    # 检测 Turnstile
    turnstile = await page.query_selector(".cf-turnstile")
    if turnstile:
        site_key = await turnstile.get_attribute("data-sitekey")
        token = capsolver.solve({
            "type": "AntiTurnstileTaskProxyLess",
            "websiteURL": page.url,
            "websiteKey": site_key,
        })["token"]
        await page.evaluate(
            f"document.querySelector('[name=cf-turnstile-response]').value = '{token}'"
        )

    # 检测 hCaptcha
    hcaptcha = await page.query_selector(".h-captcha")
    if hcaptcha:
        site_key = await hcaptcha.get_attribute("data-sitekey")
        token = capsolver.solve({
            "type": "HCaptchaTaskProxyLess",
            "websiteURL": page.url,
            "websiteKey": site_key,
        })["token"]
        await page.evaluate(
            f"document.querySelector('[name=h-captcha-response]').value = '{token}'"
        )
```

---

## 各 Tier 成本与速度对比

| 指标 | Tier 1 | Tier 2 | Tier 2+CAPTCHA | Tier 3 | Tier 3+CAPTCHA |
|---|---|---|---|---|---|
| **单次耗时** | 0.5–2s | 1–5s | 5–20s | 10–30s | 20–60s |
| **并发上限** | 50+ | 5–10 | 3–5 | 1–3 | 1–2 |
| **代理成本** | 数据中心（低） | 住宅（中） | 住宅（中） | 住宅/移动（高） | 住宅/移动（高） |
| **CAPTCHA 成本** | 无 | 无 | $1–1.5/1000次 | 无 | $1–1.5/1000次 |
| **浏览器资源** | 无 | 无 | 无 | 高（内存/CPU） | 高 |
| **成功率（对应防护）** | 99%+ | 85–95% | 90–98% | 70–90% | 80–95% |

---

## 与侦察结果的对接

`recon_demo.py` 输出的 `tier_verdict` 字段直接映射到执行策略：

```python
# 读取侦察结果，选择执行策略
import json

with open("recon_result.json") as f:
    recon = json.load(f)

tier = recon["tier_verdict"]           # "tier1" / "tier2" / "tier2+captcha" / "tier3" / "tier3+captcha"
need_captcha = recon["need_captcha_solver"]
antibot = recon["antibot"]             # {"Cloudflare": {"confidence": 65, ...}, ...}

if tier == "tier1":
    result = fetch_tier1(url)
elif tier == "tier2":
    result = await fetch_tier2(url, proxy=RESIDENTIAL_PROXY)
elif tier == "tier2+captcha":
    # 从 antibot 中提取 site_key（需要 Playwright 一次性获取）
    result = await fetch_with_turnstile(url, site_key=SITE_KEY)
elif "tier3" in tier:
    html, cookies = await fetch_tier3_camoufox(url, proxy=RESIDENTIAL_PROXY)
    if need_captcha:
        await handle_captcha_in_browser(page, CAPSOLVER_KEY)
```

---

## 附录：验证码开源方案实战对比

> 核心结论：开源方案只能解决**图形字符**和**简单滑块**，对主流商业 CAPTCHA 要么成功率不稳定，要么根本无法闭环。

### 各类验证码能否用开源方案闭环

| 验证码类型 | 开源能否闭环 | 推荐工具 | 成功率 | 原因 |
|---|---|---|---|---|
| 图形字符（4-6位数字/字母） | **✅ 能** | ddddocr OCR 模式 | ~95%（中等干扰） | 纯图像问题，无服务端逻辑 |
| 简单滑块（无 JS 签名校验） | **✅ 能** | ddddocr 缺口定位 + Playwright 拖拽 | ~85-90% | 只需定位 + 模拟拖拽 |
| 点选验证码（文字/图标点选） | **⚠️ 部分** | ddddocr 目标检测模式 | ~70-80% | 图像识别可行，但服务端有行为校验 |
| GeeTest v3 滑块 | **⚠️ 部分** | geetest-crack + JS 逆向 | ~85% | JS 签名可逆向，但维护成本高 |
| GeeTest v4 滑块 | **❌ 不稳定** | geetest-v4-slide-crack | ~90%（不稳定） | JS 加密每次更新就失效，需持续维护 |
| 腾讯 TCaptcha 点选 | **❌ 难** | 无可靠开源方案 | <50% | 服务端有行为验证，纯图像不够 |
| reCAPTCHA v2（图片选择） | **❌ 不行** | 无 | — | Google 服务端验证，无法纯本地破解 |
| reCAPTCHA v3（行为评分） | **❌ 不行** | 无 | — | 无可见挑战，纯行为 + 环境评分 |
| hCaptcha | **❌ 不行** | 无 | — | 同 reCAPTCHA v2 |
| Cloudflare Turnstile | **❌ 不行** | 无 | — | 无可见挑战，纯环境 + 行为检测 |
| Arkose / FunCaptcha | **❌ 不行** | 无 | — | 3D 旋转 + 服务端多轮验证 |
| 网易易盾滑块 | **⚠️ 部分** | ddddocr + 轨迹模拟 | ~75% | 缺口定位可行，轨迹加密需逆向 |
| 阿里云人机验证（NC） | **❌ 难** | 无稳定开源方案 | <60% | 服务端设备指纹 + 行为分析 |

---

### ddddocr 实际能力边界

ddddocr（GitHub 13.6k star，2026-01 仍在维护，MIT 协议）是**图像识别库**，不是"破解验证码逻辑"的工具。

**它能做的**：
- 识别图像中的文字（OCR）
- 定位图像中的目标坐标（目标检测）

**它不能做的**：
- 处理 JS 签名/加密参数
- 生成合法的鼠标轨迹数据
- 绕过服务端行为验证

```python
# pip install ddddocr
import ddddocr

# 场景一：图形字符验证码 OCR
ocr = ddddocr.DdddOcr()
with open("char_captcha.png", "rb") as f:
    result = ocr.classification(f.read())
print(result)  # "a3k9"

# 场景二：滑块缺口定位（返回缺口 x 坐标）
ocr_det = ddddocr.DdddOcr(det=False, ocr=False)
with open("bg.png", "rb") as bg, open("slider.png", "rb") as sl:
    result = ocr_det.slide_match(sl.read(), bg.read())
print(result)  # {"target": [x1, y1, x2, y2]}  缺口位置

# 场景三：点选验证码目标检测
ocr_det2 = ddddocr.DdddOcr(det=True)
with open("click_captcha.png", "rb") as f:
    poses = ocr_det2.detection(f.read())
print(poses)  # [(x1,y1,x2,y2), ...]  各点击目标坐标框
```

---

### 滑块验证码完整闭环流程（以 GeeTest v4 为例）

GeeTest v4 需要五步，ddddocr 只解决第二步：

```
步骤1：请求 GeeTest 初始化 API
        → 获取 lot_number、pow_detail、bg_img_url、slice_img_url

步骤2：图像识别缺口位置（ddddocr 负责这步）
        → 得到缺口 x 坐标（距离）

步骤3：生成人类轨迹数据
        → 模拟加速-匀速-减速曲线，加入随机抖动
        → 这步需要自己实现或 JS 逆向

步骤4：JS 参数签名（最难，也是开源方案最脆弱的地方）
        → GeeTest 对轨迹 + 环境数据进行加密
        → 每次 GeeTest 更新 JS 就失效，需要重新逆向

步骤5：提交验证，获取 pass_token
        → 服务端校验通过后返回可用 token
```

```python
# 完整滑块流程示例（步骤2+3，步骤4需要 JS 逆向或 CapSolver）
import ddddocr
import requests
import random, time

def get_slide_distance(bg_url: str, slider_url: str) -> int:
    """步骤2：用 ddddocr 定位缺口"""
    bg = requests.get(bg_url).content
    slider = requests.get(slider_url).content
    ocr = ddddocr.DdddOcr(det=False, ocr=False)
    result = ocr.slide_match(slider, bg)
    return result["target"][0]  # 缺口 x 坐标

def gen_track(distance: int) -> list:
    """步骤3：生成人类轨迹（加速-匀速-减速）"""
    track = []
    current = 0
    # 加速阶段：前 60% 距离
    mid = distance * 0.6
    t = 0.2
    v = 0
    while current < distance:
        if current < mid:
            a = 2  # 加速
        else:
            a = -3  # 减速
        v0 = v
        v = v0 + a * t
        move = v0 * t + 0.5 * a * t * t
        current += move
        # 加入随机抖动
        track.append([
            round(move + random.uniform(-1, 1), 2),
            round(random.uniform(-2, 2), 2),
            round(t * 1000)
        ])
    return track
```

---

### 开源 vs 商业 CAPTCHA Solver 选择建议

| 场景 | 推荐方案 | 理由 |
|---|---|---|
| 图形字符验证码（国内小站） | **ddddocr** 本地运行 | 免费，成功率高，无需外部依赖 |
| 简单滑块（无复杂 JS 签名） | **ddddocr + Playwright** | 免费闭环 |
| GeeTest v4 / 腾讯 TCaptcha | **CapSolver**（$1.5/1000次） | 开源方案不稳定，商业服务持续跟进 JS 更新 |
| reCAPTCHA / hCaptcha / Turnstile | **CapSolver**（$0.8-1.2/1000次） | 无可用开源方案 |
| 高频大量（>10万次/天） | **2captcha / Anti-Captcha** | 价格更低，有量折扣 |
| 极低频（<100次/天） | **CapSolver** 按需付费 | 无月费，用多少付多少 |

---

## 已知局限与降级策略

| 场景 | 问题 | 降级方案 |
|---|---|---|
| Zealy TIMEOUT | 连接级静默丢包，curl_cffi 无响应 | 直接走 Tier 3 Camoufox |
| Akamai `_abck` 失效 | token 有效期短（约 2min），高并发下频繁过期 | 每个 session 独立维护 `_abck`，定期刷新 |
| DataDome 实时 ML | 行为模式被学习后封禁 | 更换 IP + 重置 session，降低并发 |
| Kasada proof.js 更新 | 混淆 JS 每次部署都变化 | 依赖 CapSolver 云端执行（自动跟进） |
| 瑞数 RASP | 每次请求 HTML 不同，无法静态分析 | 必须 Playwright，且需等待 JS 执行完成 |

---

## 附录：全维度缓存省钱方案

> 来源：Cloudflare 官方文档、Scrapeless (Oct 2025)、Roundproxies (Dec 2025)、Browserless (Feb 2025)、Scrapfly (Sep 2025)、WebScraping.Club (Mar 2025)

缓存分为**三个完全不同的层**，每层独立，可叠加使用：

```
Layer A：验证码厂商 Token 缓存（减少解题次数）
Layer B：目标网站 Session/Cookie 缓存（减少重新登录）
Layer C：网络连接层缓存（减少代理流量和握手开销）
```

---

### Layer A：验证码 Token 缓存

#### A1. Turnstile Token 缓存（最关键）

**核心事实**（来自 Cloudflare 官方文档）：
- Turnstile 默认模式：每次 `siteverify` 验证后 token **一次性失效**
- 但 token 本身在被验证前有效期约 **300 秒（5 分钟）**
- `cf_clearance` cookie（Pre-clearance 模式）有效期由站点配置决定，通常 **30-60 分钟**，部分站点长达 **24 小时**

**两种缓存策略**：

| 策略 | 原理 | 节省比例 | 风险 |
|---|---|---|---|
| **Token 预生成池** | 提前批量解题，存入队列，按需消费 | 0%（次数不变，但并发更平滑） | token 过期浪费 |
| **cf_clearance 复用** | 解一次题获得 clearance cookie，同 IP + 同 UA 下复用 30-60min | **90%+** | IP/UA 变化立即失效 |

**cf_clearance 复用的关键约束**（来自 Scrapeless 技术文档）：
1. **必须绑定同一 IP**：换 IP 立即失效，Cloudflare 服务端校验 IP 一致性
2. **必须绑定同一 User-Agent**：UA 变化触发重新挑战
3. **必须绑定同一 TLS 指纹**：JA3 指纹不一致会被识别

```python
import time
import json
import os
from curl_cffi.requests import AsyncSession

CLEARANCE_STORE = "clearance_cache.json"

def load_cache():
    if os.path.exists(CLEARANCE_STORE):
        with open(CLEARANCE_STORE) as f:
            return json.load(f)
    return {}

def save_cache(cache):
    with open(CLEARANCE_STORE, "w") as f:
        json.dump(cache, f)

async def get_session_with_cache(account_id: str, proxy: str) -> AsyncSession:
    """
    复用 cf_clearance：同一账号 + 同一代理 IP 下，30min 内不重新解题
    """
    cache = load_cache()
    key = f"{account_id}:{proxy}"
    now = time.time()

    session = AsyncSession(impersonate="chrome124")
    session.proxies = {"https": proxy, "http": proxy}

    if key in cache and cache[key]["expires"] > now + 60:
        # 缓存有效，注入已有 cookie
        session.cookies.set(
            "cf_clearance", cache[key]["cf_clearance"],
            domain=cache[key]["domain"]
        )
        session.headers["User-Agent"] = cache[key]["user_agent"]
        return session

    # 缓存失效，需要重新过 Cloudflare 挑战
    # （此处调用 Camoufox 或 CapSolver 获取新的 cf_clearance）
    new_clearance = await solve_cloudflare_challenge(proxy)

    cache[key] = {
        "cf_clearance": new_clearance["cookie"],
        "domain": new_clearance["domain"],
        "user_agent": new_clearance["user_agent"],
        "expires": now + 1800  # 30 分钟
    }
    save_cache(cache)
    session.cookies.set("cf_clearance", new_clearance["cookie"])
    session.headers["User-Agent"] = new_clearance["user_agent"]
    return session
```

#### A2. Turnstile Pre-clearance 模式（站点支持时）

Cloudflare 官方文档说明：当站点开启 Pre-clearance 时，Turnstile 解题后会同时颁发 `cf_clearance` cookie，该 cookie 可让后续所有 WAF 规则直接放行，**无需每次解题**。

**判断站点是否支持 Pre-clearance**：
```python
# 解题后检查响应是否包含 cf_clearance
resp = await session.get(url)
has_preclearance = "cf_clearance" in resp.cookies
```

#### A3. reCAPTCHA v3 Token 缓存

**核心事实**（来自 Google 官方文档）：
- reCAPTCHA v3 token 有效期 **2 分钟**
- 每个 token 只能被 `siteverify` 验证**一次**（防重放）
- 但同一 session 内，`grecaptcha.execute()` 可以多次调用，每次返回新 token

**省钱策略**：reCAPTCHA v3 通常只在**特定操作**（登录、提交）时触发，不是每个页面都需要。识别哪些 API 端点真正校验 token，只在这些端点解题。

```python
# 只在需要提交的接口前解题，不要提前解
CAPTCHA_REQUIRED_ENDPOINTS = ["/api/login", "/api/submit-task"]

async def smart_request(url, method="GET", **kwargs):
    needs_captcha = any(ep in url for ep in CAPTCHA_REQUIRED_ENDPOINTS)
    if needs_captcha:
        token = await capsolver_solve_recaptcha_v3(url)
        kwargs.setdefault("data", {})["g-recaptcha-response"] = token
    return await session.request(method, url, **kwargs)
```

#### A4. FlareSolverr / Byparr：本地 cf_clearance 服务器

**FlareSolverr**（GitHub: FlareSolverr/FlareSolverr，12.6k stars，2026-01 仍活跃）是一个本地代理服务器，启动后：
1. 接收你的请求
2. 用内置 Chromium 自动过 Cloudflare 挑战
3. 返回 `cf_clearance` cookie 和 headers
4. **支持 session 复用**：同一 session_id 的请求共享已获取的 clearance

```python
import requests

# FlareSolverr 本地服务（Docker 启动）
FLARESOLVERR_URL = "http://localhost:8191/v1"

def get_clearance_via_flaresolverr(target_url: str, session_id: str = "default"):
    resp = requests.post(FLARESOLVERR_URL, json={
        "cmd": "request.get",
        "url": target_url,
        "session": session_id,   # 同一 session_id 复用 clearance
        "maxTimeout": 60000
    })
    data = resp.json()
    # 提取 cf_clearance cookie
    cookies = {c["name"]: c["value"] for c in data["solution"]["cookies"]}
    return cookies.get("cf_clearance"), data["solution"]["userAgent"]

# 第一次调用：解题（约 5-10 秒）
clearance, ua = get_clearance_via_flaresolverr("https://target.com", "account_001")

# 后续调用：复用 session（约 0.5 秒，不重新解题）
clearance2, ua2 = get_clearance_via_flaresolverr("https://target.com/page2", "account_001")
```

**注意**：FlareSolverr 对 Turnstile 挑战目前**无法自动解题**（官方 README 明确标注），只能处理 JS Challenge 和 Managed Challenge。

---

### Layer B：目标网站 Session / Cookie 缓存

这是**最省钱**的缓存层，和验证码无关，纯粹是避免重复登录。

#### B1. Web3 DApp JWT / localStorage Token 缓存

Web3 DApp 登录流程：钱包签名 → 后端颁发 JWT → 存入 `localStorage`。

**JWT 有效期通常 7-30 天**，只要 token 没过期，完全不需要重新走签名流程。

```python
import json
import time
import os

TOKEN_FILE = "web3_tokens.json"

def load_tokens():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE) as f:
            return json.load(f)
    return {}

def save_tokens(tokens):
    with open(TOKEN_FILE, "w") as f:
        json.dump(tokens, f, indent=2)

async def get_auth_token(wallet_address: str, sign_fn) -> str:
    """
    缓存 Web3 JWT，有效期内不重新签名
    """
    tokens = load_tokens()
    now = time.time()

    if wallet_address in tokens:
        t = tokens[wallet_address]
        # 留 1 小时余量
        if t["expires"] - now > 3600:
            return t["token"]

    # 重新登录：获取 nonce → 签名 → 换 JWT
    nonce_resp = await session.get(f"/api/nonce?address={wallet_address}")
    nonce = nonce_resp.json()["nonce"]
    signature = sign_fn(nonce)  # 钱包签名
    login_resp = await session.post("/api/login", json={
        "address": wallet_address,
        "signature": signature
    })
    jwt = login_resp.json()["token"]
    expires = now + 7 * 86400  # 假设 7 天有效期

    tokens[wallet_address] = {"token": jwt, "expires": expires}
    save_tokens(tokens)
    return jwt
```

#### B2. requests.Session 持久化（HTTP Cookie 自动管理）

```python
import pickle
import os
from curl_cffi.requests import AsyncSession

SESSION_FILE = "sessions/{account_id}.pkl"

async def get_persistent_session(account_id: str) -> AsyncSession:
    """
    持久化整个 session（包含所有 cookie），避免重复登录
    """
    path = SESSION_FILE.format(account_id=account_id)
    session = AsyncSession(impersonate="chrome124")

    if os.path.exists(path):
        with open(path, "rb") as f:
            saved = pickle.load(f)
        session.cookies.update(saved["cookies"])
        session.headers.update(saved["headers"])

    return session

async def save_session(account_id: str, session: AsyncSession):
    path = SESSION_FILE.format(account_id=account_id)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        pickle.dump({
            "cookies": dict(session.cookies),
            "headers": dict(session.headers)
        }, f)
```

#### B3. Playwright 浏览器 Profile 持久化（Tier 3 场景）

Playwright 支持 `user_data_dir` 持久化整个浏览器 profile，包含所有 cookie、localStorage、IndexedDB。

```python
from playwright.async_api import async_playwright
import os

async def get_persistent_browser_context(account_id: str):
    """
    持久化浏览器 profile：cf_clearance + JWT + 所有 cookie 全部保留
    一次登录，后续直接复用，无需重新过 Cloudflare 或重新签名
    """
    profile_dir = f"profiles/{account_id}"
    os.makedirs(profile_dir, exist_ok=True)

    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=profile_dir,
            headless=True,
            args=["--no-sandbox"],
        )
        return context
```

**节省效果**：首次登录后，后续操作完全不需要重新过 Cloudflare 或重新签名，**CAPTCHA 解题次数降为 0**（直到 cookie 过期）。

---

### Layer C：网络连接层缓存（代理流量节省）

#### C1. TCP 连接池 + Keep-Alive（减少握手开销）

来源：Scrapfly 技术文档（Sep 2025）——连接优化可减少 **60-80%** 的连接建立时间。

```python
import aiohttp
from aiohttp.connector import TCPConnector

connector = TCPConnector(
    limit=50,               # 连接池总大小
    limit_per_host=10,      # 每个目标域名最多 10 个连接
    ttl_dns_cache=300,      # DNS 缓存 5 分钟
    use_dns_cache=True,
    keepalive_timeout=30,   # 连接保活 30 秒
    enable_cleanup_closed=True,
)
session = aiohttp.ClientSession(connector=connector)
# 整个程序生命周期复用同一个 session，不要每次请求都新建
```

#### C2. 拦截无用资源（减少代理流量 30-50%）

来源：Browserless 技术博客（Feb 2025）——Session 复用 + 资源拦截可减少代理用量 **90%**。

```python
# Playwright 场景：拦截图片、CSS、字体，只加载 JS 和 API
async def setup_page_optimization(page):
    await page.route("**/*", lambda route: (
        route.abort()
        if route.request.resource_type in ["image", "stylesheet", "font", "media"]
        else route.continue_()
    ))
```

```python
# curl_cffi 场景：不加载图片（通过 Accept 头控制）
session.headers.update({
    "Accept": "application/json, text/plain, */*",  # 不接受图片
})
```

#### C3. ISP 静态代理 vs 住宅轮换代理（选型省钱）

| 代理类型 | 计费 | 适用场景 | 月费（100账号） |
|---|---|---|---|
| **住宅轮换**（Smartproxy/Oxylabs） | 按流量 $3-5/GB | 需要频繁换 IP | $15-30 |
| **ISP 静态住宅**（固定 IP） | 按 IP $2-3/IP/月 | 账号绑定固定 IP，cf_clearance 可长期复用 | $200-300 |
| **数据中心**（Hetzner/Vultr） | 按 IP $0.3/IP/月 | 无 Cloudflare 的站点 | $30 |
| **本机 IP**（家庭宽带） | $0 | 本地测试 | $0 |

**关键洞察**：`cf_clearance` 绑定 IP，如果用**住宅轮换代理**（每次请求换 IP），clearance 每次都失效，必须重新解题。用**ISP 静态代理**（固定 IP），clearance 可以复用 30-60 分钟，大幅减少解题次数。

**对于 100 账号场景**：
- 每账号分配 1 个固定 ISP IP → $200-300/月，但 CAPTCHA 解题次数降至 1次/30min
- 住宅轮换 → $15/月，但每次操作都要解题

**经济平衡点**：如果每账号每天操作 >10 次，ISP 静态代理更划算（CAPTCHA 节省 > 代理溢价）。

---

### 三层缓存叠加后的成本对比

**场景：100 账号，每账号每天 5 次操作，运行 1 个月（共 15000 次操作）**

| 方案 | CAPTCHA 解题次数 | CAPTCHA 费用 | 代理费用 | 合计/月 |
|---|---|---|---|---|
| **无缓存**（每次都解） | 15000 次 | $18 | $15（流量） | **$33** |
| **Layer A 缓存**（cf_clearance 30min 复用） | ~300 次（每账号每天 1 次） | $0.36 | $15 | **$15.4** |
| **Layer B 缓存**（JWT 7天复用 + cf_clearance） | ~100 次（每账号每周 1 次） | $0.12 | $15 | **$15.1** |
| **Layer A+B+C**（全缓存 + ISP 静态代理） | ~100 次 | $0.12 | $200（ISP） | **$200**（不划算） |
| **Layer A+B**（全缓存 + 住宅流量代理） | ~100 次 | $0.12 | $15 | **$15.1** |

**最优方案**：Layer A + Layer B，住宅流量代理，月费约 **$15-16**，比无缓存节省 **55%**。

---

### 缓存失效处理

```python
import asyncio
from typing import Optional

class CacheManager:
    """统一管理三层缓存，自动处理失效重试"""

    def __init__(self):
        self.cf_cache = {}    # Layer A: cf_clearance
        self.jwt_cache = {}   # Layer B: JWT token
        self.session_cache = {}  # Layer B: session cookies

    async def get_valid_session(self, account_id: str, proxy: str, target_url: str):
        now = time.time()

        # 1. 检查 JWT 是否有效
        jwt = self.jwt_cache.get(account_id)
        if not jwt or jwt["expires"] < now + 3600:
            jwt = await self._refresh_jwt(account_id)
            self.jwt_cache[account_id] = jwt

        # 2. 检查 cf_clearance 是否有效（绑定 IP）
        cf_key = f"{account_id}:{proxy}"
        cf = self.cf_cache.get(cf_key)
        if not cf or cf["expires"] < now + 60:
            cf = await self._refresh_clearance(proxy, target_url)
            self.cf_cache[cf_key] = cf

        # 3. 组装 session
        session = AsyncSession(impersonate="chrome124")
        session.proxies = {"https": proxy}
        session.headers["Authorization"] = f"Bearer {jwt['token']}"
        session.headers["User-Agent"] = cf["user_agent"]
        session.cookies.set("cf_clearance", cf["cookie"])
        return session

    async def _refresh_clearance(self, proxy: str, url: str) -> dict:
        # 调用 CapSolver 或 FlareSolverr 获取新 clearance
        ...

    async def _refresh_jwt(self, account_id: str) -> dict:
        # 重新钱包签名登录
        ...
```

---

## 参考资料

- WebAutomation.io, *The Ultimate Guide to Web Scraping Antibot Systems*, Oct 2025
- Scrapfly, *How to Bypass PerimeterX when Web Scraping in 2026*, Feb 2026
- Scrapeless, *Manage Cloudflare cf_clearance Cookie for Persistent Scraping*, Oct 2025
- Roundproxies, *How to scrape cf_clearance cookies in 2026: 7 working methods*, Dec 2025
- Browserless, *Cutting Proxy Usage with Reconnects*, Feb 2025
- Scrapfly, *Advanced Proxy Connection Optimization Techniques*, Sep 2025
- WebScraping.Club, *Optimizing costs for large-scale scraping operations*, Mar 2025
- Cloudflare 官方文档, *Clearance · Cloudflare challenges docs*：https://developers.cloudflare.com/cloudflare-challenges/concepts/clearance/
- FlareSolverr GitHub：https://github.com/FlareSolverr/FlareSolverr
- CapSolver 官方定价：https://docs.capsolver.com/en/pricing/
- camoufox GitHub：https://github.com/daijro/camoufox
- curl_cffi 文档：https://curl-cffi.readthedocs.io/en/stable/faq.html
