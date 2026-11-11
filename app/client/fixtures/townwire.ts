// FIXTURE, never shipped: the town's mix as the engine serves it over the wire (api/models.View), captured from a real
// engine run (two ruled lanes, helper and mason, joined at 100 and 120 s; the town mix split 60/30 and 70/20; the helper
// tapping Haul by a rule at 450 s, the mason on shares; "one": only the helper has joined, the mason's own lane run by
// its always rule). The generator is the scenario in the 3e notes; a hand-edit here would break its totals.
import type { View } from "../src/api/types";

export type TownWire = Pick<View, "at" | "lanes" | "cards" | "mixes" | "orders" | "orders_on" | "order_states" | "running_town_mix_id" | "town_mix_order" | "greyed_mix_ids"> & { joined: { category: "joined"; id: string }[] };

export const TOWN_WIRE: Record<"two" | "one", TownWire> = {
 "two": {
  "at": 450,
  "lanes": [
   {
    "lane": "hands",
    "running_card": null,
    "completes_at": null,
    "order": null
   },
   {
    "lane": "helper",
    "running_card": "haul",
    "completes_at": null,
    "order": 0
   },
   {
    "lane": "mason",
    "running_card": null,
    "completes_at": null,
    "order": null
   }
  ],
  "cards": [
   {
    "card": "chop",
    "completions": 1,
    "cap": null,
    "bar": {
     "start": 450,
     "start_value": 1000000,
     "rate": 0,
     "limit": null
    },
    "bar_total": 1000000,
    "by": null,
    "completes_at": null,
    "share_bp": 6000,
    "run": "yielded",
    "blocker": null,
    "cuts_in": false,
    "spent_store": null,
    "gained": [],
    "tap_s": 100,
    "needs": []
   },
   {
    "card": "haul",
    "completions": 7,
    "cap": null,
    "bar": {
     "start": 450,
     "start_value": 3500000,
     "rate": 10000,
     "limit": null
    },
    "bar_total": 500000,
    "by": "tap",
    "completes_at": 500,
    "share_bp": 3000,
    "run": "yielded",
    "blocker": null,
    "cuts_in": false,
    "spent_store": null,
    "gained": [],
    "tap_s": 50,
    "needs": []
   },
   {
    "card": "hew",
    "completions": 3,
    "cap": null,
    "bar": {
     "start": 450,
     "start_value": 3750000,
     "rate": 7000,
     "limit": null
    },
    "bar_total": 1000000,
    "by": "mix",
    "completes_at": 486,
    "share_bp": 7000,
    "run": "full",
    "blocker": null,
    "cuts_in": false,
    "spent_store": null,
    "gained": [],
    "tap_s": 25,
    "needs": []
   },
   {
    "card": "carve",
    "completions": 0,
    "cap": null,
    "bar": {
     "start": 450,
     "start_value": 500000,
     "rate": 2000,
     "limit": null
    },
    "bar_total": 600000,
    "by": "mix",
    "completes_at": 500,
    "share_bp": 2000,
    "run": "full",
    "blocker": null,
    "cuts_in": false,
    "spent_store": null,
    "gained": [],
    "tap_s": 10,
    "needs": []
   }
  ],
  "mixes": [
   {
    "id": "town:main",
    "components": [
     {
      "kind": "card_share",
      "card": "chop",
      "share_bp": 6000
     },
     {
      "kind": "card_share",
      "card": "haul",
      "share_bp": 3000
     },
     {
      "kind": "card_share",
      "card": "hew",
      "share_bp": 7000
     },
     {
      "kind": "card_share",
      "card": "carve",
      "share_bp": 2000
     }
    ]
   }
  ],
  "orders": [
   {
    "when": {
     "kind": "at_least",
     "watched": {
      "kind": "card_count",
      "card": "chop"
     },
     "value": 1,
     "release": 1
    },
    "then": {
     "kind": "tap_card",
     "card": "haul"
    }
   },
   {
    "when": {
     "kind": "after_time",
     "at": 0
    },
    "then": {
     "kind": "switch_mix",
     "mix_id": "town:main"
    }
   }
  ],
  "orders_on": [
   true,
   true
  ],
  "order_states": [
   "on",
   "on"
  ],
  "running_town_mix_id": "town:main",
  "town_mix_order": 1,
  "greyed_mix_ids": [],
  "joined": [
   {
    "category": "joined",
    "id": "helper"
   },
   {
    "category": "joined",
    "id": "mason"
   }
  ]
 },
 "one": {
  "at": 450,
  "lanes": [
   {
    "lane": "hands",
    "running_card": null,
    "completes_at": null,
    "order": null
   },
   {
    "lane": "helper",
    "running_card": "haul",
    "completes_at": null,
    "order": 0
   },
   {
    "lane": "mason",
    "running_card": "hew",
    "completes_at": null,
    "order": 1
   }
  ],
  "cards": [
   {
    "card": "chop",
    "completions": 1,
    "cap": null,
    "bar": {
     "start": 450,
     "start_value": 1000000,
     "rate": 0,
     "limit": null
    },
    "bar_total": 1000000,
    "by": null,
    "completes_at": null,
    "share_bp": 6000,
    "run": "yielded",
    "blocker": null,
    "cuts_in": false,
    "spent_store": null,
    "gained": [],
    "tap_s": 100,
    "needs": []
   },
   {
    "card": "haul",
    "completions": 7,
    "cap": null,
    "bar": {
     "start": 450,
     "start_value": 3500000,
     "rate": 10000,
     "limit": null
    },
    "bar_total": 500000,
    "by": "tap",
    "completes_at": 500,
    "share_bp": 3000,
    "run": "yielded",
    "blocker": null,
    "cuts_in": false,
    "spent_store": null,
    "gained": [],
    "tap_s": 50,
    "needs": []
   },
   {
    "card": "hew",
    "completions": 4,
    "cap": null,
    "bar": {
     "start": 450,
     "start_value": 4500000,
     "rate": 10000,
     "limit": null
    },
    "bar_total": 1000000,
    "by": "tap",
    "completes_at": 500,
    "share_bp": 0,
    "run": null,
    "blocker": null,
    "cuts_in": false,
    "spent_store": null,
    "gained": [],
    "tap_s": 50,
    "needs": []
   },
   {
    "card": "carve",
    "completions": 0,
    "cap": null,
    "bar": {
     "start": 450,
     "start_value": 0,
     "rate": 0,
     "limit": null
    },
    "bar_total": 600000,
    "by": null,
    "completes_at": null,
    "share_bp": 0,
    "run": null,
    "blocker": null,
    "cuts_in": false,
    "spent_store": null,
    "gained": [],
    "tap_s": 60,
    "needs": []
   }
  ],
  "mixes": [
   {
    "id": "town:main",
    "components": [
     {
      "kind": "card_share",
      "card": "chop",
      "share_bp": 6000
     },
     {
      "kind": "card_share",
      "card": "haul",
      "share_bp": 3000
     }
    ]
   }
  ],
  "orders": [
   {
    "when": {
     "kind": "at_least",
     "watched": {
      "kind": "card_count",
      "card": "chop"
     },
     "value": 1,
     "release": 1
    },
    "then": {
     "kind": "tap_card",
     "card": "haul"
    }
   },
   {
    "when": {
     "kind": "after_time",
     "at": 0
    },
    "then": {
     "kind": "tap_card",
     "card": "hew"
    }
   },
   {
    "when": {
     "kind": "after_time",
     "at": 0
    },
    "then": {
     "kind": "switch_mix",
     "mix_id": "town:main"
    }
   }
  ],
  "orders_on": [
   true,
   true,
   true
  ],
  "order_states": [
   "on",
   "on",
   "on"
  ],
  "running_town_mix_id": "town:main",
  "town_mix_order": 2,
  "greyed_mix_ids": [],
  "joined": [
   {
    "category": "joined",
    "id": "helper"
   }
  ]
 }
};
