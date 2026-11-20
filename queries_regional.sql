--- State & District Size Benchmarking

--- State Bang for Buck Efficiency Rating
WITH district_roi AS (
    SELECT 
        d.state_fips,
        f.leaid, 
        f.fall_membership,
        f.instructional_expenditure,
        (f.instructional_expenditure / NULLIF(f.fall_membership, 0)) AS per_pupil_spending,
        AVG(a.proficiency_rate) AS avg_district_proficiency
    FROM k12_education.districts d
    JOIN k12_education.district_finances f ON d.leaid = f.leaid
    JOIN k12_education.district_assessments a ON d.leaid = a.leaid
    WHERE a.is_suppressed = FALSE
    GROUP BY d.state_fips, f.leaid, f.fall_membership, f.instructional_expenditure
)
SELECT 
    state_fips,
    COUNT(leaid) AS num_districts,
    ROUND(AVG(per_pupil_spending), 2) AS state_avg_per_pupil_spending,
    ROUND(AVG(avg_district_proficiency), 2) AS state_avg_proficiency,
    ROUND((AVG(avg_district_proficiency) / NULLIF(AVG(per_pupil_spending), 0)) * 1000, 2) AS bang_for_buck_index
FROM district_roi
GROUP BY state_fips
ORDER BY bang_for_buck_index DESC;

--- District Tier Spending vs. Proficiency Summary
WITH district_metrics AS (
    SELECT 
        f.leaid,
        f.fall_membership,
        (f.instructional_expenditure / NULLIF(f.fall_membership, 0)) AS per_pupil_spending,
        AVG(a.proficiency_rate) AS avg_proficiency
    FROM k12_education.district_finances f
    JOIN k12_education.district_assessments a ON f.leaid = a.leaid
    WHERE a.is_suppressed = FALSE
    GROUP BY f.leaid, f.fall_membership, f.instructional_expenditure
),
tiered_districts AS (
    SELECT 
        leaid,
        fall_membership,
        per_pupil_spending,
        avg_proficiency,
        CASE 
            WHEN fall_membership < 1000 THEN '1. Small Rural (< 1,000 students)'
            WHEN fall_membership BETWEEN 1000 AND 10000 THEN '2. Mid-Size (1,000 - 10,000 students)'
            WHEN fall_membership > 10000 THEN '3. Large Urban (> 10,000 students)'
            ELSE 'Unknown'
        END AS district_size_tier
    FROM district_metrics
)
SELECT 
    district_size_tier,
    COUNT(leaid) AS total_districts,
    ROUND(AVG(per_pupil_spending), 2) AS avg_per_pupil_spending,
    ROUND(AVG(avg_proficiency), 2) AS avg_proficiency,
    ROUND((AVG(avg_proficiency) / NULLIF(AVG(per_pupil_spending), 0)) * 1000, 2) AS roi_index
FROM tiered_districts
GROUP BY district_size_tier
ORDER BY district_size_tier ASC;
