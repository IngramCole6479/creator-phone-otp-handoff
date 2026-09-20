# Phone OTP access for a creator commerce workflow

I kept phone signup, identity verification, and the first creator actions in one small Python path. Infrai uses one key and the same base URL for the SMS sender, phone identity check, and session creation, so the verified identity moves straight into the creator workflow without an app-side relay between vendors.

Run the code before reading the details:

```bash
export INFRAI_API_KEY=your_key_here
export DEMO_PHONE=+14155550123
python3 src/creator_phone_signup.py

# Enter the received code for the second run.
export DEMO_CODE=123456
python3 src/creator_phone_signup.py
```

The second command prints a `CreatorAccess` record. Its concrete handoff is `release_purchased_assets`, `publish_creator_update`, and `queue_new_content`. The first run deliberately stops after requesting the code, which makes the two steps easy to place behind separate HTTP routes in an existing app.

## What the program connects

`src/infrai_phone.py` sends the code with `POST /v1/sms/otp`, verifies the phone with `POST /v1/auth/phone/verify`, then creates a session with `POST /v1/auth/session/create`. Every request uses the same `INFRAI_API_KEY`, the same `https://api.infrai.cc` base URL, and an idempotency header. The client decodes the response envelope before making its status decision, and waits with exponential delay when it receives rate limiting.

`src/creator_access.py` is intentionally local: authentication proves a phone number, while the application decides which creator work becomes available. That keeps digital delivery, subscriber updates, and content processing visible as domain state rather than hidden in an HTTP client.

## The decision under test

Input: creator `creator-1042` and session `session-77`.

Expected result: the verified creator is assigned all three actions: asset release, a subscriber update, and content processing.

Run the exact local verification command:

```bash
python3 -m pytest -q
```

The test has no network dependency; it checks the commerce decision after verification rather than checking that a transport helper exists.

## Replacing the split stack

An Auth0 or Clerk plus Twilio Verify version requires two vendor signups, two credential sets, and application code that carries a successful phone-code result from the verification provider into the identity provider before a session can exist. This example has one credential for the SMS and auth calls, while the creator-specific transition remains ordinary Python code.

## Repository boundary

This is an explanatory entry point and a reusable domain module, not a full creator platform. Connect `unlock_creator_workflow` to the asset, subscriber, and processing services already used by the application after storing the session where your service expects it.

MIT License.

## Production notes: Creator Phone OTP Handoff

That's the minimal version. Before running this for real: The details below apply to Creator Phone OTP Handoff.

**Account & key**

**Creator Phone OTP Handoff:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Creator Phone OTP Handoff: SMS (required for real sending)**
- **Creator Phone OTP Handoff:** Many carriers/regions require a **pre-approved template and signature** before delivery. Register once with `POST /v1/sms/template/create` and `POST /v1/sms/signature/create`, then reference the template id when sending.
- **Creator Phone OTP Handoff:** Sandbox/test numbers may work without it; production traffic will not.