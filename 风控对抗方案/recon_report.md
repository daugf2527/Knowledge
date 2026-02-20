# Anti-Sybil 侦察报告

> 生成时间：2026-02-20 13:00  |  总目标：50 个

## 一、总览统计

| 指标 | 数值 |
|---|---|
| 总站点 | 50 |
| 成功扫描 | 46 |
| 扫描失败 | 4 |
| 🟢 Tier1（纯协议可用） | 20 |
| 🟡 Tier2（TLS指纹伪装） | 24 |
| 🟡 Tier2+CAPTCHA | 1 |
| 🔴 Tier3（Playwright DOM）| 1 |
| ⚠ P0 拦截页嫌疑 | 1 |
| 需要 CAPTCHA Solver | 2 |

## 二、防作弊工具出现频率

| 防作弊工具 | 命中次数 | 覆盖率 |
|---|---|---|
| Cloudflare | 19 | 41% |
| Vercel WAF | 8 | 17% |
| Cloudflare Turnstile | 1 | 2% |
| Fastly Shield | 1 | 2% |
| DataDome | 1 | 2% |
| 百度云盾 | 1 | 2% |
| 极验GeeTest | 1 | 2% |

## 三、Tier 分布

| Tier | 站点数 | 占比 | 说明 |
|---|---|---|---|
| 🟢 Tier1 | 20 | 43% | 直接 curl_cffi 请求即可，无需额外处理 |
| 🟡 Tier2 | 24 | 52% | 需 curl_cffi Chrome124 TLS 指纹 |
| 🟡 Tier2 | 1 | 2% | TLS 指纹 + CAPTCHA Solver |
| 🔴 Tier3 | 1 | 2% | 需 Playwright 全 DOM 渲染 |

## 四、P0 拦截页嫌疑站点

> status 非 200 且 HTML < 8KB，防作弊 JS 可能未注入，Pass 2/3 无效，需 Playwright 渲染

- `https://magiceden.io`

## 四B、FETCH_FAILED 站点说明

> ⚡ = TIMEOUT：站点浏览器可正常访问，说明服务端主动静默丢包（连接级 bot 检测），实际防护强度 ≥ Tier2，需人工复核。
> 其余错误类型说明：SSL_ERROR=证书/TLS握手失败；COOKIE_PARSE_ERROR=多域名 cookie 冲突（curl_cffi bug）；CONNECTION_ERROR=端口拒绝连接。

| 站点 | 错误类型 | 说明 |
|---|---|---|
| `app.debank.com` | `SSL_ERROR` | TLS 握手失败，需设置 `verify=False` 或更换 impersonate 版本 |
| `twitter.com` | `COOKIE_PARSE_ERROR` | curl_cffi 多域名 cookie 解析 bug，站点本身可访问，换 requests 库可绕过 |
| `www.ebay.com` | `ERR_ConnectionError` | ERR_ConnectionError |
| `www.notion.so` | `COOKIE_PARSE_ERROR` | curl_cffi 多域名 cookie 解析 bug，站点本身可访问，换 requests 库可绕过 |

## 五、扫描明细（50 站）

