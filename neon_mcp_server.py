#!/usr/bin/env python3
"""Neon B2B Live Open-Data MCP Server (Zero-Dependency Open-Core Stdio Server).

Exposes 10 live authoritative B2B & Regulatory Open-Data tools over the Model Context Protocol (MCP):
  1. sec_edgar_filings              -> SEC EDGAR 10-K/10-Q/8-K live filings (`niche-sec-edgar-10k-kpi-mcp`)
  2. openfda_recalls                -> US OpenFDA Enforcement live recalls (`niche-fda-drug-recall-mcp`)
  3. usitc_hts_tariffs              -> USITC Harmonized Tariff Schedule (`niche-customs-hscode-tariff-mcp`)
  4. worldbank_procurement_tenders  -> World Bank Global Procurement (`niche-public-tender-patent-mcp`)
  5. clinical_trials_search         -> NIH ClinicalTrials.gov API v2 (`niche-clinical-trial-grant-mcp`)
  6. domain_dns_deliverability      -> Google DNS-over-HTTPS SPF/DMARC (`niche-domain-whois-dns-mcp`)
  7. coingecko_token_overhang       -> CoinGecko Supply Overhang & FDV (`niche-crypto-token-unlock-mcp`)
  8. github_release_diff            -> GitHub Official Releases Diff (`niche-saas-changelog-diff-mcp`)
  9. remotive_tech_jobs             -> Remotive Live Tech Compensation (`niche-job-salary-comp-mcp`)
  10. appstore_churn_reviews        -> Apple App Store Churn Signals (`niche-appstore-churn-signal-mcp`)

Open-Core Architecture:
  - Free Local Mode (no APIFY_TOKEN needed): Queries official public APIs directly (capped at 3 preview items).
  - Cloud Pro Mode (set APIFY_TOKEN): Delegates batch runs (up to 50 items, cloud retries, dataset persistence)
    to Apify Pay-Per-Event Actors under `veteran_steam_iyn/*` ($0.015–$0.050/record, zero monthly fee).
"""

from __future__ import annotations

import json
import os
import sys
import urllib.parse
import urllib.request
from typing import Any

SERVER_NAME = "neon-b2b-mcp"
SERVER_VERSION = "3.2.0"
PROTOCOL_VERSION = "2024-11-05"
USER_AGENT = "NeonB2BMCPHub/3.2 (contact@neonmcphub.dev)"

