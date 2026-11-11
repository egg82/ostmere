// The little of node the tests that read source files use (the client has no @types/node).
declare module "node:fs" {
  export function readFileSync(path: string, encoding: "utf8"): string;
}
