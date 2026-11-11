from cryptography.hazmat.primitives.asymmetric import ec

class Vapid01:
    private_key: ec.EllipticCurvePrivateKey | None
    public_key: ec.EllipticCurvePublicKey | None
    @classmethod
    def from_raw(cls, private_raw: bytes) -> Vapid01: ...
    def generate_keys(self) -> None: ...
