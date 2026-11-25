# billing-export

Nightly job: `scripts/export_orders.py`.

The `from` parameter on the export wrapper is a closed interval. Pass
`--operator` (or `EXPORT_OPERATOR`) and, unless you need a wider window,
leave the default range at the last 24 hours.

Do not run a full-ledger export from a laptop.
