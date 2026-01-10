# API Test Cases (Manual Verification)

Run these commands in order to verify the system end-to-end.

## 1. Create School
```bash
curl -X POST http://localhost:8000/schools \
  -H "Content-Type: application/json" \
  -d '{"name": "Springfield Elementary"}'
```
**Expected**: 201 Created, returns `{"id": "...", "name": "Springfield Elementary", ...}`

## 2. Create Student
```bash
# Replace {school_id} with ID from step 1
curl -X POST http://localhost:8000/students \
  -H "Content-Type: application/json" \
  -d '{"school_id": "{school_id}", "name": "Bart Simpson"}'
```
**Expected**: 201 Created

## 3. Create Invoice
```bash
# Replace {student_id} from step 2
curl -X POST http://localhost:8000/invoices \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "{student_id}",
    "amount": 100.00,
    "currency": "USD",
    "due_date": "2026-02-01T00:00:00Z"
  }'
```
**Expected**: 201 Created, `status: PENDING`

## 4. Get Student Account Statement (Fresh)
```bash
curl http://localhost:8000/students/{student_id}/account-statement
```
**Expected**: 200 OK
- `status`: `PENDING`
- `amount_total`: 100.0
- `amount_paid`: 0.0
- `amount_due`: 100.0

## 5. Register Partial Payment
```bash
# Replace {invoice_id} from step 3
curl -X POST http://localhost:8000/payments \
  -H "Content-Type: application/json" \
  -d '{
    "invoice_id": "{invoice_id}",
    "amount": 40.00
  }'
```
**Expected**: 201 Created

## 6. Verify Statement Update (Cache Invalidation Check)
```bash
curl http://localhost:8000/students/{student_id}/account-statement
```
**Expected**: 200 OK
- `status`: `PARTIALLY_PAID`
- `amount_paid`: 40.0
- `amount_due`: 60.0

## 7. SQL Verification
```sql
-- Check Invoice State
SELECT status, amount_total FROM invoices WHERE id = '{invoice_id}';
-- Check Payments
SELECT sum(amount) FROM payments WHERE invoice_id = '{invoice_id}';
```
