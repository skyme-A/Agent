# Signalpost Intelligence 🧭
### Ground-Truth Enterprise Intelligence & Legal Registry Discovery Engine

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://zbnvvgfjbxcj2cjtuqxrxq.streamlit.app)
[![Python Version](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Author Profile](https://img.shields.io/badge/Wellfound-Aditi%20Raj-black?style=flat&logo=wellfound&logoColor=white)](https://wellfound.com/u/aditi-raj-31)
[![GitHub](https://img.shields.io/badge/GitHub-skyme--A%2FAgent-181717?style=flat&logo=github&logoColor=white)](https://github.com/skyme-A/Agent)
[![Portfolio](https://img.shields.io/badge/Portfolio-skyme--A.github.io-blue?style=flat)](https://skyme-A.github.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An enterprise-grade deterministic discovery engine engineered to resolve, verify, reconcile, and visualize corporate legal identities, financial health metrics, corporate structures, and statutory gazettes from official registries.

---

## 🌐 Live Application & Links

* **Live Interactive Web App:** [https://zbnvvgfjbxcj2cjtuqxrxq.streamlit.app](https://zbnvvgfjbxcj2cjtuqxrxq.streamlit.app)
* **GitHub Repository:** [https://github.com/skyme-A/Agent](https://github.com/skyme-A/Agent)
* **Developer Portfolio:** [https://skyme-A.github.io](https://skyme-A.github.io)
* **Wellfound Profile:** [https://wellfound.com/u/aditi-raj-31](https://wellfound.com/u/aditi-raj-31)

---

## 📌 Overview

Traditional enterprise data lookups often struggle with fragmented entity records, obsolete scrapes, and ambiguous name matches. **Signalpost Intelligence** solves this through a multi-tier deterministic retrieval pipeline. Instead of relying on generative assumptions or loose web crawling, it pulls ground-truth corporate data directly from official government registers (such as the Norwegian Brønnøysund Register Centre / Enhetsregisteret).

The engine standardizes raw upstream registry records, runs automated risk scoring, parses legal gazette filings, and serves the results through an intuitive UI with direct verified JSON profile exports.

---

## ✨ Features & Capabilities

* **Official Legal Entity Verification:** Instant verification of legal company name, registration number (`Org Nr`), operational status (`ACTIVE`/`INACTIVE`), and statutory legal form (e.g., *Allmennaksjeselskap*).
* **Corporate Health & Risk Scoring:** Generates composite health assessments (e.g., `Health 100/100 · LOW Risk`) evaluated against corporate standing, regulatory compliance, and active filings.
* **Multi-Tab Intelligence Explorer:**
  * 📊 **Financials:** Direct breakdown of reporting accounting years, total revenue, operating profits (e.g., in NOK), and year-over-year operational trends.
  * 🏛️ **Governance:** Real-time visibility into registered board members, executive leadership, chairpersons, and legal signatory mandates.
  * 🏢 **Sub-Units & Branches:** Full mapping of sub-units, regional branch locations, and registered physical operation points.
  * 📜 **Legal Gazettes:** Chronological audit of official regulatory notices, mergers, capital increases, and statutory public filings.
  * 🔍 **Evidence Audit Trail:** Complete verification provenance documenting exact upstream endpoints, timestamps, and confidence checks.
* **Deterministic Data Export:** One-click generation and download of complete, verified entity JSON payloads for seamless integration into downstream API systems.
* **Quick-Select Search Presets:** Pre-configured query tags for high-profile Scandinavian enterprises (e.g., *Equinor ASA*, *DNB Bank*, *Telenor ASA*, *Kongsberg Gruppen*).

---

## 🏗️ System Architecture

```text
 ┌────────────────────────────────────────────────────────┐
 │            Streamlit UI Frontend                       │
 │  (Search Bar, One-Click Entity Presets, Tabs, Exports) │
 └───────────────────────────┬────────────────────────────┘
                             │ Query (Org Nr or Name)
                             ▼
 ┌────────────────────────────────────────────────────────┐
 │                 Signalpost Agent Core                  │
 └─────────────┬────────────────────────────┬─────────────┘
               │ (Cache Hit)                │ (Cache Miss)
               ▼                            ▼
      ┌──────────────────┐        ┌───────────────────────┐
      │  In-Memory / TTL │        │ Official Registry     │
      │  Cache Store     │        │ Connector (Brønnøysund│
      └──────────────────┘        │ Open Data REST APIs)  │
                                  └───────────┬───────────┘
                                              │ Raw Response
                                              ▼
                                  ┌───────────────────────┐
                                  │ Normalization Engine  │
                                  │ & Pydantic Validator  │
                                  └───────────┬───────────┘
                                              │
                                              ▼
                                  ┌───────────────────────┐
                                  │ Corporate Health &    │
                                  │ Risk Evaluator        │
                                  └───────────┬───────────┘
                                              │
                                              ▼
 ┌────────────────────────────────────────────────────────┐
 │   Rendered Views (Financials, Governance, Gazettes)    │
 │       & Downloadable Verified JSON Entity Profile      │
 └────────────────────────────────────────────────────────┘
