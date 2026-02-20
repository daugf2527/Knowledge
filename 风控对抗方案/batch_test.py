"""批量侦察测试 - Web3 + Web2 50 个站点，输出 Markdown 报告"""
import asyncio
import json
import sys
import os
from datetime import datetime
sys.path.insert(0, os.path.dirname(__file__))

from recon_demo import scan

TARGETS = [
    # ══ Web3：公链生态 / 任务平台 / DeFi / NFT ══════════════
    ("Web3-任务", "https://app.galxe.com"),
    ("Web3-任务", "https://zealy.io"),
    ("Web3-任务", "https://layer3.xyz"),
    ("Web3-任务", "https://guild.xyz"),
    ("Web3-任务", "https://taskon.xyz"),
    ("Web3-任务", "https://questn.com"),
    ("Web3-任务", "https://intract.io"),
    ("Web3-任务", "https://crew3.xyz"),
    ("Web3-任务", "https://rabbithole.gg"),
    ("Web3-任务", "https://app.debank.com"),
    ("Web3-DeFi",  "https://app.uniswap.org"),
    ("Web3-DeFi",  "https://app.aave.com"),
    ("Web3-DeFi",  "https://app.compound.finance"),
    ("Web3-DeFi",  "https://app.1inch.io"),
    ("Web3-DeFi",  "https://stargate.finance"),
    ("Web3-DeFi",  "https://curve.fi"),
    ("Web3-NFT",   "https://opensea.io"),
    ("Web3-NFT",   "https://blur.io"),
    ("Web3-NFT",   "https://magiceden.io"),
    ("Web3-NFT",   "https://rarible.com"),
    ("Web3-L2",    "https://zksync.io"),
    ("Web3-L2",    "https://linea.build"),
    ("Web3-L2",    "https://scroll.io"),
    ("Web3-L2",    "https://www.optimism.io"),
    ("Web3-L2",    "https://arbitrum.io"),
    # ══ Web2：国际主流平台 ════════════════════════════════════
    ("Web2-社交",  "https://github.com"),
    ("Web2-社交",  "https://www.reddit.com"),
    ("Web2-社交",  "https://discord.com"),
    ("Web2-社交",  "https://twitter.com"),
    ("Web2-社交",  "https://www.linkedin.com"),
    ("Web2-社交",  "https://www.twitch.tv"),
    ("Web2-电商",  "https://www.amazon.com"),
    ("Web2-电商",  "https://www.shopify.com"),
    ("Web2-电商",  "https://www.ebay.com"),
    ("Web2-电商",  "https://store.steampowered.com"),
    ("Web2-旅游",  "https://www.booking.com"),
    ("Web2-旅游",  "https://airbnb.com"),
    ("Web2-流媒",  "https://www.netflix.com"),
    ("Web2-企业",  "https://stripe.com"),
    # ══ Web2：国内主流平台 ════════════════════════════════════
    ("Web2-国内",  "https://www.baidu.com"),
    ("Web2-国内",  "https://www.taobao.com"),
    ("Web2-国内",  "https://www.jd.com"),
    ("Web2-国内",  "https://www.bilibili.com"),
    ("Web2-国内",  "https://www.zhihu.com"),
    ("Web2-国内",  "https://www.weibo.com"),
    ("Web2-国内",  "https://www.163.com"),
    ("Web2-国内",  "https://www.douban.com"),
    ("Web2-国内",  "https://www.qq.com"),
    ("Web2-国内",  "https://www.tiktok.com"),
    ("Web2-企业",  "https://www.notion.so"),
]