| # | 分类 | 域名 | Tier | 防作弊工具 | 置信度 | P0? | CAPTCHA? | 技术栈（Top3）|
|---|---|---|---|---|---|---|---|---|
| 1 | Web3-任务 | `app.galxe.com` | 🟢 Tier1 | — | — |  |  | Next.js / GA4 / Cart Functionality / Envoy / Googl |
| 2 | Web3-任务 | `zealy.io` | 🟢 Tier1 | — | — |  |  | Next.js / CloudFront / GA4 / Amazon Cloudfront / R |
| 3 | Web3-任务 | `layer3.xyz` | 🟡 Tier2 | Cloudflare | Cloudflare:50% |  |  | Next.js / GA4 / Cloudflare / React / webpack / Nod |
| 4 | Web3-任务 | `guild.xyz` | 🟡 Tier2 | Cloudflare | Cloudflare:50% |  |  | Next.js / GA4 / Cloudflare / React / webpack / Nod |
| 5 | Web3-任务 | `taskon.xyz` | 🟡 Tier2 | Cloudflare | Cloudflare:50% |  |  | GA4 / Cloudflare |
| 6 | Web3-任务 | `questn.com` | 🟡 Tier2 | Cloudflare | Cloudflare:50% |  |  | Next.js / GA4 / Cloudflare / React / webpack / Nod |
| 7 | Web3-任务 | `intract.io` | 🟡 Tier2 | Cloudflare | Cloudflare:50% |  |  | GA4 / Cloudflare / Google Font API |
| 8 | Web3-任务 | `crew3.xyz` | 🟢 Tier1 | — | — |  |  | Next.js / CloudFront / GA4 / Amazon Cloudfront / R |
| 9 | Web3-任务 | `rabbithole.gg` | 🟡 Tier2 | Vercel WAF | Vercel WAF:25% |  |  | Next.js / Vercel / GA4 / React / webpack / Node.js |
| 10 | Web3-任务 | `app.debank.com` | 🔴 Tier3❌ FETCH_FAILED[SSL_ERROR] | — | — | ⚠ |  | — |
| 11 | Web3-DeFi | `app.uniswap.org` | 🟡 Tier2 | Cloudflare<br>Cloudflare Turnstile | Cloudflare:65%<br>Cloudflare Turnstile:40% |  | ✓ | Cloudflare |
| 12 | Web3-DeFi | `app.aave.com` | 🟡 Tier2 | Cloudflare<br>Vercel WAF | Cloudflare:50%<br>Vercel WAF:25% |  |  | Next.js / Vercel / Cloudflare / Vercel |
| 13 | Web3-DeFi | `app.compound.finance` | 🟡 Tier2 | Cloudflare | Cloudflare:50% |  |  | Cloudflare |
| 14 | Web3-DeFi | `app.1inch.io` | 🟡 Tier2 | Cloudflare | Cloudflare:50% |  |  | GA4 / Intercom / Cloudflare / Angular |
| 15 | Web3-DeFi | `stargate.finance` | 🟡 Tier2 | Vercel WAF | Vercel WAF:25% |  |  | Next.js / Vercel / GA4 / Google Font API / Vercel |
| 16 | Web3-DeFi | `curve.fi` | 🟡 Tier2 | Cloudflare<br>Vercel WAF | Cloudflare:50%<br>Vercel WAF:25% |  |  | Vercel / Cloudflare / Vercel / jsDelivr |
| 17 | Web3-NFT | `opensea.io` | 🟡 Tier2 | Cloudflare | Cloudflare:50% |  |  | Cloudflare |
| 18 | Web3-NFT | `blur.io` | 🟡 Tier2 | Vercel WAF | Vercel WAF:25% |  |  | Next.js / Vercel / GA4 / Vercel |
| 19 | Web3-NFT | `magiceden.io` | 🟡 Tier2 | Cloudflare | Cloudflare:50% | ⚠ |  | Cloudflare |
| 20 | Web3-NFT | `rarible.com` | 🟡 Tier2 | Cloudflare | Cloudflare:50% |  |  | Next.js / GA4 / Cloudflare / React / webpack / Nod |
| 21 | Web3-L2 | `zksync.io` | 🟡 Tier2 | Vercel WAF | Vercel WAF:25% |  |  | Next.js / Vercel / GA4 / React / Vercel |
| 22 | Web3-L2 | `linea.build` | 🟡 Tier2 | Cloudflare<br>Fastly Shield | Cloudflare:50%<br>Fastly Shield:25% |  |  | Next.js / Fastly CDN / GA4 / Cloudflare / Contentf |
| 23 | Web3-L2 | `scroll.io` | 🟡 Tier2 | Cloudflare<br>Vercel WAF | Cloudflare:50%<br>Vercel WAF:25% |  |  | Next.js / Vercel / GA4 / Cloudflare / Vercel |
| 24 | Web3-L2 | `www.optimism.io` | 🟡 Tier2 | Cloudflare | Cloudflare:50% |  |  | GA4 / Segment / Mixpanel / Cloudflare |
| 25 | Web3-L2 | `arbitrum.io` | 🟡 Tier2 | Cloudflare<br>Vercel WAF | Cloudflare:50%<br>Vercel WAF:25% |  |  | Next.js / Vercel / GA4 / Cloudflare / Vercel |
| 26 | Web2-社交 | `github.com` | 🟢 Tier1 | — | — |  |  | GA4 / React / Contentful / Ruby on Rails / GitHub  |
| 27 | Web2-社交 | `www.reddit.com` | 🟢 Tier1 | — | — |  |  | GA4 / Varnish |
| 28 | Web2-社交 | `discord.com` | 🟡 Tier2 | Cloudflare | Cloudflare:50% |  |  | GA4 / Cloudflare / Google Font API / jQuery / Webf |
| 29 | Web2-社交 | `twitter.com` | 🔴 Tier3❌ FETCH_FAILED[COOKIE_PARSE_ERROR] | — | — | ⚠ |  | — |
| 30 | Web2-社交 | `www.linkedin.com` | 🟢 Tier1 | — | — |  |  | GA4 |
| 31 | Web2-社交 | `www.twitch.tv` | 🟢 Tier1 | — | — |  |  | GA4 |
| 32 | Web2-电商 | `www.amazon.com` | 🟢 Tier1 | — | — |  |  | CloudFront / Amazon Cloudfront / Amazon Web Servic |
| 33 | Web2-电商 | `www.shopify.com` | 🟡 Tier2 | Cloudflare | Cloudflare:50% |  |  | Shopify / GA4 / Cloudflare / Cart Functionality |
| 34 | Web2-电商 | `www.ebay.com` | 🔴 Tier3❌ FETCH_FAILED[ERR_ConnectionError] | — | — | ⚠ |  | — |
| 35 | Web2-电商 | `store.steampowered.com` | 🟢 Tier1 | — | — |  |  | Nginx / jQuery / Nginx |
| 36 | Web2-旅游 | `www.booking.com` | 🟢 Tier1 | — | — |  |  | CloudFront / Amazon Cloudfront / Amazon Web Servic |
| 37 | Web2-旅游 | `airbnb.com` | 🔴 Tier3 | DataDome | DataDome:20% |  |  | Nginx / GA4 / Ruby on Rails / Envoy / Ruby / Nginx |
| 38 | Web2-流媒 | `www.netflix.com` | 🟢 Tier1 | — | — |  |  | GA4 / Zipkin / Envoy / OneTrust |
| 39 | Web2-企业 | `stripe.com` | 🟢 Tier1 | — | — |  |  | Next.js / Nginx / GA4 / Cart Functionality / Nginx |
| 40 | Web2-国内 | `www.baidu.com` | 🟡 Tier2 | 百度云盾 | 百度云盾:20% |  |  | GA4 / Vue.js / jQuery |
| 41 | Web2-国内 | `www.taobao.com` | 🟢 Tier1 | — | — |  |  | Fastly CDN / Tengine |
| 42 | Web2-国内 | `www.jd.com` | 🟢 Tier1 | — | — |  |  | Nginx / GA4 / Cart Functionality / jQuery / Nginx |
| 43 | Web2-国内 | `www.bilibili.com` | 🟡 Tier2 | 极验GeeTest | 极验GeeTest:40% |  | ✓ | GA4 / Vue.js |
| 44 | Web2-国内 | `www.zhihu.com` | 🟢 Tier1 | — | — |  |  | GA4 / Baidu Analytics (百度统计) |
| 45 | Web2-国内 | `www.weibo.com` | 🟢 Tier1 | — | — |  |  | Nginx / Nginx |
| 46 | Web2-国内 | `www.163.com` | 🟢 Tier1 | — | — |  |  | Fastly CDN / Tengine / jQuery |
| 47 | Web2-国内 | `www.douban.com` | 🟢 Tier1 | — | — |  |  | jQuery |
| 48 | Web2-国内 | `www.qq.com` | 🟢 Tier1 | — | — |  |  | React |
| 49 | Web2-国内 | `www.tiktok.com` | 🟢 Tier1 | — | — |  |  | Nginx / GA4 / React / Nginx |
| 50 | Web2-企业 | `www.notion.so` | 🔴 Tier3❌ FETCH_FAILED[COOKIE_PARSE_ERROR] | — | — | ⚠ |  | — |

