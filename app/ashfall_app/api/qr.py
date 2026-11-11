"""A join link as a QR code's modules, for the page to draw (CONTRACT.txt, TransferCode.qr): rows top first, "1" dark,
"0" light, no quiet zone. Error correction M at least (segno raises it while the version stays the same), so a phone
reads it off a screen with glare."""
import segno


def rows(text: str) -> list[str]:
    code = segno.make(text, error="m", micro=False)
    return ["".join("1" if module else "0" for module in row) for row in code.matrix_iter(scale=1, border=0)]
