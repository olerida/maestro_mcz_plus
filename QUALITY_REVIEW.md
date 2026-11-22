# Marketplace and Bronze criteria review

Local review based on official documentation consulted on November 22, 2026. This custom integration does not have an official Bronze classification; the quality scale applies to Home Assistant Core. No catalog submission has been made.

## Marketplace

- The repository contains one integration under `custom_components/maestro_mcz_plus`, a `hacs.json`, README, and local icon.
- The manifest includes domain, version, documentation, issue tracker, proposed owner and the `climate.thermostats_heating` category.
- `.github/workflows/validate.yml` runs hassfest and HACS without ignored checks. The initial run failed because the manifest keys were unsorted and the repository was private. The manifest has since been corrected and the repository made public. Hassfest and HACS validation passed in [run 45013552007](https://github.com/olerida/maestro_mcz_plus/actions/runs/45013552007).
- The repository is public, not archived, has a description, topics and issues enabled. Public catalog inclusion requires passing checks and a full GitHub release. A local ZIP is not a GitHub release. Catalog submission has not been requested.
- Verify the rights and attribution for third-party code and assets before distribution. MCZ's [legal notice](https://www.mcz.it/en/legal-disclamer) restricts use of its website logos on other websites without written permission; the integration includes MCZ brand images; verify permission before public distribution.
- Validate compatibility with the Maestro MCZ version to be recommended: this integration relies on internal structures and methods that can change. Maestro MCZ 1.7.0's coordinator structure was inspected, but full functional compatibility and physical recipe writes remain unverified.

## Core Bronze criteria

| Rule | Local assessment |
| --- | --- |
| action-setup, docs-actions, docs-conditions, docs-triggers | Not applicable: no integration-specific actions, conditions or triggers are registered. |
| appropriate-polling | Reuses Maestro MCZ's coordinator and adds no periodic polling. The effective interval depends on the source. |
| brands | A local icon is provided for Marketplace. Core requires an icon and logo in its brands repository; this remains outstanding. |
| common-modules | The shared entity is in `entity.py`; source coordinators are reused rather than defining another. |
| config-flow | UI setup selects an existing account and offers an advanced controls warning. |
| config-flow-test-coverage | Local tests covered 100% of lines and branches in `config_flow.py`; this alone does not prove all scenarios are covered. |
| dependency-transparency | Depends on another custom integration rather than a directly declared package. Acceptance of this architecture and its dependencies for Core remains to be assessed. |
| docs-high-level-description, docs-installation-instructions, docs-removal-instructions | Covered in the README for manual installation, prerequisites, configuration and removal. The repository is public; end-to-end installation through Marketplace has not been verified. |
| entity-event-setup | Entities use `CoordinatorEntity`; platform discovery subscribes during setup and unsubscribes on entry unload. Core review is needed to confirm the platform-listener exception. |
| entity-unique-id, has-entity-name | IDs derive from the stove code and key, and entities use `has_entity_name`. ID stability depends on the source. |
| runtime-data | Runtime state is stored in `ConfigEntry.runtime_data`. |
| test-before-configure, test-before-setup | Source coordinator availability is checked; no independent connection is made. Whether this is sufficient for Core remains unverified. |
| unique-config-entry | The source entry ID is the unique ID and duplicates are prevented. |

Sources: [quality rules](https://contributors.home-assistant.io/core/quality-scale/rules/), [custom integrations](https://contributors.home-assistant.io/marketplace/guides/integrations/), [catalog](https://contributors.home-assistant.io/marketplace/guides/catalog/) and [validation](https://contributors.home-assistant.io/marketplace/reference/validation/).