## 六、关键结论

1. **Cloudflare 是最主流的防护方案**：本次扫描命中 19 个站点（41%），
   其中 1 个同时部署了 Turnstile CAPTCHA。
   → 统一对策：`curl_cffi` Chrome124 TLS 指纹 + CapSolver Turnstile 解题。

2. **25 个站点（54%）处于 Tier2**，可通过 TLS 指纹伪装绕过，
   无需 Playwright，成本最低。

3. **1 个站点触发 P0 拦截**（magiceden.io），
   静态扫描完全失效，必须使用 Playwright 渲染完整 DOM 后再次侦察。

4. **国内站点特征**：百度/淘宝/京东等存在阿里云 WAF / 腾讯天御签名，
   cookie 中含 `acw_tc` / `BAIDUID` / `ptcz` 等标志位，Tier2 基本可过，极少数需 Tier3。

5. **Web3 任务平台梯度防护**：
   - Galxe / Crew3：静态扫描无防作弊信号 → Tier1 直打 API。
   - **Zealy**：静态扫描拿不到响应（TIMEOUT ⚡），浏览器可访问 → 存在连接级 bot 检测，实际防护 ≥ Tier2，**不应直接使用 Tier1 策略**。
   - Layer3 / Guild / Taskon / Questn / Intract：Cloudflare WAF → Tier2 TLS 指纹。
   - Uniswap：Cloudflare + Turnstile（API 脚本已确认）→ Tier2 + CAPTCHA Solver。
