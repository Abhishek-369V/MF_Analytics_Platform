-- ============================================================
-- BLUESTOCK MF ANALYTICS — 10 ANALYTICAL SQL QUERIES
-- Day 2: Business Analysis Queries
-- ============================================================

-- Q1: Top 5 funds by AUM
SELECT scheme_name, fund_house, aum_crore
FROM fact_performance
ORDER BY aum_crore DESC
LIMIT 5;

-- Q2: Average NAV per month for each fund
SELECT 
    f.scheme_name,
    strftime('%Y-%m', n.date) AS month,
    ROUND(AVG(n.nav), 4) AS avg_nav
FROM fact_nav n
JOIN dim_fund f ON n.amfi_code = f.amfi_code
GROUP BY f.scheme_name, month
ORDER BY f.scheme_name, month;

-- Q3: SIP inflow YoY growth
SELECT 
    month,
    sip_inflow_crore,
    yoy_growth_pct,
    ROUND((sip_inflow_crore - LAG(sip_inflow_crore, 12) 
        OVER (ORDER BY month)) * 100.0 / 
        LAG(sip_inflow_crore, 12) OVER (ORDER BY month), 2) 
    AS calculated_yoy_pct
FROM fact_sip
ORDER BY month;

-- Q4: Total transaction amount by state
SELECT 
    state,
    COUNT(*) AS total_transactions,
    SUM(amount_inr) AS total_amount_inr,
    ROUND(AVG(amount_inr), 2) AS avg_amount
FROM fact_transactions
GROUP BY state
ORDER BY total_amount_inr DESC;

-- Q5: Funds with expense_ratio < 1% (cheaper funds)
SELECT 
    scheme_name,
    fund_house,
    category,
    plan,
    expense_ratio_pct
FROM dim_fund
WHERE expense_ratio_pct < 1.0
ORDER BY expense_ratio_pct ASC;

-- Q6: Top 5 funds by Sharpe ratio (best risk-adjusted returns)
SELECT 
    scheme_name,
    fund_house,
    sharpe_ratio,
    sortino_ratio,
    alpha,
    risk_grade
FROM fact_performance
ORDER BY sharpe_ratio DESC
LIMIT 5;

-- Q7: Total investment by gender and transaction type
SELECT 
    gender,
    transaction_type,
    COUNT(*) AS num_transactions,
    SUM(amount_inr) AS total_invested
FROM fact_transactions
GROUP BY gender, transaction_type
ORDER BY gender, total_invested DESC;

-- Q8: Month with highest SIP inflow ever
SELECT 
    month,
    sip_inflow_crore,
    active_sip_accounts_crore
FROM fact_sip
ORDER BY sip_inflow_crore DESC
LIMIT 1;

-- Q9: Average expense ratio by fund category
SELECT 
    category,
    ROUND(AVG(expense_ratio_pct), 3) AS avg_expense_ratio,
    COUNT(*) AS num_funds,
    ROUND(MIN(expense_ratio_pct), 3) AS min_expense,
    ROUND(MAX(expense_ratio_pct), 3) AS max_expense
FROM dim_fund
GROUP BY category
ORDER BY avg_expense_ratio;

-- Q10: States with highest redemption amounts
SELECT 
    state,
    COUNT(*) AS redemption_count,
    SUM(amount_inr) AS total_redeemed,
    ROUND(AVG(amount_inr), 2) AS avg_redemption
FROM fact_transactions
WHERE transaction_type = 'Redemption'
GROUP BY state
ORDER BY total_redeemed DESC
LIMIT 10;