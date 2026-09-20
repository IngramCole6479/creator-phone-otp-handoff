from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CreatorLoginRequest:
    phone: str
    code: str
    creator_id: str


@dataclass(frozen=True)
class CreatorAccess:
    creator_id: str
    session_id: str
    digital_asset_delivery: str
    subscriber_update: str
    content_processing: str


def unlock_creator_workflow(creator_id: str, session_id: str) -> CreatorAccess:
    """Make the post-login commerce handoff explicit and deterministic."""
    return CreatorAccess(
        creator_id=creator_id,
        session_id=session_id,
        digital_asset_delivery="release_purchased_assets",
        subscriber_update="publish_creator_update",
        content_processing="queue_new_content",
    )
