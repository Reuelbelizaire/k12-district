-- Query 1: Per-Pupil Instructional Spending vs. Proficiency
Select d.district_name,d.state_fips,da.subject, da.proficiency_rate, df.fall_membership,ROUND(df.instructional_expenditure/nullif(df.fall_membership,0),2) AS ROI
FROM k12_education.districts d 
JOIN k12_education.district_finances df on df.leaid = d.leaid
JOIN k12_education.district_assessments da on da.leaid = df.leaid
WHERE da.is_suppressed IS NOT TRUE AND df.fall_membership >500
ORDER BY ROI DESC;

--- Query 2: Budget Allocation Efficiency
select d.district_name,d.state_fips, df.instructional_expenditure, df.total_expenditure,ROUND(df.instructional_expenditure/nullif(df.total_expenditure,0)*100,2) AS instructional_pct,ROUND(AVG(da.proficiency_rate), 2) AS avg_proficiency
FROM k12_education.districts d 
JOIN k12_education.district_finances df on df.leaid = d.leaid
JOIN k12_education.district_assessments da on da.leaid = df.leaid
WHERE da.is_suppressed IS NOT TRUE
GROUP BY d.district_name, d.state_fips, df.instructional_expenditure, df.total_expenditure
HAVING COUNT (da.assessment_id) = 2
ORDER BY instructional_pct DESC;


-- Query 3: Within-State Proficiency & Spending Rankings (Window Functions)
WITH district_summary AS (
  SELECT d.district_name,d.state_fips, ROUND(df.instructional_expenditure/nullif(df.fall_membership,0),2) AS per_pupil_instructional, ROUND(AVG(da.proficiency_rate), 2) AS avg_proficiency
FROM k12_education.districts d 
JOIN k12_education.district_finances df on df.leaid = d.leaid
JOIN k12_education.district_assessments da on da.leaid = df.leaid
WHERE da.is_suppressed IS NOT TRUE AND df.fall_membership >500
GROUP BY d.district_name, d.state_fips, df.instructional_expenditure, df.fall_membership
HAVING COUNT (da.assessment_id) = 2
) SELECT district_name,state_fips,per_pupil_instructional,avg_proficiency,
 DENSE_RANK() OVER (PARTITION BY state_fips ORDER BY avg_proficiency DESC) AS state_proficiency_rank,
 DENSE_RANK() OVER (PARTITION BY state_fips ORDER BY per_pupil_instructional DESC) AS state_spending_rank
 FROM district_summary
 ORDER BY state_fips, state_proficiency_rank, state_spending_rank;

-- Query 4: National Spending Quartiles vs. Average Proficiency (NTILE)
WITH district_summary AS (
  SELECT d.district_name,d.state_fips, ROUND(df.instructional_expenditure/nullif(df.fall_membership,0),2) AS per_pupil_instructional, ROUND(AVG(da.proficiency_rate), 2) AS avg_proficiency
FROM k12_education.districts d 
JOIN k12_education.district_finances df on df.leaid = d.leaid
JOIN k12_education.district_assessments da on da.leaid = df.leaid
WHERE da.is_suppressed IS NOT TRUE AND df.fall_membership >500
GROUP BY d.district_name, d.state_fips, df.instructional_expenditure, df.fall_membership
HAVING COUNT (da.assessment_id) = 2
), spending_tiers AS (
  select per_pupil_instructional,
  avg_proficiency,
  NTILE(4) OVER (ORDER BY per_pupil_instructional ASC) AS spending_quartile --- (1 = Lowest 25% spenders, 4 = Highest 25% spenders)
  FROM district_summary
)
  SELECT spending_quartile,
  count(*) AS distinct_count,
  ROUND(AVG(per_pupil_instructional), 2) AS avg_spending,
  ROUND(AVG(avg_proficiency), 2) AS tier_avg_proficiency
  FROM spending_tiers
  GROUP BY spending_quartile
  ORDER BY spending_quartile;

