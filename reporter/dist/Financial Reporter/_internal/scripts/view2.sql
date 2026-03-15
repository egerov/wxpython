select

TO_CHAR(dt_rep, 'YYYY-MM-DD'),
conto,
prod_type,
prod_subtype,
con_type,
outflow,
sum(amount_rub)

from dm_ras.ras_pmbk_lcr

where 1=1
and dt_rep = :dt

group by

dt_rep,
conto,
prod_type,
prod_subtype,
con_type,
outflow

order by conto