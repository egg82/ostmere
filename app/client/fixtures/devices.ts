// FIXTURE, never shipped: a TransferCode for screenshots, its QR rows drawn by segno (ashfall_app/api/qr.py) from its
// join_url once, so the fixture page shows a code a phone can read.
import { ApiFailure } from "../src/api/api";
import type { Device, Devices, TransferCode } from "../src/api/types";

export const FIXTURE_CODE: TransferCode = {
  transfer_code: "K7QM-4XRT", expires_in_s: 600, join_url: "https://ostmere.yggdrasil.pub/#join=K7QM-4XRT",
  qr: [
    "111111101000110011100010001111111",
    "100000101010011000000100001000001",
    "101110100111010100110110101011101",
    "101110100001110110100110101011101",
    "101110100101010010101010001011101",
    "100000100100110110100010001000001",
    "111111101010101010101010101111111",
    "000000000001101100010000000000000",
    "010000111011110101001011110000011",
    "011100001010101000010011000011100",
    "001100110111100010100010100010100",
    "101111011111111100101011011111100",
    "100000100001111111110101001100000",
    "110110010010000000101111101001011",
    "001100111011001000100110111010010",
    "100101011111010010101011010101101",
    "101000100101001011110001110111001",
    "110010011101010100011001001001101",
    "000000111001000000110111110101101",
    "100110010010001001111010101011110",
    "001001101110101011101111110111001",
    "110010000111010111000111000010100",
    "101011110101101101100010000110110",
    "101101001011010010101000110001110",
    "111100101010011010111000111110000",
    "000000001000101111111110100010101",
    "111111101101000010001111101010110",
    "100000100000101111110001100011110",
    "101110100110000111001000111111000",
    "101110100011100111110101010111101",
    "101110100100010100110111100110111",
    "100000101000111101101010011111100",
    "111111100001110110010011111100010",
  ],
};

const DAY_MS = 86_400_000;

/** FIXTURE: an account's browsers as the server lists them (this one first, then latest use first); removing one
 * answers the rest, and removing this one answers the others with none marked, as the contract says. */
export function fixtureDevices(): { devices(): Promise<Devices>; removeDevice(id: number): Promise<Devices> } {
  const at = (days: number): string => new Date(Date.now() - days * DAY_MS).toISOString();
  let rows: Device[] = [
    { device_id: 7, label: "Firefox on Linux", created_at: at(40), last_seen_at: at(0), this_device: true },
    { device_id: 9, label: "Safari on iPhone", created_at: at(30), last_seen_at: at(2), this_device: false },
    { device_id: 4, label: "Chrome on Android", created_at: at(90), last_seen_at: at(12), this_device: false },
    { device_id: 3, label: "A browser", created_at: at(200), last_seen_at: at(60), this_device: false },
  ];
  const answer = (): Promise<Devices> => Promise.resolve({ devices: rows });
  return {
    devices: answer,
    removeDevice: (id) => {
      const found = rows.find((d) => d.device_id === id);
      if (!found) return Promise.reject(new ApiFailure("not_found", "fixture: no such device"));
      rows = rows.filter((d) => d !== found).map((d) => (found.this_device ? { ...d, this_device: false } : d));
      return answer();
    },
  };
}
