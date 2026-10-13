"""
Signalpost: Norwegian Enterprise Intelligence Agent (Production Elite Engine)
Deterministic Multi-Source Extraction, Hierarchy Mapping, Gazette Tracking, Audit Diffing & Batch Support
"""

import sys
import os
import json
import re
import argparse
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field


def parse_amount(val: Any) -> Optional[float]:
    """Safely extracts a numeric float from numbers, strings, or nested API dicts."""
    if val is None:
        return None
    if isinstance(val, (int, float)):
        return float(val)
    if isinstance(val, dict):
        keys = [
            "belop", "verdi", "sum", "driftsresultat", "aarsresultat",
            "salgsinntekter", "sumDriftsinntekter", "driftsinntekter", "sumEgenkapital"
        ]
        for k in keys:
            if k in val and isinstance(val[k], (int, float)):
                return float(val[k])
        for v in val.values():
            if isinstance(v, (int, float)):
                return float(v)
        return None
    if isinstance(val, str):
        cleaned = re.sub(r"[^\d.-]", "", val)
        try:
            return float(cleaned)
        except ValueError:
            return None
    return None


class FieldEnvelope(BaseModel):
    status: str = "available"  # available | not_available | not_applicable | blocked
    value: Any = None
    reason: Optional[str] = None


class FactEvidence(BaseModel):
    field: str
    value: Any
    source_url: str
    source_name: str
    retrieved_at: str
    confidence: float = Field(ge=0.0, le=1.0)


class KeyPersonnel(BaseModel):
    role: str
    name: str


class SubsidiaryUnit(BaseModel):
    sub_org_number: str
    name: str
    location: Optional[str] = None


class LegalAnnouncement(BaseModel):
    date: str
    announcement_type: str
    description: str


class FinancialSummary(BaseModel):
    status: str = "available"
    year: Optional[int] = None
    revenue_nok: Optional[float] = None
    operating_profit_nok: Optional[float] = None
    net_income_nok: Optional[float] = None
    equity_nok: Optional[float] = None


class RiskAssessment(BaseModel):
    risk_level: str  # LOW | MEDIUM | HIGH | CRITICAL
    health_score: int  # 0 to 100
    factors: List[str] = Field(default_factory=list)


class EnrichedCompanyProfile(BaseModel):
    org_number: str
    company_name: str
    legal_form: FieldEnvelope
    registration_date: FieldEnvelope
    status: str  # ACTIVE | BANKRUPT | UNDER_LIQUIDATION
    is_bankrupt: bool = False
    is_under_liquidation: bool = False
    industry_nace_code: FieldEnvelope
    industry_nace_description: FieldEnvelope
    business_address: FieldEnvelope
    postal_address: FieldEnvelope
    registered_employees: FieldEnvelope
    website: FieldEnvelope
    leadership: List[KeyPersonnel] = Field(default_factory=list)
    subsidiaries: List[SubsidiaryUnit] = Field(default_factory=list)
    recent_announcements: List[LegalAnnouncement] = Field(default_factory=list)
    financials: FinancialSummary
    risk_assessment: RiskAssessment
    business_summary: Optional[str] = None
    explanation: str
    changes_detected: List[Dict[str, Any]] = Field(default_factory=list)
    evidence_trail: List[FactEvidence] = Field(default_factory=list)
    profile_updated_at: str


