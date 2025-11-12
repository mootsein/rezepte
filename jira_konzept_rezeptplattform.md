# Jira-Konzept: Rezeptplattform »Schnell & Gesund«

## Vision
Eine schnelle, inspirierende Rezeptplattform für den Alltag: Filter nach Zeit, Diäten und Allergenen; Personalisierung, Wochenplanung, Community. Mobile-first, DSGVO-konform, messbar leistungsstark.

## OKRs (Jahr 1)
- **O1: Produkt-Market-Fit**
  - KR1: 30% Such→Rezept-CTR p95 nach 3 Monaten
  - KR2: 25% 30‑Tage-Retention für registrierte Nutzer
  - KR3: 1.000 kuratierte Rezepte + 500 UGC‑Rezepte live
- **O2: Qualität & Performance**
  - KR1: Core Web Vitals p75 grün auf 90% der Seiten
  - KR2: Fehlerquote < 0,3% Sessions; TTI p75 < 2,0 s
  - KR3: Accessibility-Audits ohne kritische Findings
- **O3: Betrieb & Sicherheit**
  - KR1: 99,9% Verfügbarkeit (Quartals-SLO)
  - KR2: DSR (Export/Löschung) < 7 Tage Erfüllungszeit
  - KR3: 100% kritische Security-Findings < 14 Tage geschlossen

## Non-Functional Requirements (Ziele)
- Performance: LCP < 2,5 s, INP < 200 ms, CLS < 0,1
- Skalierung: 10k RPS Spitze, 3 AZ, horizontale Skalierung
- Sicherheit: OWASP ASVS L2, TLS 1.2+, HSTS, CSP hart
- Datenschutz: Consent-first Tracking, DSR-Self-Service
- Verfügbarkeit: 99,9%, RTO 30 min, RPO 5 min
- Observability: 100% Services mit Logs/Metriken/Traces
- Barrierefreiheit: WCAG AA
- Internationalisierung: de/en, Locale-Fallbacks

## RACI (Auszug)
- Roadmap: **R** PO, **A** PO, **C** SM/Lead Dev, **I** Stakeholder
- Security: **R** Security Lead, **A** CTO, **C** Devs, **I** PO
- Datenverarbeitung (DSR): **R** Privacy, **A** DPO, **C** Backend, **I** Support

## Release-Plan
- **V1 (MVP, 12 Wochen):** Auth, Suche/Filter, Rezeptanzeige, Favoriten, Einkaufsliste, Wochenplan, SEO/Recipe, CI/CD, Monitoring, DSGVO DSR, A11y‑Basics.
- **V2 (6–8 Wochen):** Personalisierte Empfehlungen, PWA-Offline, Backoffice v2, RBAC, Internationalisierung, A/B-Tests, Versionierung.
- **V3 (laufend):** ML‑Verbesserungen, Mobile‑Optimierungen, Badge‑System, Performance‑Budgets straffen.

## Jira-Setup
- **Projekttyp:** Software (Scrum), Key: RCP
- **Issue-Typen:** Epic, Story, Bug, Task, Spike
- **Custom-Felder:** Acceptance Criteria (Text), Business Value (Zahl), Tech Risk (Auswahl), Effort (SP), Fix Version/s
- **Komponenten:** Auth, Search, Catalog, Creator, Planner, Community, Accessibility, SEO, Perf, PWA, Analytics, Privacy, Security, DevOps, SRE, Backoffice, Messaging, Core
- **Labels:** mvp, next, a11y, seo, perf, privacy, security, growth, roadmap-q1/q2
- **Workflows:**
  - Story/Bug: To Do → In Progress → Code Review → QA/Ready for Test → Done
  - Task/Spike: To Do → In Progress → Done
- **Automationen (Beispiele):**
  - Bei Merge in main: transitioniere „Code Review → QA“
  - Story Points ≤ 5 beim Erstellen: Label `mvp`
  - Bei Status „Done“: setze Fix Version/s auf aktuelle Release-Version, benachrichtige Reporter

## Definition of Ready (Checkliste)
- Nutzen sauber formuliert
- **AC** in Gherkin-Stil vorhanden
- Abhängigkeiten/Mocks/Designs geklärt
- Messkriterien (Events/KPIs) benannt
- Security/Privacy‑Hinweise bedacht

## Definition of Done (Checkliste)
- Code + Tests grün, Coverage ≥ Ziel
- Review durchgeführt, keine Blocker
- Doku aktualisiert, Feature‑Flag gesetzt
- Telemetrie-Events implementiert
- Rollback-Pfad vorhanden
- PO‑Abnahme

## Risiken (Auszug)
- Content-Qualität schwankt → Moderations‑SLA, Richtlinien, Reputation‑System
- SEO‑Traffic volatil → Diversifizierung, Newsletter/Push
- Datenschutz‑Fehler → Privacy‑Reviews, DSR‑Automatisierung, Audits

## Artefakte
- `jira_epics_rezeptplattform_refined.csv`
- `jira_backlog_rezeptplattform_refined.csv`
