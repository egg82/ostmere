// A transfer code's QR code (CONTRACT.txt, TransferCode.qr), drawn as SVG: one rect per run of dark modules in a row,
// dark on a light tile with a quiet zone of four modules, so a camera reads it whatever the page's colours.
const SVG = "http://www.w3.org/2000/svg";
const QUIET = 4;

export function qrSvg(rows: string[], label: string): SVGSVGElement {
  const side = rows.length + QUIET * 2;
  const svg = document.createElementNS(SVG, "svg");
  svg.setAttribute("viewBox", `0 0 ${side} ${side}`);
  svg.setAttribute("class", "qr");
  svg.setAttribute("role", "img");
  svg.setAttribute("aria-label", label);
  svg.setAttribute("shape-rendering", "crispEdges");
  svg.append(rect(0, 0, side, side, "qr-light"));
  rows.forEach((row, y) => {
    for (let x = 0; x < row.length; x += 1) {
      if (row[x] !== "1") continue;
      let end = x;
      while (row[end + 1] === "1") end += 1;
      svg.append(rect(x + QUIET, y + QUIET, end - x + 1, 1, "qr-dark"));
      x = end;
    }
  });
  return svg;
}

function rect(x: number, y: number, w: number, h: number, cls: string): SVGRectElement {
  const r = document.createElementNS(SVG, "rect");
  for (const [k, v] of [["x", x], ["y", y], ["width", w], ["height", h]] as const) r.setAttribute(k, String(v));
  r.setAttribute("class", cls);
  return r;
}
