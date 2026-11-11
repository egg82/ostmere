"""Wire models of moving an account to another device (CONTRACT.txt, "Moving to another device"). The conventions of
models.py hold here; the refusal's MergeSummary is error_models.py's."""
from typing import Literal

from datetime import datetime

from pydantic import BaseModel, Field, model_validator

from .models import Request
from .saves_models import Account


class TransferCode(BaseModel):
    transfer_code: str
    """Eight characters, shown "ABCD-EFGH"; joins one browser, once, within expires_in_s."""
    expires_in_s: int
    join_url: str
    """The public site with the code in the fragment (/#join=ABCD-EFGH)."""
    qr: list[str]
    """join_url as a QR code: rows top first, "1" dark and "0" light, no quiet zone."""


class RecoveryWords(BaseModel):
    words: str
    """Four BIP-39 English words, lowercase, joined by dashes. Never answered again."""
    label: Literal["Ostmere"]
    """The name a password manager files the words under."""


class JoinRequest(Request):
    typed: str = Field(max_length=200)
    """A transfer code (or its join_url), or recovery words, as the player typed them."""
    merge: bool = False
    """Move this browser's own games into the named account (asked first by confirm_merge)."""
    keep: bool = False
    """Join without moving: this browser's own games stay on its old account (also asked after confirm_merge). With
    merge, 422."""

    @model_validator(mode="after")
    def _one_choice(self) -> "JoinRequest":
        if self.merge and self.keep:
            raise ValueError("merge and keep are two answers to one question")
        return self


class Kept(BaseModel):
    saves: int
    """Live saves left on the old account."""
    words: str | None
    """The old account's new recovery words (like RecoveryWords.words), made because it had none; shown once. Null: it
    already had words, which cannot be shown again."""
    label: Literal["Ostmere"]
    """RecoveryWords.label."""


class Joined(BaseModel):
    moved: int
    """Saves that became the named account's."""
    account: Account
    kept: Kept | None = None
    """Set when the request had `keep` and this browser's own games stayed on its old account."""


class Device(BaseModel):
    device_id: int
    """The session's id, for DELETE /api/me/devices/{device_id}. Never the token or its hash."""
    label: str
    """Browser and system, e.g. "Firefox on Linux"; "A browser" when neither was told."""
    created_at: datetime
    """When this browser got its session (wall time, UTC)."""
    last_seen_at: datetime
    """When it was last used, stored at most once a day (wall time, UTC)."""
    this_device: bool
    """The browser that asked."""


class Devices(BaseModel):
    devices: list[Device]
    """The account's sessions, this browser first, then the rest most recently used first."""
