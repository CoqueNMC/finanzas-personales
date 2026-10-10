-- Finwell · extracto para asesor financiero
-- Usuario: usr_260516162236_jcsk · desde 2026-03-01
-- PostgreSQL (Supabase). Montos siempre positivos; el tipo define el signo.
-- Tipos: income | expense | expense_tc (tarjeta de crédito) | transfer | invest | withdraw | move
-- Regla de saldo (account_repository._calculate_balance):
--   income            → +amount en account_id
--   expense/expense_tc→ -amount en account_id
--   transfer/invest/withdraw/move → -amount en account_id, +amount en to_account_id

-- ============================================================
-- 1) DETALLE: todas las transacciones desde marzo
-- ============================================================
SELECT
    t.date                                   AS fecha,
    TO_CHAR(t.date, 'YYYY-MM')               AS mes,
    t.type::text                             AS tipo,
    CASE t.type::text
        WHEN 'income'     THEN 'Ingreso'
        WHEN 'expense'    THEN 'Gasto'
        WHEN 'expense_tc' THEN 'Gasto tarjeta de crédito'
        WHEN 'transfer'   THEN 'Transferencia entre cuentas'
        WHEN 'invest'     THEN 'Inversión'
        WHEN 'withdraw'   THEN 'Retiro de inversión'
        WHEN 'move'       THEN 'Movimiento interno'
    END                                      AS tipo_desc,
    COALESCE(c.name, '(sin categoría)')      AS categoria,
    t.description                            AS descripcion,
    t.amount                                 AS monto,
    CASE
        WHEN t.type::text = 'income' THEN  t.amount
        WHEN t.type::text IN ('expense','expense_tc') THEN -t.amount
        ELSE 0                               -- movimientos internos: no afectan patrimonio neto
    END                                      AS efecto_flujo_caja,
    a.name                                   AS cuenta_origen,
    a.type::text                             AS tipo_cuenta_origen,
    a2.name                                  AS cuenta_destino,
    a2.type::text                            AS tipo_cuenta_destino,
    t.id
FROM transactions t
LEFT JOIN accounts   a  ON a.id  = t.account_id
LEFT JOIN accounts   a2 ON a2.id = t.to_account_id
LEFT JOIN categories c  ON c.id  = t.category_id
WHERE t.user_id = 'usr_260516162236_jcsk'
  AND t.date >= DATE '2026-03-01'
ORDER BY t.date, t.created_at;


-- ============================================================
-- 2) RESUMEN MENSUAL: ingresos, gastos, ahorro neto y tasa de ahorro
-- ============================================================
WITH base AS (
    SELECT
        TO_CHAR(t.date, 'YYYY-MM') AS mes,
        SUM(CASE WHEN t.type::text = 'income'     THEN t.amount ELSE 0 END) AS ingresos,
        SUM(CASE WHEN t.type::text = 'expense'    THEN t.amount ELSE 0 END) AS gastos_efectivo_debito,
        SUM(CASE WHEN t.type::text = 'expense_tc' THEN t.amount ELSE 0 END) AS gastos_tarjeta_credito,
        SUM(CASE WHEN t.type::text = 'invest'     THEN t.amount ELSE 0 END) AS aportes_inversion,
        SUM(CASE WHEN t.type::text = 'withdraw'   THEN t.amount ELSE 0 END) AS retiros_inversion
    FROM transactions t
    WHERE t.user_id = 'usr_260516162236_jcsk'
      AND t.date >= DATE '2026-03-01'
    GROUP BY 1
)
SELECT
    mes,
    ingresos,
    gastos_efectivo_debito + gastos_tarjeta_credito           AS gastos_totales,
    gastos_tarjeta_credito,
    ingresos - (gastos_efectivo_debito + gastos_tarjeta_credito) AS ahorro_neto,
    ROUND((100.0 * (ingresos - (gastos_efectivo_debito + gastos_tarjeta_credito))
           / NULLIF(ingresos, 0))::numeric, 1)                AS tasa_ahorro_pct,
    aportes_inversion,
    retiros_inversion,
    aportes_inversion - retiros_inversion                     AS inversion_neta
FROM base
ORDER BY mes;


-- ============================================================
-- 3) GASTOS POR CATEGORÍA Y MES (con % del gasto del mes)
-- ============================================================
SELECT
    TO_CHAR(t.date, 'YYYY-MM')          AS mes,
    COALESCE(c.name, '(sin categoría)') AS categoria,
    COUNT(*)                            AS n_transacciones,
    SUM(t.amount)                       AS total,
    ROUND((100.0 * SUM(t.amount)
           / SUM(SUM(t.amount)) OVER (PARTITION BY TO_CHAR(t.date, 'YYYY-MM')))::numeric, 1) AS pct_gasto_mes
FROM transactions t
LEFT JOIN categories c ON c.id = t.category_id
WHERE t.user_id = 'usr_260516162236_jcsk'
  AND t.date >= DATE '2026-03-01'
  AND t.type::text IN ('expense', 'expense_tc')
GROUP BY 1, 2
ORDER BY 1, total DESC;


-- ============================================================
-- 4) SALDO ACTUAL POR CUENTA (misma lógica que la app)
-- ============================================================
SELECT
    a.name                              AS cuenta,
    a.type::text                        AS tipo_cuenta,
    a.initial_balance                   AS saldo_inicial,
    a.initial_balance
      + COALESCE(SUM(CASE
            WHEN t.type::text = 'income' AND t.account_id = a.id THEN  t.amount
            WHEN t.type::text IN ('expense','expense_tc') AND t.account_id = a.id THEN -t.amount
            WHEN t.type::text IN ('transfer','invest','withdraw','move') AND t.account_id    = a.id THEN -t.amount
            WHEN t.type::text IN ('transfer','invest','withdraw','move') AND t.to_account_id = a.id THEN  t.amount
            ELSE 0 END), 0)             AS saldo_actual
FROM accounts a
LEFT JOIN transactions t ON (t.account_id = a.id OR t.to_account_id = a.id)
WHERE a.user_id = 'usr_260516162236_jcsk'
  AND a.is_active = TRUE
GROUP BY a.id, a.name, a.type, a.initial_balance
ORDER BY a.type, a.name;
