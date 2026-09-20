from __future__ import annotations

import os

from creator_access import CreatorAccess, CreatorLoginRequest, unlock_creator_workflow
from infrai_phone import InfraiPhoneClient


def request_signup_code(phone: str, creator_id: str) -> None:
    InfraiPhoneClient().send_signup_code(phone, f"creator-signup-{creator_id}")


def complete_login(request: CreatorLoginRequest) -> CreatorAccess:
    client = InfraiPhoneClient()
    verification = client.verify_phone(
        request.phone, request.code, f"creator-verify-{request.creator_id}"
    )
    session_id = client.create_session(
        verification.user_id, f"creator-session-{verification.user_id}"
    )
    return unlock_creator_workflow(request.creator_id, session_id)


def main() -> None:
    phone = os.environ["DEMO_PHONE"]
    creator_id = os.environ.get("DEMO_CREATOR_ID", "creator-1042")
    request_signup_code(phone, creator_id)
    print("Code sent. Set DEMO_CODE, then run this command again.")
    code = os.environ.get("DEMO_CODE")
    if code:
        access = complete_login(CreatorLoginRequest(phone, code, creator_id))
        print(access)


if __name__ == "__main__":
    main()
