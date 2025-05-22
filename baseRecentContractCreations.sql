SELECT
  t.address AS contract_address,
  t.block_time,
  t.tx_hash,
  t."from" AS creator_address
FROM base.creation_traces AS t
WHERE
  t.block_time >= CURRENT_TIMESTAMP - INTERVAL '48' hour
  AND t.block_time < CURRENT_TIMESTAMP - INTERVAL '24' hour
ORDER BY
  t.block_time DESC
LIMIT 25