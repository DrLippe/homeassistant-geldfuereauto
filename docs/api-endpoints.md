# Network endpoints identified in HAR

These are **observed browser requests**, not an official supported API.
Never commit a HAR file, cookies, passwords, customer details, bank account
information, or access tokens.

| Endpoint | Method | Observed response | v0.2 integration |
|---|---|---|---|
| /api/login | POST | 200, empty body; JSON keys email/password | Attempted; session semantics unverified |
| /api/getAccountDetails | GET | Account details, values, values_per_type | Login verification, account lookup |
| /api/getCars | GET | count, cars; payouts, values | Yes; paginated |
| /api/getStatus | GET | count, docs | No |
| /api/getPayments | GET | count, payments | No |
| /api/profile/getPaymentSummary | GET | pending_amount, paid_amount, pending_car_amount_next_year | Yes; parameter payment_type=all needs runtime verification |
| /api/getDirectUploadedDocCount | GET | count | No |
| /api/getOtbDocId | GET | doc_id, paid | No |
| /api/getReferralPrice | GET | referral price data | No |
| /api/getReferralCodes | GET | referral_codes, count | No |
| /api/getReferralDetails | GET | referrals | No |
| /api/chargers/stations | GET | rows, count | No |
| /api/chargers/events | GET | rows, count | No |
| /api/chargers/locations | GET | rows, count | No |
| /api/chargers/operators | GET | rows, count | No |

Postman validation confirmed the JSON login body is accepted and the server sets
\`sid\` (session token) and \`sid_active\` (session state) cookies. The integration
now uses a private aiohttp CookieJar, logs in before the first read, and
re-authenticates after HTTP 401/403. Cookie contents are never logged or stored.
Live end-to-end verification in Home Assistant is still pending.
