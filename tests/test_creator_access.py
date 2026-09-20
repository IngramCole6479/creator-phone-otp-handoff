from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from creator_access import unlock_creator_workflow


def test_verified_creator_releases_the_three_following_actions() -> None:
    access = unlock_creator_workflow("creator-1042", "session-77")

    assert access.creator_id == "creator-1042"
    assert access.digital_asset_delivery == "release_purchased_assets"
    assert access.subscriber_update == "publish_creator_update"
    assert access.content_processing == "queue_new_content"
