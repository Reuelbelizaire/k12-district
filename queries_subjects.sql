--- Math vs. ELA Subject Splits & Rankings

-- K-12 School District Performance & ROI Database
-- Cyncier Harrison: Subject Comparisons and District Rankings
-- School Year 2021-2022 / Fiscal Year 2022


-- QUERY 1: Compare Math vs. ELA Proficiency

SELECT
    subject,
    COUNT(*) AS total_assessments,
    ROUND(AVG(proficiency_rate), 2) AS avg_proficiency
FROM k12_education.district_assessments
WHERE proficiency_rate IS NOT NULL
  AND school_year = '2021-2022'
GROUP BY subject
ORDER BY avg_proficiency DESC;


-- QUERY 2: Spending vs. Math and ELA Performance

SELECT
    a.subject,
    COUNT(*) AS total_districts,
    ROUND(AVG(
        f.instructional_expenditure /
        NULLIF(f.fall_membership, 0)
    ), 2) AS avg_spending_per_student,
    ROUND(AVG(a.proficiency_rate), 2) AS avg_proficiency,
    ROUND(
        CORR(
            (f.instructional_expenditure /
             NULLIF(f.fall_membership, 0))::DOUBLE PRECISION,
            a.proficiency_rate::DOUBLE PRECISION
        )::NUMERIC, 3
    ) AS spending_proficiency_correlation
FROM k12_education.district_assessments a
JOIN k12_education.district_finances f
    ON a.leaid = f.leaid
WHERE a.school_year = '2021-2022'
  AND f.fiscal_year = '22'
  AND f.fall_membership > 0
  AND f.instructional_expenditure >= 0
  AND a.proficiency_rate IS NOT NULL
GROUP BY a.subject
ORDER BY a.subject;


-- QUERY 3: Rank Districts Within Each State

SELECT
    d.leaid,
    d.district_name,
    d.state_fips,
    a.subject,
    a.proficiency_rate,

    DENSE_RANK() OVER (
        PARTITION BY d.state_fips, a.subject
        ORDER BY a.proficiency_rate DESC
    ) AS state_rank

FROM k12_education.districts d

JOIN k12_education.district_assessments a
    ON d.leaid = a.leaid

WHERE a.school_year = '2021-2022'
  AND a.proficiency_rate IS NOT NULL

ORDER BY d.state_fips, a.subject, state_rank;


-- QUERY 4: District Performance Quartiles

WITH ranked_districts AS (
    SELECT
        d.leaid,
        d.district_name,
        d.state_fips,
        a.subject,
        a.proficiency_rate,

        NTILE(4) OVER (
            PARTITION BY d.state_fips, a.subject
            ORDER BY a.proficiency_rate DESC, d.leaid
        ) AS performance_quartile

    FROM k12_education.districts d

    JOIN k12_education.district_assessments a
        ON d.leaid = a.leaid

    WHERE a.school_year = '2021-2022'
      AND a.proficiency_rate IS NOT NULL
)

SELECT
    district_name,
    state_fips,
    subject,
    proficiency_rate,
    performance_quartile,

    CASE
        WHEN performance_quartile = 1 THEN 'Top 25%'
        WHEN performance_quartile = 2 THEN 'Upper Middle'
        WHEN performance_quartile = 3 THEN 'Lower Middle'
        ELSE 'Bottom 25%'
    END AS performance_category

FROM ranked_districts

ORDER BY state_fips, subject, performance_quartile;
