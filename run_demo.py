import httpx
import asyncio
import json

BASE_URL = "http://localhost:8000"

async def print_step(title):
    print(f"\n{'='*50}")
    print(f"STEP: {title}")
    print(f"{'='*50}")

async def log_req_res(response):
    try:
        data = response.json()
        print(f"Response Status: {response.status_code}")
        print(f"Response Body: {json.dumps(data, indent=2)}")
        return data
    except Exception:
        print(f"Response Text: {response.text}")
        return None

async def main():
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as client:
        await print_step("1. Create School")
        resp = await client.post("/schools", json={"name": "Springfield Elementary"})
        data = await log_req_res(resp)
        assert resp.status_code == 201
        school_id = data["id"]

        await print_step("2. Create Student")
        resp = await client.post("/students", json={"school_id": school_id, "name": "Bart Simpson"})
        data = await log_req_res(resp)
        assert resp.status_code == 201
        student_id = data["id"]

        await print_step("3. Create Invoice (Amount: 100.00)")
        resp = await client.post("/invoices", json={
            "student_id": student_id,
            "amount": 100.00,
            "currency": "USD",
            "due_date": "2026-02-01"
        })
        data = await log_req_res(resp)
        assert resp.status_code == 201
        invoice_id = data["id"]

        await print_step("4. Get Account Statement (Fresh)")
        resp = await client.get(f"/students/{student_id}/account-statement")
        data = await log_req_res(resp)
        assert resp.status_code == 200
        
        # Debugging assertions
        print(f"DEBUG: total_due type: {type(data['total_due'])} value: {data['total_due']}")
        assert float(data["total_due"]) == 100.0, f"Expected 100.0, got {data['total_due']}"

        await print_step("5. Process Payment (Amount: 40.00)")
        resp = await client.post("/payments", json={
            "invoice_id": invoice_id,
            "amount": 40.00
        })
        data = await log_req_res(resp)
        assert resp.status_code == 200

        await print_step("6. Get Account Statement (After Payment)")
        resp = await client.get(f"/students/{student_id}/account-statement")
        data = await log_req_res(resp)
        assert resp.status_code == 200
        assert float(data["total_due"]) == 60.0, f"Expected 60.0, got {data['total_due']}"
        assert data["invoices"][0]["status"] == "PARTIALLY_PAID"

        print("\nSUCCESS: All checks passed.")

if __name__ == "__main__":
    asyncio.run(main())
