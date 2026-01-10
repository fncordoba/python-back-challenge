import httpx
import asyncio
import sys

BASE_URL = "http://localhost:8000"

async def main():
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as client:
        print("1. Creating School...")
        resp = await client.post("/schools", json={"name": "Springfield Elementary"})
        assert resp.status_code == 201, f"Failed to create school: {resp.text}"
        school = resp.json()
        school_id = school["id"]
        print(f"School created: {school_id}")

        print("2. Creating Student...")
        resp = await client.post("/students", json={"school_id": school_id, "name": "Bart Simpson"})
        assert resp.status_code == 201
        student = resp.json()
        student_id = student["id"]
        print(f"Student created: {student_id}")

        print("3. Creating Invoice...")
        resp = await client.post("/invoices", json={
            "student_id": student_id,
            "amount": 100.0,
            "currency": "USD",
            "due_date": "2026-02-01"
        })
        assert resp.status_code == 201
        invoice = resp.json()
        invoice_id = invoice["id"]
        print(f"Invoice created: {invoice_id}")

        print("4. Checking Statement (Pending)...")
        resp = await client.get(f"/students/{student_id}/account-statement")
        assert resp.status_code == 200
        stmt = resp.json()
        assert stmt["total_due"] == 100.0
        assert stmt["invoices"][0]["status"] == "PENDING"
        print("Statement verified (Pending).")

        print("5. Making Partial Payment...")
        resp = await client.post("/payments", json={
            "invoice_id": invoice_id,
            "amount": 40.0
        })
        assert resp.status_code == 200
        print("Payment processed.")

        print("6. Checking Statement (Partial)...")
        # Give a small moment for DB/Cache if needed (though it should be consistent/invalidated immediately)
        resp = await client.get(f"/students/{student_id}/account-statement")
        assert resp.status_code == 200
        stmt = resp.json()
        assert stmt["total_due"] == 60.0
        assert stmt["invoices"][0]["status"] == "PARTIALLY_PAID"
        print("Statement verified (Partially Paid).")
        
        print("ALL CHECKS PASSED")

if __name__ == "__main__":
    asyncio.run(main())