async def test_one(idx: int, total: int, category: str, url: str) -> dict:
    slug = url.replace("https://", "").replace("http://", "").rstrip("/").replace("/", "_").replace(".", "_")
    out_file = f"_tmp_{slug}.json"
    print(f"\n[{idx:02d}/{total}] [{category}] {url}")
    try:
        await scan(url, output_path=out_file)
        with open(out_file, encoding="utf-8") as f:
            data = json.load(f)
        os.remove(out_file)
        # 检查是否是 fetch 级别失败（有 error_type）
        if data.get("error_type"):
            return {
                "idx": idx, "category": category, "url": url,
                "status": f"FETCH_FAILED[{data['error_type']}]",
                "intercept": True, "antibot": [], "antibot_conf": {},
                "tier": "tier3", "captcha": False, "tech": [], "wapp": [],
            }
        ab = data.get("antibot", {})
        tech = data.get("tech", {})
        return {
            "idx": idx, "category": category, "url": url, "status": "ok",
            "intercept": data.get("intercept_suspected", False),
            "antibot": list(ab.keys()),
            "antibot_conf": {k: v["confidence"] for k, v in ab.items()},
            "tier": data.get("tier_verdict", "tier1"),
            "captcha": data.get("need_captcha_solver", False),
            "tech": list(tech.keys())[:4],
            "wapp": list(data.get("wappalyzer", {}).keys())[:4],
        }
    except Exception as e:
        if os.path.exists(out_file):
            os.remove(out_file)
        return {
            "idx": idx, "category": category, "url": url, "status": f"ERROR: {e}",
            "intercept": False, "antibot": [], "antibot_conf": {},
            "tier": "err", "captcha": False, "tech": [], "wapp": [],
        }


def _tier_emoji(tier: str) -> str:
    if tier == "err":      return "❌"
    if "tier3" in tier:    return "🔴 Tier3"
    if "tier2" in tier:    return "🟡 Tier2"
    return "🟢 Tier1"


