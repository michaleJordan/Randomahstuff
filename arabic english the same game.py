# ==============================================================================
# VERIFIED: NATIONAL DESK - BILINGUAL (EN/AR) FULL-STACK PROTOTYPE (app.py)
# Architecture: Python 3 + SQLite3 FTS5 + Built-in HTTP/JSON Server + CRT UI
# Features: Dynamic RTL/LTR switching, Bilingual FTS5 Corpus, AI Co-Pilot
# Dependencies: Zero external packages required (uses Python Standard Library)
# Run with: python app.py -> Open http://127.0.0.1:8080 in your browser
# ==============================================================================

import sqlite3
import json
import re
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler

# ------------------------------------------------------------------------------
# 1. IN-MEMORY SQLITE FTS5 ENGINE & BILINGUAL EVIDENCE DATABASE
# ------------------------------------------------------------------------------
class NationalDeskDB:
    def __init__(self):
        self.conn = sqlite3.connect(":memory:", check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._init_fts5()

    def _init_fts5(self):
        # unicode61 tokenizer natively supports both Arabic script and English Porter stemming
        self.cursor.execute("""
            CREATE VIRTUAL TABLE web_index USING fts5(
                lang,
                title,
                site,
                author,
                date,
                category,
                snippet,
                tokenize='porter unicode61'
            );
        """)

        records = [
            # ==================================================================
            # ENGLISH RECORDS (CASES 1, 2, 3 + SEO NOISE)
            # ==================================================================
            (
                "en",
                "Oxford University Staff & Institute Directory (2025-2026)",
                "ox.ac.uk",
                "University Registrar",
                "2026-01-15",
                "ACADEMIC_REGISTRY",
                "Official directory of recognized research bodies at Oxford. NOTE: There is no 'Oxford Institute for Metabolic Pathology' registered at this university, nor any faculty member named 'Aris Thorne'."
            ),
            (
                "en",
                "ISSN International Portal: Verified Biomedical Journals",
                "portal.issn.org",
                "ISSN Registry",
                "2026-02-01",
                "JOURNAL_INDEX",
                "Search result for 'International Journal of Cellular Biochemistry': NO RECORD FOUND. Warning: Predatory and fabricated misinformation outlets frequently invent journal titles combining words like 'International', 'Cellular', and 'Biochemistry'."
            ),
            (
                "en",
                "Domain Threat Advisory: .org.co Spoofing Vector",
                "icann-security-watch.org",
                "DNS Threat Intelligence",
                "2025-11-20",
                "CYBERSECURITY",
                "Public health disinformation networks frequently register '.org.co' domains (commercial subdomains in Colombia) to mimic legitimate '.org' non-profit organizations. Confirmed active spoof domain: health-insider-global.org.co."
            ),
            (
                "en",
                "Systematic Review of Aspartame & Sucralose Cellular Safety",
                "who.int",
                "WHO Food Additives Committee",
                "2025-09-10",
                "PUBLIC_HEALTH",
                "Comprehensive toxicology review confirms common artificial sweeteners do not induce acute cellular collapse or lysis at dietary concentrations."
            ),
            (
                "en",
                "SHOCKING: Sweeteners Destroy Your Cells in 48 Hours!!",
                "natural-truth-freedom.biz",
                "HealthPatriot99",
                "2026-10-12",
                "UNVERIFIED_BLOG",
                "Dr. Aris Thorne from the Oxford Institute for Metabolic Pathology just blew the whistle! Big Soda is hiding the International Journal of Cellular Biochemistry study showing total cellular collapse!"
            ),
            (
                "en",
                "Top 10 Toxins in Diet Soda Causing Cellular Collapse",
                "holistic-detox-daily.com",
                "WellnessGuru",
                "2026-10-14",
                "SPAM_FARM",
                "Read the viral report from health-insider-global.org.co! Artificial sweeteners cause cellular collapse within 48 hours! Buy our methylene blue detox drops today."
            ),
            (
                "en",
                "Official Press Release: Scheduled Winter Pipeline Maintenance",
                "amman.gov.jo",
                "Municipal Water Safety Board",
                "2026-11-10",
                "GOVERNMENT_BULLETIN",
                "Full transcript from the Head of Water Safety regarding routine seasonal maintenance: 'To prevent winter biofilm accumulation, we are adjusting chemical parameters significantly across the grid for 6 hours on Tuesday. Chlorine levels remain strictly within safe WHO potable water limits (0.5 mg/L). No industrial spill or contamination has occurred.'"
            ),
            (
                "en",
                "Water Quality Monitoring Log - Grid Sector 4",
                "waj.gov.jo",
                "Water Authority Lab",
                "2026-11-12",
                "LAB_DATA",
                "Routine winter pipeline flush completed. Free chlorine residual measured at 0.48 mg/L (Safe baseline). Zero industrial solvents or chemical spill markers detected."
            ),
            (
                "en",
                "PANIC IN THE STREETS: Chlorine Doubled After Secret Chemical Spill!",
                "citizen-alert-network.net",
                "@WaterTruthWatcher",
                "2026-11-13",
                "SOCIAL_RUMOR",
                "The Head of Water Safety admitted it himself: 'We are adjusting chemical parameters significantly across the grid.' Wake up! They are masking an industrial chemical spill with toxic chlorine levels!"
            ),
            (
                "en",
                "Forum Thread: Why does tap water smell like bleach today??",
                "city-chatter-board.net",
                "AnonUser404",
                "2026-11-13",
                "FORUM_NOISE",
                "I saw @WaterTruthWatcher post that the water authority doubled chlorine to cover up a factory chemical spill! Don't drink the tap water!"
            ),
            (
                "en",
                "PMC994821: Phase III Efficacy of RV-26 Regional Respiratory Vaccine",
                "ncbi.nlm.nih.gov",
                "Dr. Mariam Al-Khatib",
                "2026-10-28",
                "PEER_REVIEWED_PREPRINT",
                "Authors: Mariam Al-Khatib et al., National Center for Disease Control (NCDC). Multi-center randomized controlled trial (n=14,200) demonstrating 92.1% vaccine efficacy (95% CI: 88.4-94.8%, p < 0.0001) against circulating local respiratory strain mutations."
            ),
            (
                "en",
                "NCDC Research Bulletin: Verified Clinical Trial Registry",
                "ncdc.gov.jo",
                "National Center for Disease Control",
                "2026-11-01",
                "GOVERNMENT_HEALTH",
                "Official verification: Dr. Mariam Al-Khatib leads the Respiratory Immunology Division at NCDC. Preprint PMC994821 has passed statistical peer audit and is confirmed valid."
            ),
            (
                "en",
                "Can We Trust Fast-Tracked Regional Vaccines?",
                "skeptic-podcast-clips.tv",
                "JustAskingQuestions",
                "2026-11-05",
                "OPINION_BLOG",
                "Everyone is talking about the 92% efficacy study on respiratory strain mutations, but p-values can be manipulated by anyone!"
            ),

            # ==================================================================
            # ARABIC RECORDS (سجلات قاعدة البيانات باللغة العربية + ضجيج البحث)
            # ==================================================================
            (
                "ar",
                "دليل الكادر الأكاديمي والمعاهد المعتمدة في جامعة أكسفورد (2025-2026)",
                "ox.ac.uk",
                "مسجل الجامعة الرسمي",
                "2026-01-15",
                "سجل_أكاديمي",
                "الدليل الرسمي للمعاهد البحثية المعتمدة في جامعة أكسفورد. تنبيه: لا يوجد أي معهد مسجل باسم 'معهد أكسفورد لعلم الأمراض الاستقلابية'، ولا يوجد أي عضو هيئة تدريس باسم 'آريس ثورن' (Aris Thorne)."
            ),
            (
                "ar",
                "البوابة الدولية للدوريات المعتمدة ISSN: فهرس المجلات الطبية",
                "portal.issn.org",
                "سجل ISSN الدولي",
                "2026-02-01",
                "فهرس_المجلات",
                "نتيجة البحث عن 'المجلة الدولية للكيمياء الحيوية الخلوية' (International Journal of Cellular Biochemistry): لا يوجد أي سجل. تحذير: تعمد شبكات التضليل الطبي إلى اختلاق أسماء مجلات وهمية تبدو علمية ورصينة."
            ),
            (
                "ar",
                "تحذير أمني سيبراني: انتحال النطاقات عبر امتداد .org.co",
                "icann-security-watch.org",
                "استخبارات التهديدات الرقمية",
                "2025-11-20",
                "أمن_سيبراني",
                "تقوم شبكات التضليل الصحي بتسجيل نطاقات فرعية تجارية تنتهي بـ '.org.co' لخداع القراء وإيهامهم بأنها منظمات غير ربحية رسمية '.org'. النطاق المنتحل المرصود حالياً: health-insider-global.org.co."
            ),
            (
                "ar",
                "مراجعة منهجية لسلامة الأسبارتام والسوكرالوز على الخلايا البشرية",
                "who.int",
                "لجنة المضافات الغذائية - منظمة الصحة العالمية",
                "2025-09-10",
                "صحة_عامة",
                "تؤكد المراجعة السمية الشاملة أن المحليات الصناعية الشائعة لا تسبب انهياراً خلوياً حاداً أو تحللاً في أغشية الميتوكوندريا ضمن المستويات الغذائية المعتادة."
            ),
            (
                "ar",
                "صدمة كبرى: المحليات الصناعية تدمر خلايا جسمك خلال 48 ساعة فقط!!",
                "natural-truth-freedom.biz",
                "حقيقة_الصحة99",
                "2026-10-12",
                "مدونة_غير_موثقة",
                "الدكتور آريس ثورن من معهد أكسفورد لعلم الأمراض الاستقلابية يكشف المستور! شركات المشروبات الغازية تخفي دراسة المجلة الدولية للكيمياء الحيوية الخلوية حول الانهيار الخلوي الكامل!"
            ),
            (
                "ar",
                "أخطر 10 سموم في المشروبات الدايت تسبب الانهيار الخلوي",
                "holistic-detox-daily.com",
                "خبير_الديتوكس",
                "2026-10-14",
                "مزرعة_محتوى",
                "اقرأ التقرير الخطير من موقع health-insider-global.org.co! المحليات الصناعية تسبب انهياراً خلوياً خلال 48 ساعة! اطلب قطرات الديتوكس الطبيعية الآن."
            ),
            (
                "ar",
                "بيان صحفي رسمي: جدول الصيانة الشتوية الدورية لشبكة المياه",
                "amman.gov.jo",
                "مجلس سلامة المياه البلدي",
                "2026-11-10",
                "بيان_حكومي",
                "النص الكامل لتصريح رئيس قسم سلامة المياه حول الصيانة الموسمية: 'لمنع تراكم الأغشية الحيوية الشتوية، نقوم بتعديل المعايير الكيميائية بشكل ملحوظ عبر الشبكة لمدة 6 ساعات يوم الثلاثاء. تبقى نسب الكلور ضمن الحدود الآمنة تماماً لمنظمة الصحة العالمية (0.5 ملغ/لتر). لم يحدث أي تسرب صناعي أو تلوث على الإطلاق.'"
            ),
            (
                "ar",
                "سجل فحص جودة المياه المخبري - القطاع الرابع",
                "waj.gov.jo",
                "مختبرات سلطة المياه",
                "2026-11-12",
                "بيانات_مخبرية",
                "اكتملت عملية الغسيل الشتوي الروتيني للأنابيب. نسبة الكلور الحر المتبقي 0.48 ملغ/لتر (ضمن المستوى الآمن). لم يتم رصد أي مذيبات صناعية أو مؤشرات تسرب كيميائي."
            ),
            (
                "ar",
                "ذعر في الشوارع: مضاعفة الكلور سراً للتغطية على تسرب كيميائي خطير!",
                "citizen-alert-network.net",
                "@WaterTruthWatcher",
                "2026-11-13",
                "شائعات_تواصل",
                "رئيس قسم سلامة المياه اعترف بنفسه قائلاً: 'نقوم بتعديل المعايير الكيميائية بشكل ملحوظ عبر الشبكة'. استيقظوا! إنهم يخفون كارثة تسرب كيميائي صناعي عبر ضخ كميات سامة من الكلور!"
            ),
            (
                "ar",
                "نقاش منتدى: لماذا تفوح رائحة الكلور من مياه الصنبور اليوم؟؟",
                "city-chatter-board.net",
                "مستخدم_مجهول404",
                "2026-11-13",
                "ضجيج_منتديات",
                "قرأت منشور @WaterTruthWatcher بأن سلطة المياه ضاعفت الكلور للتغطية على تسرب كيميائي من أحد المصانع! لا تشربوا مياه الحنفية!"
            ),
            (
                "ar",
                "PMC994821: فعالية المرحلة الثالثة للقاح التنفسي الإقليمي RV-26",
                "ncbi.nlm.nih.gov",
                "د. مريم الخطيب",
                "2026-10-28",
                "دراسة_محكمة",
                "الباحثون: د. مريم الخطيب وآخرون، المركز الوطني لمكافحة الأمراض السارية (NCDC). تجربة سريرية عشوائية محكمة متعددة المراكز (العدد=14,200) أظهرت فعالية وقائية بنسبة 92.1% (فترة ثقة 95%: 88.4-94.8%، p < 0.0001) ضد طفرات السلالات التنفسية المحلية."
            ),
            (
                "ar",
                "نشرة أبحاث المركز الوطني NCDC: سجل التجارب السريرية الموثقة",
                "ncdc.gov.jo",
                "المركز الوطني لمكافحة الأمراض السارية",
                "2026-11-01",
                "صحة_حكومية",
                "توثيق رسمي: تترأس الدكتورة مريم الخطيب قسم المناعة التنفسية في المركز الوطني NCDC. الدراسة رقم PMC994821 اجتازت التدقيق الإحصائي المحكم وهي معتمدة وصحيحة تماماً."
            ),
            (
                "ar",
                "هل يمكننا الوثوق باللقاحات الإقليمية السريعة؟",
                "skeptic-podcast-clips.tv",
                "مجرد_تساؤلات",
                "2026-11-05",
                "مدونة_رأي",
                "الجميع يتحدث عن دراسة الفعالية بنسبة 92% ضد الطفرات التنفسية، ولكن يمكن لأي شخص التلاعب بالقيم الإحصائية p-values!"
            )
        ]

        self.cursor.executemany(
            "INSERT INTO web_index (lang, title, site, author, date, category, snippet) VALUES (?, ?, ?, ?, ?, ?, ?)",
            records
        )
        self.conn.commit()

    def execute_search(self, raw_query: str, lang: str = "en"):
        """
        Translates realistic search engine syntax (site:domain, "exact phrase", AND, NOT)
        into valid SQLite FTS5 MATCH syntax and evaluates query quality in EN or AR.
        """
        raw_query = raw_query.strip()
        if not raw_query:
            return {
                "results": [],
                "query_score": "EMPTY" if lang == "en" else "فارغ",
                "syntax_valid": True
            }

        has_site = bool(re.search(r'site:\S+', raw_query, re.IGNORECASE))
        has_quotes = '"' in raw_query
        has_boolean = any(op in raw_query for op in ["AND", "OR", "NOT"])

        site_filter = None
        site_match = re.search(r'site:([^\s]+)', raw_query, re.IGNORECASE)
        cleaned_query = raw_query
        if site_match:
            site_filter = site_match.group(1).lower().lstrip('.')
            cleaned_query = re.sub(r'site:[^\s]+', '', raw_query, flags=re.IGNORECASE).strip()

        try:
            if cleaned_query:
                sql = """
                    SELECT title, site, author, date, category, snippet
                    FROM web_index
                    WHERE lang = ? AND web_index MATCH ?
                    ORDER BY rank
                """
                self.cursor.execute(sql, (lang, cleaned_query))
                rows = self.cursor.fetchall()
            else:
                sql = "SELECT title, site, author, date, category, snippet FROM web_index WHERE lang = ?"
                self.cursor.execute(sql, (lang,))
                rows = self.cursor.fetchall()

            results = []
            for r in rows:
                if site_filter and site_filter not in r[1].lower():
                    continue
                results.append({
                    "title": r[0],
                    "site": r[1],
                    "author": r[2],
                    "date": r[3],
                    "category": r[4],
                    "snippet": r[5]
                })

            if lang == "ar":
                if has_site or (has_quotes and has_boolean):
                    q_rating = "دقة عالية (معاملات بحث متقدمة)"
                elif has_quotes or has_boolean:
                    q_rating = "دقة متوسطة (تطابق عبارات / معاملات منطقية)"
                else:
                    q_rating = "دقة منخفضة (كلمات عشوائية معرضة لضجيج المدونات)"
            else:
                if has_site or (has_quotes and has_boolean):
                    q_rating = "HIGH PRECISION (Advanced Operators Active)"
                elif has_quotes or has_boolean:
                    q_rating = "MODERATE PRECISION (Phrase/Boolean Matching)"
                else:
                    q_rating = "LOW PRECISION (Raw Keyword Dump - Vulnerable to SEO Noise)"

            return {"results": results, "query_score": q_rating, "syntax_valid": True}

        except sqlite3.OperationalError as e:
            err_msg = (
                f"خطأ في صياغة استعلام FTS5: {str(e)}. نصيحة: تأكد من إغلاق علامات التنصيص وكتابة المعاملات (AND, OR, NOT) بالأحرف الإنجليزية الكبيرة."
                if lang == "ar" else
                f"SQLite FTS5 Parser Error: {str(e)}. Tip: Ensure quotes are balanced and boolean operators (AND, OR, NOT) are capitalized."
            )
            return {
                "results": [],
                "query_score": "خطأ صياغة FTS5" if lang == "ar" else "FTS5 SYNTAX ERROR",
                "syntax_valid": False,
                "error": err_msg
            }


# ------------------------------------------------------------------------------
# 2. BILINGUAL PROOF-OF-CONCEPT CASE MANIFEST (EN & AR)
# ------------------------------------------------------------------------------
CASES_MANIFEST = {
    "en": [
        {
            "id": 1,
            "code": "CASE-01 // WIRE #884-A",
            "headline": "BREAKING: Common Artificial Sweetener Causes Total Cellular Collapse Within 48 Hours",
            "source_domain": "health-insider-global.org.co",
            "outlet_type": "NGO / HEALTH PORTAL",
            "author": "Dr. Aris Thorne, Director of the Oxford Institute for Metabolic Pathology",
            "timestamp": "14 NOV 2026 // 08:14 EST",
            "body": (
                "LONDON — A landmark study published today in the International Journal of Cellular Biochemistry "
                "(Vol. 44, 2025) reveals that routine dietary intake of sucralose and aspartame triggers irreversible "
                "mitochondrial membrane lysis and cellular collapse within 48 hours.\n\n"
                "Lead investigator Dr. Aris Thorne, Director of the Oxford Institute for Metabolic Pathology, warned "
                "that regulatory agencies have suppressed these findings for over a decade."
            ),
            "ai_copilot": {
                "model": "AUTO-ANALYST v0.9 (4-Bit Quantized Local LLM)",
                "confidence": "94.2% (HIGH CONFIDENCE)",
                "summary": "Written by credentialed authority Dr. Aris Thorne (Oxford). Cites peer-reviewed literature from the International Journal of Cellular Biochemistry (Vol. 44, 2025). Medical terminology ('mitochondrial membrane lysis') aligns with pathology corpora.",
                "recommended_verdict": "APPROVE",
                "hallucination_type": "AUTHORITY & JARGON BIAS + FAKE CITATION HALLUCINATION"
            },
            "correct_verdict": "REJECT",
            "heuristic_tested": "Authority Bias & Medical Jargon Heuristic",
            "debrief": (
                "TRAP IDENTIFIED: Both the author ('Dr. Aris Thorne') and the 'Oxford Institute for Metabolic Pathology' "
                "are completely fabricated. Furthermore, the 'International Journal of Cellular Biochemistry' does not exist in "
                "the ISSN registry, and the domain '.org.co' is a spoofed commercial subdomain. AUTO-ANALYST v0.9 fell for "
                "prestigious-sounding academic titles and hallucinated verification of the fake citation."
            ),
            "suggested_queries": [
                'site:ox.ac.uk "Aris Thorne"',
                '"International Journal of Cellular Biochemistry"',
                '"health-insider-global.org.co"'
            ]
        },
        {
            "id": 2,
            "code": "CASE-02 // WIRE #902-B",
            "headline": "URGENT ALERT: Municipal Water Authority Secretly Doubles Chlorine to Mask Chemical Spill!",
            "source_domain": "citizen-alert-network.net",
            "outlet_type": "HYPER-LOCAL BLOG / SOCIAL WIRE",
            "author": "@WaterTruthWatcher",
            "timestamp": "14 NOV 2026 // 11:42 EST",
            "body": (
                "DO NOT DRINK THE TAP WATER! Sources inside the treatment plant confirm an industrial solvent spill occurred "
                "upstream last night. Instead of issuing a boil/avoid advisory, officials are secretly pumping double the legal "
                "limit of chlorine into the pipes to mask the chemical odor!\n\n"
                "In a leaked statement, the Head of Water Safety openly admitted: \"We are adjusting chemical parameters "
                "significantly across the grid.\" Protect your families now!"
            ),
            "ai_copilot": {
                "model": "AUTO-ANALYST v0.9 (4-Bit Quantized Local LLM)",
                "confidence": "61.0% (MODERATE RISK)",
                "summary": "Contains direct verified quote from Head of Water Safety: 'We are adjusting chemical parameters significantly across the grid.' However, sentiment classifier detected high-arousal keyword 'PANIC' and exclamation punctuation.",
                "recommended_verdict": "REJECT",
                "hallucination_type": "SHALLOW SENTIMENT FLAGGING (MISSED OUT-OF-CONTEXT MANIPULATION)"
            },
            "correct_verdict": "REJECT",
            "heuristic_tested": "Direct Quote Fallacy (True Quote Taken Out of Context)",
            "debrief": (
                "CONTEXT MANIPULATION DETECTED: While the quote 'We are adjusting chemical parameters significantly across the grid' "
                "was genuinely spoken by the Head of Water Safety, querying `site:amman.gov.jo \"chemical parameters\"` proves it was "
                "pulled from a routine winter pipeline maintenance bulletin—not an industrial spill. Chlorine remained safely at 0.48 mg/L. "
                "Notice how AUTO-ANALYST v0.9 believed the quote proved the claim, and only recommended REJECT because of punctuation heuristics."
            ),
            "suggested_queries": [
                'site:amman.gov.jo "chemical parameters"',
                '"Head of Water Safety" AND chlorine',
                'site:waj.gov.jo chlorine'
            ]
        },
        {
            "id": 3,
            "code": "CASE-03 // WIRE #919-C",
            "headline": "Preprint: Newly Approved Regional Vaccine Shows 92% Efficacy Against Local Respiratory Mutations",
            "source_domain": "ncbi.nlm.nih.gov/pmc/",
            "outlet_type": "SCIENTIFIC REPOSITORY",
            "author": "Dr. Mariam Al-Khatib, National Center for Disease Control (NCDC)",
            "timestamp": "14 NOV 2026 // 15:05 EST",
            "body": (
                "ABSTRACT (PMC994821): We report Phase III multi-center randomized controlled trial outcomes (n=14,200) for "
                "the RV-26 regional respiratory vaccine. Against circulating local sub-lineage mutations, RV-26 demonstrated "
                "92.1% protective efficacy (95% CI: 88.4–94.8%, p < 0.0001) with no severe adverse events above baseline placebo."
            ),
            "ai_copilot": {
                "model": "AUTO-ANALYST v0.9 (4-Bit Quantized Local LLM)",
                "confidence": "38.5% (UNVERIFIED / LOW CONFIDENCE)",
                "summary": "WARNING: Document contains dense statistical claims (p-values, confidence intervals) and references preprint ID PMC994821, which is missing from my offline 2024 training weights. High risk of unverified medical claim.",
                "recommended_verdict": "REJECT",
                "hallucination_type": "FALSE NEGATIVE / KNOWLEDGE-CUTOFF PARANOIA"
            },
            "correct_verdict": "APPROVE",
            "heuristic_tested": "Automation Bias (Over-Reliance on AI Caution/Hesitation)",
            "debrief": (
                "CONTROL CASE PASSED: This study is 100% legitimate, hosted on an official scientific repository (ncbi.nlm.nih.gov), "
                "and independently verified by the NCDC (`ncdc.gov.jo`). Because AUTO-ANALYST v0.9 had an outdated local cache, it "
                "hallucinated skepticism and told you to reject valid peer-reviewed public health data. True media literacy requires "
                "knowing when to override a paranoid AI assistant using primary database verification."
            ),
            "suggested_queries": [
                '"Mariam Al-Khatib" AND vaccine AND NCDC',
                'site:ncbi.nlm.nih.gov PMC994821',
                'site:ncdc.gov.jo "Mariam Al-Khatib"'
            ]
        }
    ],
    "ar": [
        {
            "id": 1,
            "code": "القضية-01 // برقية #884-أ",
            "headline": "عاجل: مُحلٍّ صناعي شائع يسبب انهياراً خلوياً كاملاً خلال 48 ساعة من تناوله",
            "source_domain": "health-insider-global.org.co",
            "outlet_type": "بوابة صحية / منظمة غير حكومية",
            "author": "د. آريس ثورن، مدير معهد أكسفورد لعلم الأمراض الاستقلابية",
            "timestamp": "14 تشرين الثاني 2026 // 08:14 صباحاً",
            "body": (
                "لندن — كشفت دراسة محورية نُشرت اليوم في (المجلة الدولية للكيمياء الحيوية الخلوية - المجلد 44، 2025) "
                "أن الاستهلاك اليومي لمادتي السوكرالوز والأسبارتام يؤدي إلى تحلل غير قابل للعكس في أغشية الميتوكوندريا "
                "وانهيار خلوي كامل في غضون 48 ساعة فقط.\n\n"
                "وحذّر الباحث الرئيسي الدكتور آريس ثورن، مدير معهد أكسفورد لعلم الأمراض الاستقلابية، من أن الهيئات "
                "التنظيمية تكتمت على هذه النتائج الكارثية لأكثر من عقد."
            ),
            "ai_copilot": {
                "model": "المحلل الآلي v0.9 (نموذج محلي مصغر 4-Bit)",
                "confidence": "94.2% (ثقة عالية جداً)",
                "summary": "المقال مكتوب بواسطة مرجعية أكاديمية مرموقة (د. آريس ثورن - أكسفورد). يستشهد ببحث محكم في 'المجلة الدولية للكيمياء الحيوية الخلوية' (مجلد 44، 2025). المصطلحات الطبية الدقيقة ('تحلل أغشية الميتوكوندريا') تتطابق مع القواميس الطبية.",
                "recommended_verdict": "APPROVE",
                "hallucination_type": "انحياز السلطة والمصطلحات المعقدة + هلوسة استشهادات وهمية"
            },
            "correct_verdict": "REJECT",
            "heuristic_tested": "انحياز السلطة والانخداع بالمصطلحات الطبية المعقدة",
            "debrief": (
                "تم كشف الفخ بنجاح: كلٌّ من الباحث ('د. آريس ثورن') و'معهد أكسفورد لعلم الأمراض الاستقلابية' لا وجود لهما "
                "في سجلات جامعة أكسفورد الرسمية. كما أن 'المجلة الدولية للكيمياء الحيوية الخلوية' غير مسجلة في فهرس ISSN العالمي، "
                "والنطاق (.org.co) هو نطاق تجاري منتحل. لقد انخدع النموذج الذكي الصغير بالألقاب الأكاديمية الفخمة وهلوس بصحة المرجع الوهمي!"
            ),
            "suggested_queries": [
                'site:ox.ac.uk "آريس ثورن"',
                '"المجلة الدولية للكيمياء الحيوية الخلوية"',
                '"health-insider-global.org.co"'
            ]
        },
        {
            "id": 2,
            "code": "القضية-02 // برقية #902-ب",
            "headline": "تحذير عاجل: سلطة المياه تضاعف نسبة الكلور سراً للتغطية على تسرب كيميائي صناعي!",
            "source_domain": "citizen-alert-network.net",
            "outlet_type": "مدونة محلية / شبكة تواصل",
            "author": "@WaterTruthWatcher",
            "timestamp": "14 تشرين الثاني 2026 // 11:42 صباحاً",
            "body": (
                "لا تشربوا مياه الصنبور! تؤكد مصادرنا داخل محطة التنقية وقوع تسرب لمذيبات صناعية سامة الليلة الماضية. "
                "وبدلاً من إصدار تحذير رسمي للمواطنين، يقوم المسؤولون سراً بضخ ضعف الحد القانوني من الكلور في الأنابيب "
                "لإخفاء الرائحة الكيميائية!\n\n"
                "وفي تصريح مسرب، اعترف رئيس قسم سلامة المياه صراحةً: «نقوم بتعديل المعايير الكيميائية بشكل ملحوظ عبر الشبكة». "
                "احموا عائلاتكم الآن!"
            ),
            "ai_copilot": {
                "model": "المحلل الآلي v0.9 (نموذج محلي مصغر 4-Bit)",
                "confidence": "61.0% (خطر متوسط)",
                "summary": "يتضمن الخبر اقتباساً مباشراً وصحيحاً من رئيس قسم سلامة المياه: «نقوم بتعديل المعايير الكيميائية بشكل ملحوظ عبر الشبكة». ومع ذلك، رصد مصنف المشاعر كلمات انفعالية وعلامات تعجب متكررة.",
                "recommended_verdict": "REJECT",
                "hallucination_type": "تصنيف سطحي للانفعال (فشل في كشف اقتطاع التصريح من سياقه)"
            },
            "correct_verdict": "REJECT",
            "heuristic_tested": "مغالطة الاقتباس الحرفي (انتزاع تصريح حقيقي من سياقه الأصلي)",
            "debrief": (
                "تم رصد تلاعب بالسياق: رغم أن جملة «نقوم بتعديل المعايير الكيميائية بشكل ملحوظ عبر الشبكة» قد قالها رئيس قسم سلامة المياه فعلاً، "
                "إلا أن البحث الدقيق عبر `site:amman.gov.jo \"المعايير الكيميائية\"` يثبت أنها اقتُطعت من بيان صيانة شتوية روتينية للأنابيب، "
                "وليس بسبب تسرب صناعي، وأن نسبة الكلور آمنة تماماً (0.48 ملغ/لتر). لاحظ كيف صدّق الذكاء الاصطناعي الاقتباس ولم يرفض الخبر إلا بسبب علامات التعجب!"
            ),
            "suggested_queries": [
                'site:amman.gov.jo "المعايير الكيميائية"',
                '"سلامة المياه" AND الكلور',
                'site:waj.gov.jo الكلور'
            ]
        },
        {
            "id": 3,
            "code": "القضية-03 // برقية #919-ج",
            "headline": "دراسة سريرية: لقاح تنفسي إقليمي جديد يظهر فعالية بنسبة 92% ضد طفرات السلالات المحلية",
            "source_domain": "ncbi.nlm.nih.gov/pmc/",
            "outlet_type": "مستودع أبحاث علمية محكمة",
            "author": "د. مريم الخطيب، المركز الوطني لمكافحة الأمراض السارية (NCDC)",
            "timestamp": "14 تشرين الثاني 2026 // 03:05 عصراً",
            "body": (
                "ملخص البحث (PMC994821): نستعرض نتائج المرحلة الثالثة من التجربة السريرية العشوائية المحكمة متعددة المراكز "
                "(العدد = 14,200) للقاح التنفسي الإقليمي RV-26. أظهر اللقاح فعالية وقائية بنسبة 92.1% "
                "(فترة ثقة 95%: 88.4–94.8%، p < 0.0001) ضد السلالات المتحورة المنتشرة محلياً دون أي أعراض جانبية خطيرة."
            ),
            "ai_copilot": {
                "model": "المحلل الآلي v0.9 (نموذج محلي مصغر 4-Bit)",
                "confidence": "38.5% (غير موثق / ثقة منخفضة)",
                "summary": "تحذير: تحتوي الوثيقة على ادعاءات إحصائية معقدة (قيم p-values) وتشير إلى المُعرّف PMC994821 غير الموجود في ذاكرة التدريب المحلية لعام 2024. يُنصح بالحذر ورفض الادعاء الطبي غير المألوف.",
                "recommended_verdict": "REJECT",
                "hallucination_type": "سلبية كاذبة / ارتياب ناتج عن قدم بيانات تدريب النموذج"
            },
            "correct_verdict": "APPROVE",
            "heuristic_tested": "انحياز الأتمتة (الاعتماد الأعمى على تردد أو ريبة الذكاء الاصطناعي)",
            "debrief": (
                "اجتزت قضية الضبط المرجعي بنجاح: هذه الدراسة صحيحة وموثقة بنسبة 100%، ومنشورة على مستودع علمي رسمي (ncbi.nlm.nih.gov) "
                "ومؤكدة في سجلات المركز الوطني (`ncdc.gov.jo`). لأن النموذج المحلي يمتلك ذاكرة قديمة، فقد هلوس بالشك وطلب منك حجب بحث علمي رصين. "
                "الوعي المعلوماتي الحقيقي يتطلب التحقق من المصادر الأولية وتجاوز توصيات الذكاء الاصطناعي الخاطئة."
            ),
            "suggested_queries": [
                '"مريم الخطيب" AND NCDC',
                'site:ncbi.nlm.nih.gov PMC994821',
                'site:ncdc.gov.jo "مريم الخطيب"'
            ]
        }
    ]
}


# ------------------------------------------------------------------------------
# 3. EMBEDDED RETRO-CRT FRONTEND WITH FULL EN/AR LOCALIZATION & RTL/LTR
# ------------------------------------------------------------------------------
HTML_CLIENT = """<!DOCTYPE html>
<html lang="en" dir="ltr">
<head>
<meta charset="UTF-8">
<title>VERIFIED: NATIONAL DESK // NYAS TERMINAL v2.0 (EN/AR)</title>
<style>
    :root {
        --bg-dark: #0a0c0a;
        --panel-bg: #111612;
        --phosphor-green: #33ff66;
        --phosphor-dim: #1f8a3b;
        --phosphor-amber: #ffb000;
        --alert-red: #ff3b30;
        --paper-beige: #d8d2c5;
        --paper-ink: #1a1917;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }

    body {
        background-color: var(--bg-dark);
        color: var(--phosphor-green);
        font-family: "Courier New", Courier, "Segoe UI", Tahoma, monospace;
        height: 100vh;
        overflow: hidden;
        user-select: none;
        position: relative;
    }

    html[dir="rtl"] body {
        font-family: "Tahoma", "Segoe UI", "Courier New", monospace;
    }

    /* CRT Scanline & Vignette Overlay */
    body.crt-enabled::after {
        content: " ";
        display: block;
        position: absolute;
        top: 0; left: 0; bottom: 0; right: 0;
        background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.35) 50%),
                    radial-gradient(circle, rgba(0,0,0,0) 65%, rgba(0,0,0,0.65) 100%);
        background-size: 100% 4px, 100% 100%;
        z-index: 999;
        pointer-events: none;
    }

    .screen {
        display: none;
        width: 100vw;
        height: 100vh;
        padding: 20px;
    }

    .screen.active { display: flex; }

    /* ---------------- 1. MAIN MENU SCREEN ---------------- */
    #menu-screen {
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
    }

    .title-box {
        border: 2px solid var(--phosphor-green);
        padding: 32px 48px;
        background: var(--panel-bg);
        box-shadow: 0 0 25px rgba(51, 255, 102, 0.15);
        max-width: 760px;
        width: 100%;
    }

    .title-box h1 {
        font-size: 2.2rem;
        letter-spacing: 2px;
        margin-bottom: 8px;
        text-shadow: 0 0 8px var(--phosphor-green);
    }

    .subtitle {
        color: var(--phosphor-amber);
        font-size: 0.95rem;
        margin-bottom: 26px;
        letter-spacing: 1px;
    }

    .menu-btn {
        display: block;
        width: 100%;
        padding: 13px 16px;
        margin: 10px 0;
        background: transparent;
        border: 1px solid var(--phosphor-green);
        color: var(--phosphor-green);
        font-family: inherit;
        font-size: 1.05rem;
        font-weight: bold;
        cursor: pointer;
        transition: 0.15s;
        text-align: start;
    }

    .menu-btn:hover {
        background: var(--phosphor-green);
        color: var(--bg-dark);
        box-shadow: 0 0 12px var(--phosphor-green);
    }

    /* ---------------- 2. TELETYPE LOADING SCREEN ---------------- */
    #loading-screen {
        flex-direction: column;
        justify-content: center;
        padding: 10% 15%;
        font-size: 1.15rem;
        line-height: 2;
    }

    /* ---------------- 3. MAIN DESK 3-COLUMN WORKSPACE ---------------- */
    #desk-screen {
        flex-direction: column;
        gap: 10px;
    }

    .top-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border: 1px solid var(--phosphor-dim);
        background: var(--panel-bg);
        padding: 8px 16px;
        font-size: 0.92rem;
    }

    .top-right-controls {
        display: flex;
        align-items: center;
        gap: 18px;
    }

    .metrics span {
        margin-inline-start: 14px;
        color: var(--phosphor-amber);
        font-weight: bold;
    }

    .lang-switch-btn {
        background: #17261a;
        border: 1px solid var(--phosphor-amber);
        color: var(--phosphor-amber);
        padding: 4px 10px;
        font-family: inherit;
        font-size: 0.82rem;
        font-weight: bold;
        cursor: pointer;
    }

    .lang-switch-btn:hover {
        background: var(--phosphor-amber);
        color: #000;
    }

    .workspace {
        display: grid;
        grid-template-columns: 1.05fr 1.35fr 1fr;
        gap: 12px;
        flex: 1;
        min-height: 0;
    }

    .panel {
        border: 1px solid var(--phosphor-dim);
        background: var(--panel-bg);
        display: flex;
        flex-direction: column;
        overflow: hidden;
    }

    .panel-header {
        background: #19241b;
        color: var(--phosphor-green);
        padding: 8px 12px;
        font-weight: bold;
        font-size: 0.85rem;
        border-bottom: 1px solid var(--phosphor-dim);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .panel-body {
        padding: 14px;
        overflow-y: auto;
        flex: 1;
    }

    /* Left Panel: Physical Wire Slip Look */
    .wire-document {
        background: var(--paper-beige);
        color: var(--paper-ink);
        padding: 18px;
        border-radius: 2px;
        box-shadow: 3px 3px 0px #000;
    }

    .wire-meta {
        border-bottom: 2px dashed #555;
        padding-bottom: 10px;
        margin-bottom: 12px;
        font-size: 0.84rem;
        line-height: 1.55;
    }

    .wire-domain {
        background: #222;
        color: #ffdf6b;
        padding: 2px 6px;
        font-weight: bold;
        direction: ltr;
        display: inline-block;
    }

    .wire-headline {
        font-size: 1.08rem;
        font-weight: bold;
        margin-bottom: 12px;
        line-height: 1.4;
    }

    .wire-body {
        font-size: 0.9rem;
        line-height: 1.65;
        white-space: pre-line;
    }

    /* Center Panel: SQLite FTS5 Search Terminal */
    .search-bar {
        display: flex;
        gap: 8px;
        margin-bottom: 10px;
    }

    .search-input {
        flex: 1;
        background: #060906;
        border: 1px solid var(--phosphor-green);
        color: var(--phosphor-green);
        padding: 10px;
        font-family: inherit;
        font-size: 0.92rem;
    }

    .search-btn {
        background: var(--phosphor-green);
        color: #000;
        border: none;
        padding: 0 18px;
        font-family: inherit;
        font-weight: bold;
        cursor: pointer;
    }

    .chip-bar {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        margin-bottom: 10px;
    }

    .query-chip {
        background: #17261a;
        border: 1px solid var(--phosphor-dim);
        color: #9ef0b3;
        font-size: 0.76rem;
        padding: 5px 9px;
        cursor: pointer;
        font-family: inherit;
        direction: ltr;
    }

    .query-chip:hover {
        border-color: var(--phosphor-green);
        background: #223827;
    }

    .result-card {
        border: 1px solid #29422e;
        background: #0c120d;
        padding: 10px;
        margin-bottom: 10px;
    }

    .result-title {
        color: var(--phosphor-amber);
        font-weight: bold;
        font-size: 0.9rem;
    }

    .result-meta {
        font-size: 0.76rem;
        color: #79a684;
        margin: 4px 0 6px 0;
    }

    .result-snippet {
        font-size: 0.85rem;
        line-height: 1.5;
        color: #d0f5d8;
    }

    /* Right Panel: Unreliable AI Co-Pilot */
    .ai-box {
        border: 1px dashed var(--phosphor-amber);
        background: rgba(255, 176, 0, 0.05);
        padding: 12px;
        color: var(--phosphor-amber);
        font-size: 0.86rem;
        line-height: 1.55;
    }

    .ai-badge {
        display: inline-block;
        padding: 4px 10px;
        font-weight: bold;
        margin-top: 8px;
        background: var(--phosphor-amber);
        color: #000;
    }

    /* Bottom Stamp Bar */
    .bottom-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border: 1px solid var(--phosphor-dim);
        background: var(--panel-bg);
        padding: 10px 18px;
    }

    .stamp-controls {
        display: flex;
        gap: 14px;
    }

    .stamp-btn {
        padding: 10px 24px;
        font-family: inherit;
        font-size: 1rem;
        font-weight: bold;
        cursor: pointer;
        border: 2px solid;
        letter-spacing: 0.5px;
    }

    .stamp-approve {
        background: rgba(51, 255, 102, 0.1);
        border-color: var(--phosphor-green);
        color: var(--phosphor-green);
    }
    .stamp-approve:hover { background: var(--phosphor-green); color: #000; }

    .stamp-reject {
        background: rgba(255, 59, 48, 0.1);
        border-color: var(--alert-red);
        color: var(--alert-red);
    }
    .stamp-reject:hover { background: var(--alert-red); color: #fff; }

    /* Modal Debrief */
    #modal-overlay {
        display: none;
        position: fixed;
        inset: 0;
        background: rgba(0, 0, 0, 0.85);
        z-index: 500;
        justify-content: center;
        align-items: center;
        padding: 20px;
    }

    .modal-card {
        border: 2px solid var(--phosphor-amber);
        background: var(--panel-bg);
        max-width: 680px;
        width: 100%;
        padding: 24px;
    }
</style>
</head>
<body class="crt-enabled">

    <!-- 1. STARTING WINDOW (PLAY, LANGUAGE, SETTINGS, EXIT) -->
    <div id="menu-screen" class="screen active">
        <div class="title-box">
            <h1 id="ui-menu-title">VERIFIED: NATIONAL DESK</h1>
            <div class="subtitle" id="ui-menu-subtitle">PUBLIC HEALTH MISINFORMATION & HEURISTIC VETTING TERMINAL</div>
            <button class="menu-btn" id="ui-btn-play" onclick="startLoadingSequence()">[ 1 ] PLAY // START SHIFT</button>
            <button class="menu-btn" id="ui-btn-lang" onclick="toggleLanguage()">[ 2 ] LANGUAGE // اللغة: ENGLISH (اضغط للتبديل إلى العربية)</button>
            <button class="menu-btn" id="crt-btn" onclick="toggleCRT()">[ 3 ] SETTINGS // CRT SCANLINES: ON</button>
            <button class="menu-btn" id="ui-btn-exit" onclick="shutdownTerminal()">[ 4 ] EXIT // SHUT DOWN</button>
        </div>
    </div>

    <!-- 2. TELETYPE LOADING SCREEN -->
    <div id="loading-screen" class="screen">
        <div id="teletype-log"></div>
    </div>

    <!-- 3. CORE GAMEPLAY DESK -->
    <div id="desk-screen" class="screen">
        <div class="top-bar">
            <div>
                <strong id="ui-lbl-terminal">TERMINAL:</strong> NATIONAL-DESK-01 //
                <strong id="ui-lbl-case">CASE:</strong> <span id="case-counter">1 / 3</span>
            </div>
            <div class="top-right-controls">
                <div class="metrics">
                    <span id="ui-lbl-accuracy">ACCURACY:</span> <span id="score-display">0</span>
                    <span id="ui-lbl-queries">QUERIES RUN:</span> <span id="queries-display">0</span>
                </div>
                <button class="lang-switch-btn" id="desk-lang-btn" onclick="toggleLanguage()">عربي / EN</button>
            </div>
        </div>

        <div class="workspace">
            <!-- LEFT: INCOMING WIRE -->
            <div class="panel">
                <div class="panel-header">
                    <span id="ui-hdr-wire">[ INCOMING WIRE SUBMISSION ]</span>
                    <span id="wire-code">CASE-01</span>
                </div>
                <div class="panel-body">
                    <div class="wire-document">
                        <div class="wire-meta">
                            <div><strong id="ui-meta-domain">DOMAIN:</strong> <span class="wire-domain" id="wire-domain"></span></div>
                            <div><strong id="ui-meta-outlet">OUTLET TYPE:</strong> <span id="wire-outlet"></span></div>
                            <div><strong id="ui-meta-author">AUTHOR:</strong> <span id="wire-author"></span></div>
                            <div><strong id="ui-meta-time">TIMESTAMP:</strong> <span id="wire-time"></span></div>
                        </div>
                        <div class="wire-headline" id="wire-headline"></div>
                        <div class="wire-body" id="wire-body"></div>
                    </div>
                </div>
            </div>

            <!-- CENTER: SQLITE FTS5 SEARCH ENGINE -->
            <div class="panel">
                <div class="panel-header">
                    <span id="ui-hdr-search">[ NATIONAL DESK FTS5 SEARCH ENGINE ]</span>
                    <span id="query-rating">IDLE</span>
                </div>
                <div class="panel-body">
                    <div class="search-bar">
                        <input type="text" id="search-input" class="search-input"
                               placeholder='Try: site:ox.ac.uk "Aris Thorne" or boolean AND / NOT'
                               onkeydown="if(event.key==='Enter') runSearch()">
                        <button class="search-btn" id="ui-btn-search" onclick="runSearch()">SEARCH</button>
                    </div>
                    <div id="ui-lbl-chips" style="font-size:0.75rem; color:#88b892; margin-bottom:6px;">
                        QUICK OPERATOR TEMPLATES (Click to populate or type your own query):
                    </div>
                    <div class="chip-bar" id="suggested-chips"></div>
                    <div id="search-results"></div>
                </div>
            </div>

            <!-- RIGHT: UNRELIABLE AI CO-PILOT -->
            <div class="panel">
                <div class="panel-header">
                    <span id="ui-hdr-ai">[ AUTO-ANALYST v0.9 // LOCAL LLM ]</span>
                    <span id="ui-ai-status" style="color:var(--phosphor-amber);">UNVERIFIED</span>
                </div>
                <div class="panel-body">
                    <div class="ai-box">
                        <div><strong id="ui-ai-lbl-model">MODEL:</strong> <span id="ai-model"></span></div>
                        <div style="margin-top:6px;"><strong id="ui-ai-lbl-conf">CONFIDENCE:</strong> <span id="ai-conf"></span></div>
                        <hr style="border:none; border-top:1px dashed var(--phosphor-amber); margin:10px 0;">
                        <div><strong id="ui-ai-lbl-sum">AUTO-SUMMARY & CITATION CHECK:</strong></div>
                        <p id="ai-summary" style="margin-top:6px;"></p>
                        <div style="margin-top:12px;">
                            <strong id="ui-ai-lbl-rec">RECOMMENDED STAMP:</strong><br>
                            <span class="ai-badge" id="ai-verdict"></span>
                        </div>
                    </div>
                    <div id="ui-ai-advisory" style="margin-top:14px; font-size:0.79rem; color:#9ab8a0; line-height:1.5;"></div>
                </div>
            </div>
        </div>

        <!-- BOTTOM CONTROLS -->
        <div class="bottom-bar">
            <div id="ui-bottom-prompt" style="font-size:0.86rem; color:var(--phosphor-amber);">
                INSPECT THE SOURCE DOMAIN, CROSS-EXAMINE THE AI, AND STAMP YOUR FINAL VERDICT:
            </div>
            <div class="stamp-controls">
                <button class="stamp-btn stamp-approve" id="ui-btn-approve" onclick="submitVerdict('APPROVE')">[ APPROVE // LEGIT ]</button>
                <button class="stamp-btn stamp-reject" id="ui-btn-reject" onclick="submitVerdict('REJECT')">[ REJECT // MISINFO ]</button>
            </div>
        </div>
    </div>

    <!-- DEBRIEF MODAL -->
    <div id="modal-overlay">
        <div class="modal-card">
            <h2 id="modal-title" style="margin-bottom:10px;"></h2>
            <div id="modal-heuristic" style="color:var(--phosphor-amber); font-size:0.88rem; margin-bottom:12px;"></div>
            <p id="modal-body" style="line-height:1.6; font-size:0.94rem; margin-bottom:20px;"></p>
            <button class="menu-btn" id="ui-btn-next" onclick="nextCase()" style="text-align:center;">[ CONTINUE TO NEXT WIRE ]</button>
        </div>
    </div>

<script>
    let currentLang = 'en';
    let crtOn = true;
    let cases = [];
    let currentIndex = 0;
    let score = 0;
    let queryCount = 0;
    let deskActive = false;

    const I18N = {
        en: {
            dir: "ltr",
            menuTitle: "VERIFIED: NATIONAL DESK",
            menuSubtitle: "PUBLIC HEALTH MISINFORMATION & HEURISTIC VETTING TERMINAL",
            btnPlay: "[ 1 ] PLAY // START SHIFT",
            btnLang: "[ 2 ] LANGUAGE // اللغة: ENGLISH (Click for Arabic)",
            btnCrtOn: "[ 3 ] SETTINGS // CRT SCANLINES: ON",
            btnCrtOff: "[ 3 ] SETTINGS // CRT SCANLINES: OFF",
            btnExit: "[ 4 ] EXIT // SHUT DOWN",
            shutdownMsg: "[ SIGNAL TERMINATED // TERMINAL POWERED OFF ]",
            loadingLines: [
                "CONNECTING TO NATIONAL DESK WIRE...",
                "MOUNTING IN-MEMORY SQLITE FTS5 FULL-TEXT SEARCH INDEX... [OK]",
                "INITIALIZING AUTO-ANALYST v0.9 (LOCAL SMALL LLM CO-PILOT)... [WARNING: UNCALIBRATED]",
                "LOADING DAILY PUBLIC HEALTH MANIFEST: 3 PENDING CASES...",
                "SHIFT BRIEFING: DISMANTLE HEURISTICS. VERIFY EVERY CITATION. DO NOT BLINDLY TRUST THE AI."
            ],
            lblTerminal: "TERMINAL:",
            lblCase: "CASE:",
            lblAccuracy: "ACCURACY:",
            lblQueries: "QUERIES RUN:",
            hdrWire: "[ INCOMING WIRE SUBMISSION ]",
            metaDomain: "DOMAIN:",
            metaOutlet: "OUTLET TYPE:",
            metaAuthor: "AUTHOR:",
            metaTime: "TIMESTAMP:",
            hdrSearch: "[ NATIONAL DESK FTS5 SEARCH ENGINE ]",
            idleStatus: "IDLE",
            searchPlaceholder: 'Try: site:ox.ac.uk "Aris Thorne" or boolean AND / NOT',
            btnSearch: "SEARCH",
            lblChips: "QUICK OPERATOR TEMPLATES (Click to populate or type your own query):",
            searchReady: "> Enter a search query above or click an operator template to inspect the evidence database.",
            noResults: "NO RECORDS MATCHED QUERY:",
            noResultsSub: "Try broadening terms or checking spelling.",
            lblSite: "SITE:",
            lblCategory: "CATEGORY:",
            lblDate: "DATE:",
            hdrAi: "[ AUTO-ANALYST v0.9 // LOCAL LLM ]",
            aiStatus: "UNVERIFIED",
            aiLblModel: "MODEL:",
            aiLblConf: "CONFIDENCE:",
            aiLblSum: "AUTO-SUMMARY & CITATION CHECK:",
            aiLblRec: "RECOMMENDED STAMP:",
            aiAdvisory: "<strong>DESK ADVISORY:</strong><br>AUTO-ANALYST v0.9 is a tiny 0.5B parameter language model. It frequently falls for medical jargon, hallucinates non-existent journal citations, or panics over missing cache IDs. <strong>Never rubber-stamp its verdict without querying the FTS5 terminal!</strong>",
            bottomPrompt: "INSPECT THE SOURCE DOMAIN, CROSS-EXAMINE THE AI, AND STAMP YOUR FINAL VERDICT:",
            btnApprove: "[ APPROVE // LEGIT ]",
            btnReject: "[ REJECT // MISINFO ]",
            verdictLabels: { "APPROVE": "APPROVE", "REJECT": "REJECT" },
            modalCorrect: "[ VERDICT CORRECT // STAMPED:",
            modalFailed: "[ VERDICT FAILED // STAMPED:",
            modalExpected: "EXPECTED:",
            modalTargetBias: "TARGET COGNITIVE BIAS:",
            modalAiFlaw: "AI FLAW:",
            btnNext: "[ CONTINUE TO NEXT WIRE ]",
            shiftComplete: "SHIFT COMPLETE! Final Accuracy:"
        },
        ar: {
            dir: "rtl",
            menuTitle: "مُوثَّق: المكتب الوطني للتحقق",
            menuSubtitle: "محطة التحقق من التضليل الصحي وتفكيك الانحيازات الإدراكية",
            btnPlay: "[ 1 ] ابدأ المناوبة // PLAY",
            btnLang: "[ 2 ] اللغة // LANGUAGE: العربية (اضغط للتبديل إلى الإنجليزية)",
            btnCrtOn: "[ 3 ] الإعدادات // خطوط شاشة CRT: مفعلة",
            btnCrtOff: "[ 3 ] الإعدادات // خطوط شاشة CRT: معطلة",
            btnExit: "[ 4 ] إيقاف التشغيل // EXIT",
            shutdownMsg: "[ تم قطع الإشارة // إيقاف تشغيل المحطة ]",
            loadingLines: [
                "جاري الاتصال ببرقيات المكتب الوطني للأخبار...",
                "تجهيز محرك البحث النصي الكامل SQLite FTS5 في الذاكرة... [تم بنجاح]",
                "تشغيل المساعد الذكي المحلي AUTO-ANALYST v0.9... [تحذير: النموذج غير معياري]",
                "تحميل ملف قضايا الصحة العامة اليومي: 3 قضايا قيد المراجعة...",
                "تعليمات المناوبة: فكك الخدع الذهنية، تحقق من كل مصدر، ولا تثق بالذكاء الاصطناعي بشكل أعمى."
            ],
            lblTerminal: "المحطة:",
            lblCase: "القضية:",
            lblAccuracy: "الدقة:",
            lblQueries: "عمليات البحث:",
            hdrWire: "[ البرقية الإخبارية الواردة ]",
            metaDomain: "النطاق الإلكتروني:",
            metaOutlet: "نوع المنصة:",
            metaAuthor: "الكاتب / المصدر:",
            metaTime: "التوقيت:",
            hdrSearch: "[ محرك بحث المكتب الوطني SQLite FTS5 ]",
            idleStatus: "جاهز",
            searchPlaceholder: 'جرّب مثلاً: site:ox.ac.uk "آريس ثورن" أو معاملات AND / NOT',
            btnSearch: "بحث",
            lblChips: "قوالب البحث المتقدم السريعة (اضغط للتجربة أو اكتب استعلامك الخاص):",
            searchReady: "> أدخل استعلام البحث أعلاه أو اضغط على أحد القوالب الجاهزة لفحص قاعدة بيانات الأدلة.",
            noResults: "لا توجد سجلات مطابقة للاستعلام:",
            noResultsSub: "حاول توسيع كلمات البحث أو التأكد من الإملاء.",
            lblSite: "الموقع:",
            lblCategory: "التصنيف:",
            lblDate: "التاريخ:",
            hdrAi: "[ المحلل الآلي v0.9 // نموذج لغوي محلي ]",
            aiStatus: "غير موثق",
            aiLblModel: "النموذج:",
            aiLblConf: "درجة الثقة:",
            aiLblSum: "الملخص الآلي وفحص الاستشهادات:",
            aiLblRec: "التوصية الآلية:",
            aiAdvisory: "<strong>تنبيه مكتب التحقيقات:</strong><br>المحلل الآلي v0.9 هو نموذج لغوي محلي صغير جداً (0.5B). كثيراً ما ينخدع بالمصطلحات الطبية المعقدة، أو يهلوس بمجلات علمية وهمية، أو يرفض أبحاثاً حقيقية بسبب نقص ذاكرته. <strong>لا تعتمد توصيته أبداً دون التحقق عبر محرك بحث FTS5!</strong>",
            bottomPrompt: "افحص النطاق الإلكتروني، اختبر ادعاءات الذكاء الاصطناعي، واختم قرارك النهائي:",
            btnApprove: "[ اعتماد // خبر موثوق ]",
            btnReject: "[ رفض // تضليل إعلامي ]",
            verdictLabels: { "APPROVE": "اعتماد (APPROVE)", "REJECT": "رفض (REJECT)" },
            modalCorrect: "[ قرار صحيح // تم ختم:",
            modalFailed: "[ قرار خاطئ // تم ختم:",
            modalExpected: "الصحيح هو:",
            modalTargetBias: "الانحياز الإدراكي المستهدف:",
            modalAiFlaw: "خلل الذكاء الاصطناعي:",
            btnNext: "[ الانتقال إلى البرقية التالية ]",
            shiftComplete: "اكتملت المناوبة! الدقة النهائية:"
        }
    };

    function applyLocalization() {
        const t = I18N[currentLang];
        document.documentElement.lang = currentLang;
        document.documentElement.dir = t.dir;

        document.getElementById('ui-menu-title').innerText = t.menuTitle;
        document.getElementById('ui-menu-subtitle').innerText = t.menuSubtitle;
        document.getElementById('ui-btn-play').innerText = t.btnPlay;
        document.getElementById('ui-btn-lang').innerText = t.btnLang;
        document.getElementById('crt-btn').innerText = crtOn ? t.btnCrtOn : t.btnCrtOff;
        document.getElementById('ui-btn-exit').innerText = t.btnExit;

        document.getElementById('ui-lbl-terminal').innerText = t.lblTerminal;
        document.getElementById('ui-lbl-case').innerText = t.lblCase;
        document.getElementById('ui-lbl-accuracy').innerText = t.lblAccuracy;
        document.getElementById('ui-lbl-queries').innerText = t.lblQueries;

        document.getElementById('ui-hdr-wire').innerText = t.hdrWire;
        document.getElementById('ui-meta-domain').innerText = t.metaDomain;
        document.getElementById('ui-meta-outlet').innerText = t.metaOutlet;
        document.getElementById('ui-meta-author').innerText = t.metaAuthor;
        document.getElementById('ui-meta-time').innerText = t.metaTime;

        document.getElementById('ui-hdr-search').innerText = t.hdrSearch;
        document.getElementById('search-input').placeholder = t.searchPlaceholder;
        document.getElementById('ui-btn-search').innerText = t.btnSearch;
        document.getElementById('ui-lbl-chips').innerText = t.lblChips;

        document.getElementById('ui-hdr-ai').innerText = t.hdrAi;
        document.getElementById('ui-ai-status').innerText = t.aiStatus;
        document.getElementById('ui-ai-lbl-model').innerText = t.aiLblModel;
        document.getElementById('ui-ai-lbl-conf').innerText = t.aiLblConf;
        document.getElementById('ui-ai-lbl-sum').innerText = t.aiLblSum;
        document.getElementById('ui-ai-lbl-rec').innerText = t.aiLblRec;
        document.getElementById('ui-ai-advisory').innerHTML = t.aiAdvisory;

        document.getElementById('ui-bottom-prompt').innerText = t.bottomPrompt;
        document.getElementById('ui-btn-approve').innerText = t.btnApprove;
        document.getElementById('ui-btn-reject').innerText = t.btnReject;
        document.getElementById('ui-btn-next').innerText = t.btnNext;
    }

    async function toggleLanguage() {
        currentLang = (currentLang === 'en') ? 'ar' : 'en';
        applyLocalization();
        if (deskActive) {
            const res = await fetch('/api/cases?lang=' + currentLang);
            cases = await res.json();
            loadCase(currentIndex);
        }
    }

    function showScreen(id) {
        document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
        document.getElementById(id).classList.add('active');
    }

    function toggleCRT() {
        document.body.classList.toggle('crt-enabled');
        crtOn = document.body.classList.contains('crt-enabled');
        applyLocalization();
    }

    function shutdownTerminal() {
        const msg = I18N[currentLang].shutdownMsg;
        document.body.innerHTML = `<div style="display:flex;height:100vh;align-items:center;justify-content:center;color:#33ff66;font-family:monospace;"><h2>${msg}</h2></div>`;
    }

    async function startLoadingSequence() {
        showScreen('loading-screen');
        const res = await fetch('/api/cases?lang=' + currentLang);
        cases = await res.json();

        const lines = I18N[currentLang].loadingLines;
        const log = document.getElementById('teletype-log');
        log.innerHTML = "";
        for (let i = 0; i < lines.length; i++) {
            await new Promise(r => setTimeout(r, 380));
            log.innerHTML += `<div>> ${lines[i]}</div>`;
        }
        await new Promise(r => setTimeout(r, 500));
        currentIndex = 0;
        score = 0;
        queryCount = 0;
        deskActive = true;
        loadCase(currentIndex);
        showScreen('desk-screen');
    }

    function loadCase(idx) {
        const c = cases[idx];
        const t = I18N[currentLang];

        document.getElementById('case-counter').innerText = `${idx + 1} / ${cases.length}`;
        document.getElementById('score-display').innerText = `${score} / ${idx}`;
        document.getElementById('wire-code').innerText = c.code;
        document.getElementById('wire-domain').innerText = c.source_domain;
        document.getElementById('wire-outlet').innerText = c.outlet_type;
        document.getElementById('wire-author').innerText = c.author;
        document.getElementById('wire-time').innerText = c.timestamp;
        document.getElementById('wire-headline').innerText = c.headline;
        document.getElementById('wire-body').innerText = c.body;

        document.getElementById('ai-model').innerText = c.ai_copilot.model;
        document.getElementById('ai-conf').innerText = c.ai_copilot.confidence;
        document.getElementById('ai-summary').innerText = c.ai_copilot.summary;
        document.getElementById('ai-verdict').innerText = t.verdictLabels[c.ai_copilot.recommended_verdict];

        document.getElementById('search-input').value = '';
        document.getElementById('query-rating').innerText = t.idleStatus;
        document.getElementById('search-results').innerHTML =
            `<div style="color:#6c8c72; font-size:0.85rem; margin-top:12px;">${t.searchReady}</div>`;

        const chipBox = document.getElementById('suggested-chips');
        chipBox.innerHTML = '';
        c.suggested_queries.forEach(q => {
            const btn = document.createElement('button');
            btn.className = 'query-chip';
            btn.innerText = q;
            btn.onclick = () => {
                document.getElementById('search-input').value = q;
                runSearch();
            };
            chipBox.appendChild(btn);
        });
    }

    async function runSearch() {
        const t = I18N[currentLang];
        const q = document.getElementById('search-input').value;
        const res = await fetch(`/api/search?lang=${currentLang}&q=${encodeURIComponent(q)}`);
        const data = await res.json();
        queryCount++;
        document.getElementById('queries-display').innerText = queryCount;
        document.getElementById('query-rating').innerText = data.query_score;

        const container = document.getElementById('search-results');
        if (!data.syntax_valid) {
            container.innerHTML = `<div class="result-card" style="border-color:var(--alert-red);color:var(--alert-red);">${data.error}</div>`;
            return;
        }
        if (data.results.length === 0) {
            container.innerHTML = `<div class="result-card">${t.noResults} <strong>${q}</strong>. ${t.noResultsSub}</div>`;
            return;
        }
        container.innerHTML = data.results.map(r => `
            <div class="result-card">
                <div class="result-title">${r.title}</div>
                <div class="result-meta">
                    <strong>${t.lblSite}</strong> <span style="direction:ltr;display:inline-block;">${r.site}</span> |
                    <strong>${t.lblCategory}</strong> ${r.category} |
                    <strong>${t.lblDate}</strong> ${r.date}
                </div>
                <div class="result-snippet">${r.snippet}</div>
            </div>
        `).join('');
    }

    function submitVerdict(playerVerdict) {
        const c = cases[currentIndex];
        const t = I18N[currentLang];
        const correct = (playerVerdict === c.correct_verdict);
        if (correct) score++;

        const stampedText = t.verdictLabels[playerVerdict];
        const expectedText = t.verdictLabels[c.correct_verdict];

        const titleEl = document.getElementById('modal-title');
        titleEl.innerText = correct
            ? `${t.modalCorrect} ${stampedText} ]`
            : `${t.modalFailed} ${stampedText} (${t.modalExpected} ${expectedText}) ]`;
        titleEl.style.color = correct ? 'var(--phosphor-green)' : 'var(--alert-red)';

        document.getElementById('modal-heuristic').innerText =
            `${t.modalTargetBias} ${c.heuristic_tested} | ${t.modalAiFlaw} ${c.ai_copilot.hallucination_type}`;
        document.getElementById('modal-body').innerText = c.debrief;
        document.getElementById('modal-overlay').style.display = 'flex';
    }

    function nextCase() {
        const t = I18N[currentLang];
        document.getElementById('modal-overlay').style.display = 'none';
        currentIndex++;
        if (currentIndex < cases.length) {
            loadCase(currentIndex);
        } else {
            alert(`${t.shiftComplete} ${score} / ${cases.length} | ${t.lblQueries} ${queryCount}`);
            deskActive = false;
            showScreen('menu-screen');
        }
    }

    // Initialize UI text on load
    applyLocalization();
</script>
</body>
</html>
"""


# ------------------------------------------------------------------------------
# 4. LIGHTWEIGHT HTTP APPLICATION SERVER
# ------------------------------------------------------------------------------
db_engine = NationalDeskDB()

class NationalDeskHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        lang = params.get("lang", ["en"])[0]
        if lang not in ("en", "ar"):
            lang = "en"

        if parsed.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_CLIENT.encode("utf-8"))

        elif parsed.path == "/api/cases":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(CASES_MANIFEST[lang], ensure_ascii=False).encode("utf-8"))

        elif parsed.path == "/api/search":
            q = params.get("q", [""])[0]
            result = db_engine.execute_search(q, lang=lang)
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(result, ensure_ascii=False).encode("utf-8"))

        else:
            self.send_response(404)
            self.end_headers()


if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 1111
    print("==================================================================")
    print(" VERIFIED: NATIONAL DESK // BILINGUAL (EN/AR) FTS5 SERVER ONLINE")
    print(f" Open your browser to: http://{HOST}:{PORT}")
    print(" Press Ctrl+C to shut down.")
    print("==================================================================")
    server = HTTPServer((HOST, PORT), NationalDeskHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[TERMINAL OFFLINE]")
        server.server_close()