class SignalpostAgent:
    BRREG_BASE = "https://data.brreg.no/enhetsregisteret/api/enheter"
    SUB_UNITS_BASE = "https://data.brreg.no/enhetsregisteret/api/underenheter"
    REGNSKAP_BASE = "https://data.brreg.no/regnskapsregisteret/regnskap"
    KUNNGJORING_BASE = "https://data.brreg.no/enhetsregisteret/api/kunngjoringer"
    HEADERS = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (compatible; SignalpostAgent/3.5; +https://builderr.ai)"
    }
    CACHE_DIR = ".signalpost_cache"

    def __init__(self, timeout: int = 8):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
        os.makedirs(self.CACHE_DIR, exist_ok=True)

    @staticmethod
    def sanitize_org_number(raw_input: str) -> str:
        clean = re.sub(r"\D", "", str(raw_input))
        if len(clean) != 9:
            raise ValueError(f"Invalid Norwegian Org Number: '{raw_input}'. Must be exactly 9 digits.")
        return clean

    def _fetch_registry(self, org_nr: str) -> Optional[Dict[str, Any]]:
        url = f"{self.BRREG_BASE}/{org_nr}"
        try:
            r = self.session.get(url, timeout=self.timeout)
            if r.status_code == 200:
                return r.json()
        except requests.RequestException:
            pass
        return None

    def _fetch_sub_units(self, org_nr: str) -> List[SubsidiaryUnit]:
        subs = []
        try:
            r = self.session.get(
                self.SUB_UNITS_BASE,
                params={"overordnetEnhet": org_nr, "size": 10},
                timeout=self.timeout
            )
            if r.status_code == 200:
                units = r.json().get("_embedded", {}).get("underenheter", [])
                for u in units:
                    sub_org = u.get("organisasjonsnummer", "")
                    sub_name = u.get("navn", "")
                    kommune = u.get("forretningsadresse", {}).get("kommune", "")
                    if sub_org and sub_name:
                        subs.append(SubsidiaryUnit(sub_org_number=sub_org, name=sub_name, location=kommune))
        except requests.RequestException:
            pass
        return subs

    def _fetch_announcements(self, org_nr: str) -> List[LegalAnnouncement]:
        announcements = []
        try:
            r = self.session.get(
                self.KUNNGJORING_BASE,
                params={"organisasjonsnummer": org_nr, "size": 3},
                timeout=self.timeout
            )
            if r.status_code == 200:
                items = r.json().get("_embedded", {}).get("kunngjoringer", [])
                for it in items:
                    pub_date = it.get("publisertDato", "")
                    a_type = it.get("type", {}).get("beskrivelse", "Official Legal Notice")
                    desc = it.get("beskrivelse", a_type)
                    announcements.append(LegalAnnouncement(date=pub_date, announcement_type=a_type, description=desc))
        except requests.RequestException:
            pass
        return announcements

    def _fetch_roles(self, org_nr: str) -> List[KeyPersonnel]:
        url = f"{self.BRREG_BASE}/{org_nr}/roller"
        leaders = []
        try:
            r = self.session.get(url, timeout=self.timeout)
            if r.status_code == 200:
                data = r.json()
                for rg in data.get("rollegrupper", []):
                    group_name = rg.get("type", {}).get("beskrivelse", "")
                    for re_item in rg.get("roller", []):
                        role_title = re_item.get("type", {}).get("beskrivelse", group_name)
                        p = re_item.get("person", {})
                        if p:
                            parts = [p.get("fornavn", ""), p.get("mellomnavn", ""), p.get("etternavn", "")]
                            name = " ".join([x for x in parts if x]).strip()
                            if name:
                                leaders.append(KeyPersonnel(role=role_title, name=name))
        except requests.RequestException:
            pass
        return leaders

    def _fetch_financials(self, org_nr: str) -> FinancialSummary:
        url = f"{self.REGNSKAP_BASE}/{org_nr}"
        try:
            r = self.session.get(url, timeout=self.timeout)
            if r.status_code == 200:
                accounts = r.json()
                if isinstance(accounts, list) and len(accounts) > 0:
                    latest = accounts[0]
                    fra = latest.get("regnskapsperiode", {}).get("fraDato", "")
                    year_val = fra[:4] if isinstance(fra, str) else ""

                    pl = latest.get("resultatregnskapResultat", {})
                    balance = latest.get("egenkapitalGjeld", {})

                    rev_raw = pl.get("driftsinntekter", {})
                    if isinstance(rev_raw, dict):
                        rev_val = (
                            rev_raw.get("salgsinntekter") or
                            rev_raw.get("sumDriftsinntekter") or
                            rev_raw.get("driftsinntekter")
                        )
                    else:
                        rev_val = rev_raw

                    op_val = pl.get("driftsresultat")
                    net_val = pl.get("aarsresultat") or pl.get("ordinartResultatForSkattekostnad")
                    eq_raw = balance.get("egenkapital", {})
                    eq_val = eq_raw.get("sumEgenkapital") if isinstance(eq_raw, dict) else eq_raw

                    return FinancialSummary(
                        status="available",
                        year=int(year_val) if year_val.isdigit() else None,
                        revenue_nok=parse_amount(rev_val),
                        operating_profit_nok=parse_amount(op_val),
                        net_income_nok=parse_amount(net_val),
                        equity_nok=parse_amount(eq_val)
                    )
        except requests.RequestException:
            pass
        return FinancialSummary(status="not_available")

    def _scrape_website(self, url: str) -> Optional[str]:
        if not url:
            return None
        target = url if url.startswith("http") else f"https://{url}"
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            r = self.session.get(target, timeout=4, headers=headers)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, "html.parser")
                meta = soup.find("meta", attrs={"name": re.compile(r"description", re.I)})
                if meta and meta.get("content"):
                    return meta["content"].strip()
                title = soup.find("title")
                if title and title.text:
                    return title.text.strip()
        except requests.RequestException:
            pass
        return None

    def evaluate_risk(self, is_bankrupt: bool, is_liq: bool, financials: FinancialSummary) -> RiskAssessment:
        factors = []
        health_score = 100

        if is_bankrupt:
            factors.append("Formally registered as Bankrupt in Enhetsregisteret.")
            return RiskAssessment(risk_level="CRITICAL", health_score=0, factors=factors)

        if is_liq:
            factors.append("Active Liquidation proceeding registered.")
            health_score -= 50

        if financials.status == "not_available":
            factors.append("Annual accounts not filed or unavailable in Regnskapsregisteret.")
            health_score -= 15
        else:
            if financials.equity_nok is not None and financials.equity_nok < 0:
                factors.append("Negative total balance sheet equity.")
                health_score -= 30
            if financials.operating_profit_nok is not None and financials.operating_profit_nok < 0:
                factors.append("Negative operational operating profit in latest filing.")
                health_score -= 15

        health_score = max(0, min(100, health_score))
        level = "LOW" if health_score >= 80 else ("MEDIUM" if health_score >= 50 else "HIGH")
        if not factors:
            factors.append("Clear corporate legal standing with positive equity filings.")

        return RiskAssessment(risk_level=level, health_score=health_score, factors=factors)

    def check_changes(self, org_nr: str, current_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        cache_file = os.path.join(self.CACHE_DIR, f"{org_nr}.json")
        diffs = []
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    prior = json.load(f)
                for field in ["status", "registered_employees", "legal_form"]:
                    if prior.get(field) != current_data.get(field):
                        diffs.append({
                            "field": field,
                            "previous": prior.get(field),
                            "current": current_data.get(field),
                            "detected_at": datetime.now(timezone.utc).isoformat()
                        })
            except Exception:
                pass
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(current_data, f, ensure_ascii=False)
        return diffs

    def build_explanation(self, name, legal_form, nace_desc, employees, leaders, subsidiaries, announcements, financials, summary, risk) -> str:
        parts = [f"{name} is a Norwegian {legal_form or 'commercial entity'}"]
        if nace_desc:
            parts.append(f"operating within '{nace_desc}'")
        if employees is not None:
            parts.append(f"with {employees} registered employee(s)")
        if subsidiaries:
            parts.append(f"operates {len(subsidiaries)} registered sub-unit/branch location(s)")
        if leaders:
            top_leads = ", ".join([f"{l.role}: {l.name}" for l in leaders[:2]])
            parts.append(f"Key leadership includes {top_leads}.")
        if financials.status == "available" and financials.year:
            fin = []
            if financials.revenue_nok is not None:
                fin.append(f"revenue of {financials.revenue_nok:,.0f} NOK")
            if financials.operating_profit_nok is not None:
                fin.append(f"operating profit of {financials.operating_profit_nok:,.0f} NOK")
            if fin:
                parts.append(f"In {financials.year}, reported {', '.join(fin)}.")
        if announcements:
            latest = announcements[0]
            parts.append(f"Latest official legal gazette notice ({latest.date}): {latest.announcement_type}.")
        parts.append(f"Corporate health scored at {risk.health_score}/100 ({risk.risk_level} risk).")
        if summary:
            clean_sum = summary[:180].replace('"', "'")
            parts.append(f"Public summary: \"{clean_sum}\".")
        return ". ".join(parts).replace("..", ".")

    def get_profile(self, raw_org_number: str) -> Optional[EnrichedCompanyProfile]:
        try:
            org_nr = self.sanitize_org_number(raw_org_number)
        except ValueError:
            return None

        reg_data = self._fetch_registry(org_nr)
        if not reg_data:
            return None

        now = datetime.now(timezone.utc).isoformat()
        evidence: List[FactEvidence] = []
        reg_url = f"{self.BRREG_BASE}/{org_nr}"

        def log_ev(field: str, val: Any, url: str, src: str):
            if val is not None:
                evidence.append(FactEvidence(field=field, value=val, source_url=url, source_name=src, retrieved_at=now, confidence=1.0))

        name = reg_data.get("navn", "UNKNOWN")
        log_ev("company_name", name, reg_url, "Enhetsregisteret")

        org_form = reg_data.get("organisasjonsform")
        legal_form = org_form.get("beskrivelse") if isinstance(org_form, dict) else None
        legal_form_env = FieldEnvelope(status="available" if legal_form else "not_available", value=legal_form)
        log_ev("legal_form", legal_form, reg_url, "Enhetsregisteret")

        reg_date = reg_data.get("registreringsdatoEnhetsregisteret")
        reg_date_env = FieldEnvelope(status="available" if reg_date else "not_available", value=reg_date)
        log_ev("registration_date", reg_date, reg_url, "Enhetsregisteret")

        is_bankrupt = reg_data.get("konkurs", False)
        is_liq = reg_data.get("underAvvikling", False)
        status = "BANKRUPT" if is_bankrupt else ("UNDER_LIQUIDATION" if is_liq else "ACTIVE")
        log_ev("status", status, reg_url, "Enhetsregisteret")

        nace = reg_data.get("naeringskode1", {})
        nace_code = nace.get("kode") if isinstance(nace, dict) else None
        nace_desc = nace.get("beskrivelse") if isinstance(nace, dict) else None
        nace_code_env = FieldEnvelope(status="available" if nace_code else "not_available", value=nace_code)
        nace_desc_env = FieldEnvelope(status="available" if nace_desc else "not_available", value=nace_desc)
        log_ev("industry_nace_code", nace_code, reg_url, "Enhetsregisteret")
        log_ev("industry_nace_description", nace_desc, reg_url, "Enhetsregisteret")

        b_addr = reg_data.get("forretningsadresse", {})
        p_addr = reg_data.get("postadresse", {})
        b_addr_env = FieldEnvelope(status="available" if b_addr else "not_available", value=b_addr)
        p_addr_env = FieldEnvelope(status="available" if p_addr else "not_available", value=p_addr)
        log_ev("business_address", b_addr, reg_url, "Enhetsregisteret")
        log_ev("postal_address", p_addr, reg_url, "Enhetsregisteret")

        emp = reg_data.get("antallAnsatte")
        emp_env = FieldEnvelope(status="available" if emp is not None else "not_available", value=emp)
        log_ev("registered_employees", emp, reg_url, "Enhetsregisteret")

        website = reg_data.get("hjemmeside")
        website_env = FieldEnvelope(status="available" if website else "not_available", value=website)
        log_ev("website", website, reg_url, "Enhetsregisteret")

        roles = self._fetch_roles(org_nr)
        if roles:
            log_ev("leadership", [r.model_dump() for r in roles], f"{self.BRREG_BASE}/{org_nr}/roller", "Foretaksregisteret")

        subs = self._fetch_sub_units(org_nr)
        if subs:
            log_ev("subsidiaries", [s.model_dump() for s in subs], self.SUB_UNITS_BASE, "Enhetsregisteret Underenheter")

        announcements = self._fetch_announcements(org_nr)
        if announcements:
            log_ev("announcements", [a.model_dump() for a in announcements], self.KUNNGJORING_BASE, "Brønnøysund Kunngjøringer")

        financials = self._fetch_financials(org_nr)
        if financials.status == "available":
            log_ev("financials", financials.model_dump(), f"{self.REGNSKAP_BASE}/{org_nr}", "Regnskapsregisteret")

        summary = self._scrape_website(website) if website else None
        if summary and website:
            site_url = website if website.startswith("http") else f"https://{website}"
            log_ev("business_summary", summary, site_url, "Corporate Website")

        risk = self.evaluate_risk(is_bankrupt, is_liq, financials)

        current_snapshot = {
            "status": status,
            "registered_employees": emp,
            "legal_form": legal_form
        }
        changes = self.check_changes(org_nr, current_snapshot)

        explanation = self.build_explanation(name, legal_form, nace_desc, emp, roles, subs, announcements, financials, summary, risk)

        return EnrichedCompanyProfile(
            org_number=org_nr,
            company_name=name,
            legal_form=legal_form_env,
            registration_date=reg_date_env,
            status=status,
            is_bankrupt=is_bankrupt,
            is_under_liquidation=is_liq,
            industry_nace_code=nace_code_env,
            industry_nace_description=nace_desc_env,
            business_address=b_addr_env,
            postal_address=p_addr_env,
            registered_employees=emp_env,
            website=website_env,
            leadership=roles,
            subsidiaries=subs,
            recent_announcements=announcements,
            financials=financials,
            risk_assessment=risk,
            business_summary=summary,
            explanation=explanation,
            changes_detected=changes,
            evidence_trail=evidence,
            profile_updated_at=now
        )


def main():
    parser = argparse.ArgumentParser(description="Signalpost Norwegian Company Intelligence Agent")
    parser.add_argument("org_number", nargs="?", help="9-digit Norwegian Organization Number")
    parser.add_argument("--batch", help="Path to text or JSON file containing org numbers (one per line)")
    parser.add_argument("--output", default="output/batch_results.jsonl", help="Output path for batch results")
    args = parser.parse_args()

    agent = SignalpostAgent()

    if args.batch:
        if not os.path.exists(args.batch):
            print(f"[!] Batch file not found: {args.batch}")
            sys.exit(1)
        os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
        with open(args.batch, "r", encoding="utf-8") as fin, open(args.output, "w", encoding="utf-8") as fout:
            count = 0
            for line in fin:
                raw = line.strip()
                if not raw:
                    continue
                profile = agent.get_profile(raw)
                if profile:
                    fout.write(json.dumps(profile.model_dump(), ensure_ascii=False) + "\n")
                else:
                    envelope = {
                        "org_number": raw,
                        "status": "not_available",
                        "reason": "Organization not found in Enhetsregisteret",
                        "profile_updated_at": datetime.now(timezone.utc).isoformat()
                    }
                    fout.write(json.dumps(envelope, ensure_ascii=False) + "\n")
                count += 1
        print(f"[COMPLETED] Processed {count} entities into {args.output}")
        return

    target = args.org_number if args.org_number else "923609016"
    profile = agent.get_profile(target)
    if profile:
        print(json.dumps(profile.model_dump(), indent=2, ensure_ascii=False))
    else:
        print(json.dumps({
            "org_number": target,
            "status": "not_available",
            "reason": f"No entity matching {target}"
        }, indent=2))


if __name__ == "__main__":
    main()