# ⚡ Neon B2B Live Open-Data MCP Suite (`v3.2`)

[![Live Portal](https://img.shields.io/badge/Live_Portal-Neon_MCP_Hub-0284c7?style=flat-square)](https://zhuangruoxiong-cpu.github.io/neon-mcp-hub/)
[![MCP Protocol](https://img.shields.io/badge/MCP-2024--11--05-10b981?style=flat-square)](https://modelcontextprotocol.io/)
[![Zero Dependencies](https://img.shields.io/badge/Python_3.10+-Zero_Pip_Deps-6366f1?style=flat-square)](./neon_mcp_server.py)
[![License: MIT](https://img.shields.io/badge/License-MIT-f59e0b?style=flat-square)](./LICENSE)

**20 Pay-Per-Event B2B & Regulatory Model Context Protocol (MCP) Servers** — featuring **10 Live Official-API Flagships** (SEC EDGAR, US OpenFDA, USITC HTS Tariffs, World Bank Procurement, NIH ClinicalTrials.gov, Google DNS-over-HTTPS, CoinGecko, GitHub Releases, Remotive, Apple App Store) plus **10 Structured B2B Document Parsers**.

🌐 **Interactive Sandbox & Free Invoice-to-CSV Tool**: [https://zhuangruoxiong-cpu.github.io/neon-mcp-hub/](https://zhuangruoxiong-cpu.github.io/neon-mcp-hub/)

---

## 🚀 Quickstart Option A: Zero-Install Hosted Cloud MCP (Claude Desktop / Cursor / Windsurf)

Connect directly to any of our cloud-hosted Pay-Per-Event MCP servers on Apify (`$0.005–$0.050` per structured record, **zero monthly subscription**, free `$5/mo` Apify starter credit included):

```json
{
  "mcpServers": {
    "neon-b2b-flagships": {
      "url": "https://mcp.apify.com/?actors=veteran_steam_iyn/niche-sec-edgar-10k-kpi-mcp,veteran_steam_iyn/niche-fda-drug-recall-mcp,veteran_steam_iyn/niche-customs-hscode-tariff-mcp,veteran_steam_iyn/niche-public-tender-patent-mcp,veteran_steam_iyn/niche-clinical-trial-grant-mcp",
      "headers": {
        "Authorization": "Bearer YOUR_APIFY_TOKEN"
      }
    }
  }
}
```

## 💻 Quickstart Option B: Zero-Dependency Local Open-Core Stdio Server

`neon_mcp_server.py` runs on **pure Python 3.10+ standard library** (`0` external packages required).
- **Free Local Preview Mode** (no token needed): Queries official public APIs directly (`<= 3` items/call).
- **Cloud Pro Batch Mode** (set `APIFY_TOKEN`): Automatically scales batch queries up to `50` schema-validated records per call on Apify Cloud.

```bash
# Install & run instantly via uvx or git clone:
uvx --from git+https://github.com/zhuangruoxiong-cpu/neon-mcp-hub neon-b2b-mcp
```

Or add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "neon-b2b-local": {
      "command": "python3",
      "args": ["/path/to/neon-mcp-hub/neon_mcp_server.py"],
      "env": {
        "APIFY_TOKEN": "OPTIONAL_FOR_BATCH_SCALE"
      }
    }
  }
}
```

---

## 🔥 10 Live Official-API Flagship MCP Servers

| # | MCP Tool / Actor Slug | Official Real-Time Data Source | Price / Event | Docs |
|---|---|---|---|---|
| 1 | `niche-sec-edgar-10k-kpi-mcp` | **SEC EDGAR** Official Submissions API (`10-K/10-Q/8-K`) | `$0.045` | [Spec](https://zhuangruoxiong-cpu.github.io/neon-mcp-hub/actors/niche-sec-edgar-10k-kpi-mcp.html) |
| 2 | `niche-fda-drug-recall-mcp` | **US OpenFDA** Enforcement API (`Drug/Food/Device`) | `$0.035` | [Spec](https://zhuangruoxiong-cpu.github.io/neon-mcp-hub/actors/niche-fda-drug-recall-mcp.html) |
| 3 | `niche-customs-hscode-tariff-mcp` | **USITC** Official Harmonized Tariff Schedule (`HTS`) | `$0.035` | [Spec](https://zhuangruoxiong-cpu.github.io/neon-mcp-hub/actors/niche-customs-hscode-tariff-mcp.html) |
| 4 | `niche-public-tender-patent-mcp` | **World Bank** Global Public Procurement Notices API | `$0.050` | [Spec](https://zhuangruoxiong-cpu.github.io/neon-mcp-hub/actors/niche-public-tender-patent-mcp.html) |
| 5 | `niche-clinical-trial-grant-mcp` | **NIH ClinicalTrials.gov** Official REST API v2 | `$0.030` | [Spec](https://zhuangruoxiong-cpu.github.io/neon-mcp-hub/actors/niche-clinical-trial-grant-mcp.html) |
| 6 | `niche-domain-whois-dns-mcp` | **Google DNS-over-HTTPS** Live SPF/DMARC Resolver | `$0.015` | [Spec](https://zhuangruoxiong-cpu.github.io/neon-mcp-hub/actors/niche-domain-whois-dns-mcp.html) |
| 7 | `niche-crypto-token-unlock-mcp` | **CoinGecko** Live Markets & Supply Overhang API | `$0.030` | [Spec](https://zhuangruoxiong-cpu.github.io/neon-mcp-hub/actors/niche-crypto-token-unlock-mcp.html) |
| 8 | `niche-saas-changelog-diff-mcp` | **GitHub** Official Software Releases Diff API | `$0.015` | [Spec](https://zhuangruoxiong-cpu.github.io/neon-mcp-hub/actors/niche-saas-changelog-diff-mcp.html) |
| 9 | `niche-job-salary-comp-mcp` | **Remotive** Live Remote Tech Jobs & Salary API | `$0.020` | [Spec](https://zhuangruoxiong-cpu.github.io/neon-mcp-hub/actors/niche-job-salary-comp-mcp.html) |
| 10 | `niche-appstore-churn-signal-mcp` | **Apple App Store** Official Customer Reviews JSON API | `$0.020` | [Spec](https://zhuangruoxiong-cpu.github.io/neon-mcp-hub/actors/niche-appstore-churn-signal-mcp.html) |

Plus **10 Hybrid URL + Text B2B Structured Parsers** (`niche-tradeshow-exhibitor-mcp`, `niche-crossborder-review-cleaner`, `niche-saas-pricing-table-mcp`, `niche-commercial-permit-lead-mcp`, `niche-freight-bol-manifest-mcp`, `niche-eu-carbon-cbam-mcp`, `niche-b2b-rfp-compliance-mcp`, `niche-patent-prior-art-mcp`, `niche-esg-scope3-vendor-mcp`, `niche-real-estate-auction-mcp`) — see [llms-full.txt](https://zhuangruoxiong-cpu.github.io/neon-mcp-hub/llms-full.txt) for full schemas.