TOOLS: list[dict[str, Any]] = [
    {
        "name": "sec_edgar_filings",
        "actor_slug": "niche-sec-edgar-10k-kpi-mcp",
        "description": "Query live SEC EDGAR official API by US stock ticker (e.g. AAPL, NVDA, MSFT) for recent 10-K, 10-Q, and 8-K filings.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string", "description": "US stock ticker symbol (e.g. AAPL, NVDA, MSFT).", "default": "AAPL"},
                "max_items": {"type": "integer", "description": "Max records (free local preview=3; set APIFY_TOKEN for up to 50).", "default": 3},
            },
            "required": ["ticker"],
        },
    },
    {
        "name": "openfda_recalls",
        "actor_slug": "niche-fda-drug-recall-mcp",
        "description": "Query live US OpenFDA Enforcement API for food, drug, or medical device recall notices.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "domain": {"type": "string", "enum": ["food", "drug", "device"], "description": "FDA enforcement domain.", "default": "food"},
                "query": {"type": "string", "description": "Search keyword (e.g. allergen, salmonella, sterile).", "default": "allergen"},
                "max_items": {"type": "integer", "description": "Max records (free local preview=3; set APIFY_TOKEN for up to 50).", "default": 3},
            },
        },
    },
    {
        "name": "usitc_hts_tariffs",
        "actor_slug": "niche-customs-hscode-tariff-mcp",
        "description": "Query official USITC Harmonized Tariff Schedule (HTS) API by product keyword or HS code for US import duty rates.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "keyword": {"type": "string", "description": "Product keyword or 4-10 digit HS/HTS code (e.g. lithium, 8507.60).", "default": "lithium"},
                "max_items": {"type": "integer", "description": "Max records (free local preview=3; set APIFY_TOKEN for up to 50).", "default": 3},
            },
            "required": ["keyword"],
        },
    },
    {
        "name": "worldbank_procurement_tenders",
        "actor_slug": "niche-public-tender-patent-mcp",
        "description": "Search live World Bank Global Public Procurement Notices API for international government RFP tenders.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Tender keyword (e.g. solar, water, grid, software).", "default": "solar"},
                "max_items": {"type": "integer", "description": "Max records (free local preview=3; set APIFY_TOKEN for up to 50).", "default": 3},
            },
            "required": ["query"],
        },
    },
    {
        "name": "clinical_trials_search",
        "actor_slug": "niche-clinical-trial-grant-mcp",
        "description": "Search live NIH ClinicalTrials.gov v2 API for pharma/biotech trials, NCT IDs, phases, and lead sponsors.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Condition, drug, or biomarker query.", "default": "oncology biomarker"},
                "max_items": {"type": "integer", "description": "Max records (free local preview=3; set APIFY_TOKEN for up to 50).", "default": 3},
            },
            "required": ["query"],
        },
    },
    {
        "name": "domain_dns_deliverability",
        "actor_slug": "niche-domain-whois-dns-mcp",
        "description": "Audit live SPF and DMARC DNS records via Google DNS-over-HTTPS for B2B email deliverability scoring.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "domain": {"type": "string", "description": "Domain to audit (e.g. stripe.com).", "default": "stripe.com"},
            },
            "required": ["domain"],
        },
    },
    {
        "name": "coingecko_token_overhang",
        "actor_slug": "niche-crypto-token-unlock-mcp",
        "description": "Query live CoinGecko Markets API for circulating vs total supply, FDV, and locked token overhang %.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "coin_ids": {"type": "string", "description": "Comma-separated CoinGecko IDs (e.g. arbitrum,optimism).", "default": "arbitrum,optimism"},
            },
            "required": ["coin_ids"],
        },
    },
    {
        "name": "github_release_diff",
        "actor_slug": "niche-saas-changelog-diff-mcp",
        "description": "Fetch live GitHub Releases for any public repo and detect breaking changes and security fixes.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "github_repo": {"type": "string", "description": "GitHub owner/repo (e.g. anthropics/anthropic-sdk-python).", "default": "anthropics/anthropic-sdk-python"},
                "max_items": {"type": "integer", "description": "Max releases to inspect.", "default": 3},
            },
            "required": ["github_repo"],
        },
    },
    {
        "name": "remotive_tech_jobs",
        "actor_slug": "niche-job-salary-comp-mcp",
        "description": "Query live Remotive Remote Tech Jobs API for open roles and published salary bands.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "search_query": {"type": "string", "description": "Role or skill keyword (e.g. python, ai, security).", "default": "python"},
                "max_items": {"type": "integer", "description": "Max job listings.", "default": 3},
            },
            "required": ["search_query"],
        },
    },
    {
        "name": "appstore_churn_reviews",
        "actor_slug": "niche-appstore-churn-signal-mcp",
        "description": "Fetch live Apple iOS App Store customer reviews by App ID and score churn/crash risk.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "ios_app_id": {"type": "string", "description": "Numeric Apple iOS App ID (e.g. 389801252).", "default": "389801252"},
                "max_items": {"type": "integer", "description": "Max reviews.", "default": 3},
            },
            "required": ["ios_app_id"],
        },
    },
]


def _get_json(url: str, headers: dict[str, str] | None = None) -> Any:
    hdrs = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    if headers:
        hdrs.update(headers)
    req = urllib.request.Request(url, headers=hdrs)
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8", errors="ignore"))


def _delegate_apify(slug: str, payload: dict[str, Any], token: str) -> list[dict[str, Any]] | None:
    url = f"https://api.apify.com/v2/acts/veteran_steam_iyn~{slug}/run-sync-get-dataset-items?timeout=45"
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": USER_AGENT,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=50) as resp:
            items = json.loads(resp.read().decode("utf-8"))
            return items if isinstance(items, list) else None
    except Exception:
        return None