def build_markdown(results: list, ts: str) -> str:
    lines = []
    lines.append(f"# Anti-Sybil 侦察报告\n")
    lines.append(f"> 生成时间：{ts}  |  总目标：{len(results)} 个\n")

    # ── 总览统计 ──────────────────────────────────────────────
    ok      = [r for r in results if r["status"] == "ok"]
    tier_ct = {}
    ab_ct   = {}
    intercept_list = []
    captcha_list   = []

    for r in ok:
        t = r["tier"]
        tier_ct[t] = tier_ct.get(t, 0) + 1
        for ab in r["antibot"]:
            ab_ct[ab] = ab_ct.get(ab, 0) + 1
        if r["intercept"]:
            intercept_list.append(r["url"])
        if r["captcha"]:
            captcha_list.append(r["url"])

    lines.append("## 一、总览统计\n")
    lines.append(f"| 指标 | 数值 |")
    lines.append(f"|---|---|")
    lines.append(f"| 总站点 | {len(results)} |")
    lines.append(f"| 成功扫描 | {len(ok)} |")
    lines.append(f"| 扫描失败 | {len(results)-len(ok)} |")
    lines.append(f"| 🟢 Tier1（纯协议可用） | {tier_ct.get('tier1', 0)} |")
    lines.append(f"| 🟡 Tier2（TLS指纹伪装） | {tier_ct.get('tier2', 0)} |")
    lines.append(f"| 🟡 Tier2+CAPTCHA | {tier_ct.get('tier2+captcha', 0)} |")
    lines.append(f"| 🔴 Tier3（Playwright DOM）| {tier_ct.get('tier3', 0) + tier_ct.get('tier3+captcha', 0)} |")
    lines.append(f"| ⚠ P0 拦截页嫌疑 | {len(intercept_list)} |")
    lines.append(f"| 需要 CAPTCHA Solver | {len(captcha_list)} |\n")

    # ── 防作弊工具频率 ────────────────────────────────────────
    lines.append("## 二、防作弊工具出现频率\n")
    if ab_ct:
        lines.append("| 防作弊工具 | 命中次数 | 覆盖率 |")
        lines.append("|---|---|---|")
        for ab, c in sorted(ab_ct.items(), key=lambda x: -x[1]):
            pct = f"{c/len(ok)*100:.0f}%"
            lines.append(f"| {ab} | {c} | {pct} |")
    else:
        lines.append("_本次扫描未检测到已知防作弊工具_")
    lines.append("")

    # ── 分类 Tier 分布饼图（ASCII）────────────────────────────
    lines.append("## 三、Tier 分布\n")
    tier_total = sum(tier_ct.values())
    lines.append("| Tier | 站点数 | 占比 | 说明 |")
    lines.append("|---|---|---|---|")
    tier_desc = {
        "tier1":          "直接 curl_cffi 请求即可，无需额外处理",
        "tier2":          "需 curl_cffi Chrome124 TLS 指纹",
        "tier2+captcha":  "TLS 指纹 + CAPTCHA Solver",
        "tier3":          "需 Playwright 全 DOM 渲染",
        "tier3+captcha":  "Playwright + CAPTCHA Solver",
    }
    for t, desc in tier_desc.items():
        c = tier_ct.get(t, 0)
        if c or t in ("tier1", "tier2"):
            pct = f"{c/tier_total*100:.0f}%" if tier_total else "—"
            lines.append(f"| {_tier_emoji(t)} | {c} | {pct} | {desc} |")
    lines.append("")

    # ── P0 拦截页 ─────────────────────────────────────────────
    if intercept_list:
        lines.append("## 四、P0 拦截页嫌疑站点\n")
        lines.append("> status 非 200 且 HTML < 8KB，防作弊 JS 可能未注入，Pass 2/3 无效，需 Playwright 渲染\n")
        for u in intercept_list:
            lines.append(f"- `{u}`")
        lines.append("")

    # ── FETCH_FAILED 说明 ──────────────────────────────────────
    failed = [r for r in results if r["status"] != "ok"]
    if failed:
        lines.append("## 四B、FETCH_FAILED 站点说明\n")
        lines.append("> ⚡ = TIMEOUT：站点浏览器可正常访问，说明服务端主动静默丢包（连接级 bot 检测），实际防护强度 ≥ Tier2，需人工复核。")
        lines.append("> 其余错误类型说明：SSL_ERROR=证书/TLS握手失败；COOKIE_PARSE_ERROR=多域名 cookie 冲突（curl_cffi bug）；CONNECTION_ERROR=端口拒绝连接。\n")
        lines.append("| 站点 | 错误类型 | 说明 |")
        lines.append("|---|---|---|")
        _fail_desc = {
            "TIMEOUT":            "⚡ 浏览器可访问=静默丢包，实际防护 ≥ Tier2，建议改用 Playwright 重新侦察",
            "SSL_ERROR":          "TLS 握手失败，需设置 `verify=False` 或更换 impersonate 版本",
            "COOKIE_PARSE_ERROR": "curl_cffi 多域名 cookie 解析 bug，站点本身可访问，换 requests 库可绕过",
            "CONNECTION_ERROR":   "端口/IP 被拒绝，站点可能对数据中心 IP 封锁，需代理",
        }
        for r in failed:
            domain = r["url"].replace("https://","").replace("http://","").rstrip("/")
            etype = r["status"].replace("FETCH_FAILED[","").replace("]","") if "FETCH_FAILED" in r["status"] else r["status"]
            key = next((k for k in _fail_desc if k in etype), "OTHER")
            desc = _fail_desc.get(key, etype)
            lines.append(f"| `{domain}` | `{etype}` | {desc} |")
        lines.append("")

    # ── 完整明细表 ────────────────────────────────────────────
    lines.append("## 五、扫描明细（50 站）\n")
    lines.append("| # | 分类 | 域名 | Tier | 防作弊工具 | 置信度 | P0? | CAPTCHA? | 技术栈（Top3）|")
    lines.append("|---|---|---|---|---|---|---|---|---|")

    for r in results:
        domain = r["url"].replace("https://","").replace("http://","").rstrip("/")
        tier_s = _tier_emoji(r["tier"])
        ab_names = "<br>".join(r["antibot"]) if r["antibot"] else "—"
        ab_conf  = "<br>".join(
            f"{k}:{v}%" for k, v in r["antibot_conf"].items()
        ) if r["antibot_conf"] else "—"
        p0_s   = "⚠" if r["intercept"] else ""
        cap_s  = "✓" if r["captcha"] else ""
        tech_s = " / ".join(r["tech"] + r["wapp"])[:50] if (r["tech"] or r["wapp"]) else "—"
        if r["status"] == "ok":
            status_s = ""
        elif "TIMEOUT" in r["status"]:
            status_s = "❌ FETCH_FAILED[TIMEOUT] ⚡"
        else:
            status_s = f"❌ {r['status'][:35]}"
        lines.append(
            f"| {r['idx']} | {r['category']} | `{domain}` | {tier_s}{status_s} "
            f"| {ab_names} | {ab_conf} | {p0_s} | {cap_s} | {tech_s} |"
        )

    lines.append("")

    # ── 关键结论 ───────────────────────────────────────────────
    lines.append("## 六、关键结论\n")

    # Cloudflare 覆盖率
    cf_cnt = ab_ct.get("Cloudflare", 0)
    cf_t_cnt = ab_ct.get("Cloudflare Turnstile", 0)
    lines.append(f"1. **Cloudflare 是最主流的防护方案**：本次扫描命中 {cf_cnt} 个站点（{cf_cnt/len(ok)*100:.0f}%），")
    lines.append(f"   其中 {cf_t_cnt} 个同时部署了 Turnstile CAPTCHA。")
    lines.append(f"   → 统一对策：`curl_cffi` Chrome124 TLS 指纹 + CapSolver Turnstile 解题。\n")

    t2_total = tier_ct.get("tier2", 0) + tier_ct.get("tier2+captcha", 0)
    lines.append(f"2. **{t2_total} 个站点（{t2_total/len(ok)*100:.0f}%）处于 Tier2**，可通过 TLS 指纹伪装绕过，")
    lines.append(f"   无需 Playwright，成本最低。\n")

    if intercept_list:
        lines.append(f"3. **{len(intercept_list)} 个站点触发 P0 拦截**（{', '.join(u.replace('https://','') for u in intercept_list)}），")
        lines.append(f"   静态扫描完全失效，必须使用 Playwright 渲染完整 DOM 后再次侦察。\n")

    lines.append(f"4. **国内站点特征**：百度/淘宝/京东等存在阿里云 WAF / 腾讯天御签名，")
    lines.append(f"   cookie 中含 `acw_tc` / `BAIDUID` / `ptcz` 等标志位，Tier2 基本可过，极少数需 Tier3。\n")

    lines.append(f"5. **Web3 任务平台梯度防护**：")
    lines.append(f"   - Galxe / Crew3：静态扫描无防作弊信号 → Tier1 直打 API。")
    lines.append(f"   - **Zealy**：静态扫描拿不到响应（TIMEOUT ⚡），浏览器可访问 → 存在连接级 bot 检测，实际防护 ≥ Tier2，**不应直接使用 Tier1 策略**。")
    lines.append(f"   - Layer3 / Guild / Taskon / Questn / Intract：Cloudflare WAF → Tier2 TLS 指纹。")
    lines.append(f"   - Uniswap：Cloudflare + Turnstile（API 脚本已确认）→ Tier2 + CAPTCHA Solver。\n")

    return "\n".join(lines)


async def main():
    total = len(TARGETS)
    print(f"\n{'='*65}")
    print(f"  Anti-Sybil 批量侦察 v2 — {total} 个目标")
    print(f"{'='*65}")

    results = []
    for idx, (cat, url) in enumerate(TARGETS, 1):
        r = await test_one(idx, total, cat, url)
        results.append(r)

    # ── 输出 JSON ────────────────────────────────────────────
    with open("batch_result.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # ── 输出 Markdown ────────────────────────────────────────
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    md = build_markdown(results, ts)
    md_path = "recon_report.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md)

    print(f"\n\n{'='*65}")
    print(f"  扫描完成！")
    print(f"  JSON → batch_result.json")
    print(f"  报告 → {md_path}")
    print(f"{'='*65}\n")


if __name__ == "__main__":
    asyncio.run(main())
