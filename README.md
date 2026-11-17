# 🏫 K-12 School District Performance & Educational ROI Database

An end-to-end data engineering and relational SQL analytics pipeline linking federal **NCES F-33 School District Finance Survey** records with **EDFacts State Assessment** proficiency data (FY 2021–2022) to evaluate whether higher per-pupil classroom spending correlates with stronger student outcomes in Mathematics and Reading/Language Arts (ELA)[cite: 2, 3].

---

## 📌 Research Question
> **Does higher per-pupil instructional spending actually translate into higher student academic proficiency, or do classroom budget allocation efficiency and district characteristics play a larger role in educational ROI?**

---

## 📂 Repository Structure

| File | Description |
| :--- | :--- |
| `ETL-Proj.ipynb` | Python (`pandas`) data cleaning, standardization, and merging pipeline processing raw federal finance and assessment archives into a clean 7,726-district dataset. |
| `Sql Setup` | PostgreSQL DDL script defining the isolated `k12_education` schema and Third Normal Form (3NF) tables (`districts`, `district_finances`, `district_assessments`). |
| `queries_roi.sql` | Core analytical SQL suite evaluating per-pupil instructional ROI, classroom budget allocation efficiency, within-state window rankings (`DENSE_RANK`), and national spending quartiles (`NTILE`). |
| `queries_regional.sql` | State-level benchmarking and district size/efficiency comparative queries. |
| `queries_subjects.sql` | Subject-level performance splits comparing Math vs. ELA funding responsiveness and district rankings[cite: 1]. |
| `sdf22_2a.zip` | Raw NCES F-33 School District Finance Survey archive (FY 2022)[cite: 1]. |
| `EDFacts_2022_District_math.zip` | Raw U.S. Department of Education EDFacts District Mathematics assessment archive (SY 2021–2022)[cite: 1]. |
| `EDFacts_2022_District_ela.zip` | Raw U.S. Department of Education EDFacts District Reading/Language Arts assessment archive (SY 2021–2022)[cite: 1]. |

---

## 🛠️ Data Pipeline & ETL Architecture

1. **Key Standardization:** Standardized the 7-character zero-padded `LEAID` (Local Education Agency ID) across all three federal datasets to ensure lossless relational joins[cite: 3].
2. **Survey Code & Suppression Handling:** Filtered out invalid/missing NCES survey codes and normalized EDFacts privacy-suppressed score intervals into clean numeric values with an explicit `is_suppressed` boolean flag[cite: 3].
3. **Granularity Alignment:** Isolated district-wide aggregate rows (`All Students` / `All Grades`) to prevent duplicate join fan-out[cite: 3].
4. **Matched Cohort:** Confirmed an exact inner-join match of **7,726 U.S. public school districts** across Finance, Math, and ELA datasets[cite: 3].

---

## 🗄️ Database Schema (`k12_education` — 3NF)

Hosted on **Supabase (PostgreSQL)** inside an isolated `k12_education` schema[cite: 1, 3]:

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
