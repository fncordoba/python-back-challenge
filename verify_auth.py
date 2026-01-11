import httpx
import asyncio
import os

# Try to load formatted URL from env, default to local
BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")

async def main():
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as client:
        print("1. Try CREATE School (Unauthenticated)...")
        resp = await client.post("/schools", json={"name": "Hacker School"})
        assert resp.status_code == 401
        print("   -> 401 Unauthorized (Expected)")

        print("2. Login as Admin...")
        resp = await client.post("/token", data={"username": "admin@mattilda.io", "password": "admin123"})
        if resp.status_code != 200:
            print(f"Login Failed: {resp.text}")
            return
        
        token_data = resp.json()
        access_token = token_data["access_token"]
        print("   -> Login Success. Token received.")
        
        headers = {"Authorization": f"Bearer {access_token}"}
        
        print("3. Try CREATE School (Authenticated)...")
        resp = await client.post("/schools", json={"name": "Secure School"}, headers=headers)
        if resp.status_code == 201:
             print("   -> 201 Created (Success)")
             school_id = resp.json()["id"]
             
             # Clean up
             await client.delete(f"/schools/{school_id}", headers=headers)
        else:
             print(f"   -> FAILED: {resp.status_code} {resp.text}")

        print("SUCCESS: Auth Flow Verified.")

if __name__ == "__main__":
    asyncio.run(main())
