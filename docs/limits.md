# Limits — read before trusting an atlas

**Coverage is uneven by design.** Labels, agents and distributors are global and research well. Promoters, bookers and open stages live on Instagram, Facebook events, Resident Advisor listings and local forums — sources that unattended fetching often cannot read. A thin Promoters tab in a city is more often a coverage failure than an empty scene; the verify notes say which.

**Facts rot.** Open stages change weekly, promoters go quiet, bookers move jobs. Every record carries a `seen_date`; anything older than 180 days is flagged `re-verify`. Treat a flagged record as a lead, not a fact.

**Judgments are rubric outputs, not advice.** The groups and scores apply written rules to the artist's own answers. If the answers are optimistic (draw band, live video), the atlas is optimistic. The mock scorer is a simple implementation of the rubrics for testing; the model scorer applies the same rules with more nuance and more variance.

**Contacts.** Only business contacts published by the organisation or an official listing. If a record says `contact-unpublished`, that is the finding — the engine will not construct an address and neither should the user. Personal handles appear only when a source outside that platform names them as the booking channel.

**Non-English scenes.** The prompts take search terms from the lane definition and a geographic scope, but source lists per country are not built in. Expect a German or Spanish city to come back thinner and more Anglophone until you add local sources to the lane's `search_terms` and the category prompts.

**Legal.** The engine reads public pages and quotes facts with sources. It does not log in anywhere, does not read private groups, and should not be pointed at paywalled databases. Respect each site's terms; if one disallows automated access, remove it from the sweeps.

**What it is not.** Not a booking service, not outreach automation, not a substitute for going to shows. It tells an artist where the doors are and which ones are open to them today.