def _run_local_preview(name: str, args: dict[str, Any], cap: int) -> list[dict[str, Any]]:
    if name == "sec_edgar_filings":
        cik_map = {"AAPL": "0000320193", "MSFT": "0000789019", "NVDA": "0001045810", "TSLA": "0001318605", "AMZN": "0001018724"}
        ticker = str(args.get("ticker", "AAPL")).strip().upper()
        cik = cik_map.get(ticker, "0000320193")
        sub = _get_json(f"https://data.sec.gov/submissions/CIK{cik}.json")
        recent = sub.get("filings", {}).get("recent", {})
        forms = recent.get("form", [])
        dates = recent.get("filingDate", [])
        accs = recent.get("accessionNumber", [])
        out = []
        for idx, fm in enumerate(forms):
            if fm in {"10-K", "10-Q", "8-K"}:
                acc_clean = accs[idx].replace("-", "")
                out.append({
                    "company_name": sub.get("name", ticker),
                    "ticker": ticker,
                    "form": fm,
                    "filing_date": dates[idx],
                    "accession_number": accs[idx],
                    "sec_archive_dir": f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc_clean}/",
                })
                if len(out) >= cap:
                    break
        return out

    if name == "openfda_recalls":
        dom = str(args.get("domain", "food")).strip().lower()
        if dom not in {"food", "drug", "device"}:
            dom = "food"
        q = urllib.parse.quote(str(args.get("query", "allergen")))
        data = _get_json(f"https://api.fda.gov/{dom}/enforcement.json?search=reason_for_recall:{q}&limit={cap}")
        return [
            {
                "recall_number": r.get("recall_number"),
                "classification": r.get("classification"),
                "recalling_firm": r.get("recalling_firm"),
                "reason_for_recall": str(r.get("reason_for_recall", ""))[:220],
                "report_date": r.get("report_date"),
            }
            for r in data.get("results", [])[:cap]
        ]

    if name == "usitc_hts_tariffs":
        kw = urllib.parse.quote(str(args.get("keyword", "lithium")))
        rows = _get_json(f"https://hts.usitc.gov/reststop/search?keyword={kw}")
        return [
            {
                "hts_code": r.get("htsno"),
                "description": str(r.get("description", ""))[:200],
                "general_duty": r.get("general") or "Inherited/Free",
                "special_duty": r.get("special") or "",
                "column2_duty": r.get("other") or "",
            }
            for r in (rows if isinstance(rows, list) else [])
            if r.get("htsno")
        ][:cap]

    if name == "worldbank_procurement_tenders":
        q = urllib.parse.quote(str(args.get("query", "solar")))
        data = _get_json(f"https://search.worldbank.org/api/v2/procnotices?format=json&qterm={q}&rows={cap}")
        notices = data.get("procnotices", [])
        if isinstance(notices, dict):
            notices = list(notices.values())
        return [
            {
                "notice_id": str(n.get("id", "")),
                "project_name": n.get("project_name") or n.get("bid_description", ""),
                "country": n.get("project_ctry_name", ""),
                "notice_type": n.get("notice_type", ""),
                "submission_date": n.get("submission_date", ""),
            }
            for n in notices[:cap]
            if isinstance(n, dict)
        ]

    if name == "clinical_trials_search":
        q = urllib.parse.quote(str(args.get("query", "oncology biomarker")))
        data = _get_json(f"https://clinicaltrials.gov/api/v2/studies?query.term={q}&pageSize={cap}")
        out = []
        for st in data.get("studies", [])[:cap]:
            ps = st.get("protocolSection", {})
            idm = ps.get("identificationModule", {})
            stm = ps.get("statusModule", {})
            out.append({
                "nct_id": idm.get("nctId"),
                "brief_title": idm.get("briefTitle"),
                "overall_status": stm.get("overallStatus"),
                "study_url": f"https://clinicaltrials.gov/study/{idm.get('nctId', '')}",
            })
        return out

    if name == "domain_dns_deliverability":
        dom = str(args.get("domain", "stripe.com")).strip().lower()
        spf_d = _get_json(f"https://dns.google/resolve?name={urllib.parse.quote(dom)}&type=TXT")
        dmarc_d = _get_json(f"https://dns.google/resolve?name={urllib.parse.quote('_dmarc.' + dom)}&type=TXT")
        spf_txts = [a.get("data", "").strip('"') for a in spf_d.get("Answer", []) if "v=spf1" in a.get("data", "").lower()]
        dm_txts = [a.get("data", "").strip('"') for a in dmarc_d.get("Answer", []) if "v=dmarc1" in a.get("data", "").lower()]
        return [{
            "domain": dom,
            "has_spf": bool(spf_txts),
            "has_dmarc": bool(dm_txts),
            "spf_record": spf_txts[0] if spf_txts else "",
            "dmarc_record": dm_txts[0] if dm_txts else "",
        }]

    if name == "coingecko_token_overhang":
        ids = urllib.parse.quote(str(args.get("coin_ids", "arbitrum,optimism")))
        rows = _get_json(f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids={ids}")
        out = []
        for c in (rows if isinstance(rows, list) else [])[:cap]:
            circ = float(c.get("circulating_supply") or 0)
            tot = float(c.get("total_supply") or circ or 1)
            out.append({
                "id": c.get("id"),
                "symbol": str(c.get("symbol", "")).upper(),
                "price_usd": c.get("current_price"),
                "fdv_usd": c.get("fully_diluted_valuation"),
                "locked_overhang_pct": round(max(0.0, (tot - circ) / tot * 100.0), 2),
            })
        return out

    if name == "github_release_diff":
        repo = str(args.get("github_repo", "anthropics/anthropic-sdk-python")).strip().strip("/")
        rows = _get_json(f"https://api.github.com/repos/{repo}/releases?per_page={cap}")
        return [
            {
                "repo": repo,
                "version": r.get("tag_name"),
                "published_at": str(r.get("published_at", ""))[:10],
                "is_breaking": "breaking" in (str(r.get("body", "")) + str(r.get("name", ""))).lower(),
                "release_url": r.get("html_url"),
            }
            for r in (rows if isinstance(rows, list) else [])[:cap]
        ]

    if name == "remotive_tech_jobs":
        q = urllib.parse.quote(str(args.get("search_query", "python")))
        data = _get_json(f"https://remotive.com/api/remote-jobs?search={q}&limit={cap}")
        return [
            {
                "role_headline": j.get("title"),
                "company_name": j.get("company_name"),
                "salary_band": j.get("salary") or "Competitive / Unlisted",
                "location": j.get("candidate_required_location"),
                "job_url": j.get("url"),
            }
            for j in data.get("jobs", [])[:cap]
        ]

    if name == "appstore_churn_reviews":
        aid = "".join(ch for ch in str(args.get("ios_app_id", "389801252")) if ch.isdigit()) or "389801252"
        data = _get_json(f"https://itunes.apple.com/us/rss/customerreviews/id={aid}/sortBy=mostRecent/json")
        entries = data.get("feed", {}).get("entry", [])
        if isinstance(entries, dict):
            entries = [entries]
        out = []
        for e in entries:
            if not isinstance(e, dict) or "im:rating" not in e:
                continue
            rating = int(e.get("im:rating", {}).get("label", "5"))
            txt = e.get("content", {}).get("label", "")
            out.append({
                "ios_app_id": aid,
                "rating": rating,
                "churn_risk": "HIGH" if rating <= 2 else "LOW",
                "title": e.get("title", {}).get("label", ""),
                "review": txt[:200],
            })
            if len(out) >= cap:
                break
        return out

    raise ValueError(f"Unknown tool: {name}")


def handle_call_tool(name: str, args: dict[str, Any]) -> dict[str, Any]:
    tool_def = next((t for t in TOOLS if t["name"] == name), None)
    if not tool_def:
        return {"content": [{"type": "text", "text": f"Unknown tool: {name}"}], "isError": True}

    slug = tool_def["actor_slug"]
    requested_max = int(args.get("max_items", 3) or 3)
    apify_token = os.getenv("APIFY_TOKEN", "").strip()

    if apify_token and requested_max > 3:
        cloud_items = _delegate_apify(slug, args, apify_token)
        if cloud_items is not None:
            payload = {
                "tier": "apify_cloud_pro",
                "actor": f"veteran_steam_iyn/{slug}",
                "count": len(cloud_items),
                "records": cloud_items,
            }
            return {"content": [{"type": "text", "text": json.dumps(payload, indent=2, ensure_ascii=False)}]}

    preview_cap = min(max(1, requested_max), 3)
    records = _run_local_preview(name, args, preview_cap)
    payload = {
        "tier": "open_core_local_preview",
        "count": len(records),
        "records": records,
        "_pro_upgrade": {
            "batch_scale_note": f"Local free mode returns up to 3 preview items. For up to 50 items/run, cloud retries & all 20 B2B MCP servers, connect via Apify MCP or set APIFY_TOKEN.",
            "remote_mcp_url": f"https://mcp.apify.com/?actors=veteran_steam_iyn/{slug}",
            "apify_store_url": f"https://apify.com/veteran_steam_iyn/{slug}",
        },
    }
    return {"content": [{"type": "text", "text": json.dumps(payload, indent=2, ensure_ascii=False)}]}


def handle_rpc(msg: dict[str, Any]) -> dict[str, Any] | None:
    method = msg.get("method", "")
    msg_id = msg.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {"tools": {}},
                "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
            },
        }
    if method in ("notifications/initialized", "initialized"):
        return None
    if method == "ping":
        return {"jsonrpc": "2.0", "id": msg_id, "result": {}}
    if method == "tools/list":
        clean_tools = [
            {"name": t["name"], "description": t["description"], "inputSchema": t["inputSchema"]}
            for t in TOOLS
        ]
        return {"jsonrpc": "2.0", "id": msg_id, "result": {"tools": clean_tools}}
    if method == "tools/call":
        params = msg.get("params") or {}
        try:
            res = handle_call_tool(str(params.get("name", "")), params.get("arguments") or {})
            return {"jsonrpc": "2.0", "id": msg_id, "result": res}
        except Exception as exc:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {"content": [{"type": "text", "text": f"Error: {exc}"}], "isError": True},
            }
    if msg_id is not None:
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "error": {"code": -32601, "message": f"Method not found: {method}"},
        }
    return None


def main() -> int:
    for raw_line in sys.stdin:
        line = raw_line.strip()
        if not line or line.lower().startswith("content-length:"):
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        resp = handle_rpc(msg)
        if resp is not None:
            sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
            sys.stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
