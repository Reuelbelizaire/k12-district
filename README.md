# 🏫 K-12 School District Performance & Educational ROI Database

An end-to-end data engineering, relational SQL analytics pipeline, and interactive **Streamlit** dashboard linking federal **NCES F-33 School District Finance Survey** records with **EDFacts State Assessment** proficiency data (FY 2021–2022) to evaluate whether higher per-pupil classroom spending correlates with stronger student outcomes in Mathematics and Reading/Language Arts (ELA).

---

## 📌 Research Question
> **Does higher per-pupil instructional spending actually translate into higher student academic proficiency, or do classroom budget allocation efficiency and district characteristics play a larger role in educational ROI?**

---

## 📂 Repository Structure

| File | Description |
| :--- | :--- |
| `app.py` | Interactive Streamlit dashboard connected live to Supabase (`k12_education`), featuring school-themed KPI cards, an interactive U.S. Choropleth map with state-to-district drill-down, and Plotly ROI/subject charts. |
| `db.py` | Cached SQLAlchemy + `psycopg2-binary` database connector executing parameterized read-only SQL queries against PostgreSQL. |
| `ETL-Proj.ipynb` | Python (`pandas`) data cleaning, standardization, and merging pipeline processing raw federal finance and assessment archives into a clean 7,726-district dataset. |
| `Sql Setup` | PostgreSQL DDL script defining the isolated `k12_education` schema and Third Normal Form (3NF) tables (`districts`, `district_finances`, `district_assessments`). |
| `queries_roi.sql` | Core analytical SQL suite evaluating per-pupil instructional ROI, classroom budget allocation efficiency, within-state window rankings (`DENSE_RANK`), and national spending quartiles (`NTILE`). |
| `queries_regional.sql` | State-level benchmarking and district size/efficiency comparative queries. |
| `queries_subjects.sql` | Subject-level performance splits comparing Math vs. ELA funding responsiveness and district rankings. |
| `requirements.txt` | Python package dependencies (`streamlit`, `streamlit-antd-components`, `pandas`, `sqlalchemy`, `psycopg2-binary`, `plotly`, `python-dotenv`). |
| `sdf22_2a.zip` | Raw NCES F-33 School District Finance Survey archive (FY 2022). |
| `EDFacts_2022_District_math.zip` | Raw U.S. Department of Education EDFacts District Mathematics assessment archive (SY 2021–2022). |
| `EDFacts_2022_District_ela.zip` | Raw U.S. Department of Education EDFacts District Reading/Language Arts assessment archive (SY 2021–2022). |

---

## 🛠️ Data Pipeline & ETL Architecture

1. **Key Standardization:** Standardized the 7-character zero-padded `LEAID` (Local Education Agency ID) across all three federal datasets to ensure lossless relational joins.
2. **Survey Code & Suppression Handling:** Filtered out invalid/missing NCES survey codes and normalized EDFacts privacy-suppressed score intervals into clean numeric values with an explicit `is_suppressed` boolean flag.
3. **Granularity Alignment:** Isolated district-wide aggregate rows (`All Students` / `All Grades`) to prevent duplicate join fan-out.
4. **Matched Cohort:** Confirmed an exact inner-join match of **7,726 U.S. public school districts** across Finance, Math, and ELA datasets (`7,723` active districts with positive operational denominators).

---

## ✨ Interactive Dashboard Highlights (`app.py`)

- **Live SQL Filtering:** Dynamically queries Supabase using parameterized SQLAlchemy queries by **State**, **Minimum Student Enrollment (`fall_membership`)**, and **Privacy-Suppression Exclusion (`is_suppressed = FALSE`)**.
- **School-Themed KPI Ribbon:** Real-time summary cards tracking Active Districts, Average Instructional Spending per Pupil, Classroom Budget Share (%), and Combined Proficiency Rate (%).
- **Regional Benchmarking Tab:** Interactive U.S. State Choropleth map with automatic state drill-down (plotting every individual district when a specific state is selected) alongside district enrollment tier box plots.
- **Educational ROI & Quartiles Tab:** Per-pupil instructional spending vs. proficiency scatter analysis and National Spending Quartile (`NTILE(4)`) comparisons.
- **Math vs. ELA Subject Splits Tab:** Side-by-side subject proficiency comparisons and distribution violin plots.

---

## 📊 Analytical SQL Highlights

- **Per-Pupil Instructional ROI (`queries_roi.sql`):** Computes classroom spending per student ($\frac{\text{instructional\_expenditure}}{\text{fall\_membership}}$) using `NULLIF` division-by-zero protection and filters out micro-district outliers (`fall_membership > 500`) and privacy-suppressed scores.
- **Classroom Budget Efficiency (`queries_roi.sql`):** Uses `GROUP BY` and `HAVING COUNT(assessment_id) = 2` to measure the exact share of total operational expenditure reaching classrooms (`instructional_pct`) alongside combined Math/ELA average proficiency.
- **Within-State Window Rankings (`queries_roi.sql`):** Uses Common Table Expressions (`WITH`) and `DENSE_RANK() OVER (PARTITION BY state_fips ...)` to compare each district's academic rank directly against its spending rank within its own state.
- **National Spending Quartiles (`queries_roi.sql`):** Uses `NTILE(4)` to segment districts nationwide into four equal instructional spending tiers and compare average proficiency across tiers.
- **Regional & Subject Splits (`queries_regional.sql`, `queries_subjects.sql`):** Evaluates state-level efficiency metrics and isolates whether funding impacts Math proficiency differently than ELA proficiency.

---

## 🗄️ Database Schema (`k12_education` — 3NF)

Hosted on **Supabase (PostgreSQL)** inside an isolated `k12_education` schema:

```text
k12_education.districts (Parent Dimension)
├── leaid (VARCHAR(7), PK)
├── district_name (TEXT)
└── state_fips (VARCHAR(2))
       │
       ├──< k12_education.district_finances (Fact Table)
       │    ├── leaid (FK -> districts.leaid)
       │    ├── fiscal_year (INT)
       │    ├── fall_membership (INT)
       │    ├── instructional_expenditure (NUMERIC)
       │    └── total_expenditure (NUMERIC)
       │
       └──< k12_education.district_assessments (Fact Table)
            ├── assessment_id (SERIAL, PK)
            ├── leaid (FK -> districts.leaid)
            ├── school_year (VARCHAR)
            ├── subject (VARCHAR: 'MATH' | 'ELA')
            ├── proficiency_rate (NUMERIC)
            └── is_suppressed (BOOLEAN)
```

---

## 🚀 Getting Started

1. **Clone the repository & activate the virtual environment:**
   ```powershell
   git clone https://github.com/Reuelbelizaire/k12-district.git
   cd k12-district
   python -m venv .school
   .school\Scripts\Activate.ps1
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure `.env`:** Create a `.env` file in the project root with your Supabase PostgreSQL pooler URI:
   ```env
   DATABASE_URL="postgresql://postgres.<project-ref>:<your-password>@aws-0-us-east-1.pooler.supabase.com:6543/postgres"
   ```
4. **Verify database connection & launch the dashboard:**
   ```bash
   python db.py
   streamlit run app.py
   ```

---

## 👥 Contributors

- **Reuel Belizaire** — ETL Pipeline, 3NF Database Schema, Core ROI, and Window Function Queries (`queries_roi.sql`)
- **Emily Gerdin** — Regional & District Efficiency Queries (`queries_regional.sql`)
- **Cyncier Harrison** — Subject Splits & Rankings Queries (`queries_subjects.sql`)
