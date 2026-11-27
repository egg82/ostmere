"""Her sowing reaches the player on its own: the trigger that opens the card installs its always rule, so the beds
open (and with them the barley the frost and the reaping are about) whether or not the player ever offers her the
order card. A play where nobody sets that rule would otherwise never open them."""
from ashfall_app.engine import CardId, new_save
from ashfall_app.engine.installs import installed
from ashfall_app.engine.orders import AfterTime
from ashfall_app.engine.lanes import TapCard
from tests.rules.play.playthrough import opening_rules


def test_the_trigger_that_opens_her_sowing_installs_the_rule_that_runs_it():
    rules = opening_rules()
    sow = next(t for t in rules.triggers if t.id == "t_sow")
    assert [i.card for i in sow.outcome.orders] == [CardId("n3_sow")], "the install is the trigger's"
    save = installed(new_save(rules), sow.outcome.orders)
    assert [o.then for o in save.orders if o.when == AfterTime(0)] == [TapCard(CardId("n3_sow"))]

