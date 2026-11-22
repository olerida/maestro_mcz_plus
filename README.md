# Maestro MCZ Plus

<img src="custom_components/maestro_mcz_plus/brand/logo.png" alt="MCZ" width="192">

[![Open in Home Assistant Marketplace](https://my.home-assistant.io/badges/marketplace_repository.svg)](https://my.home-assistant.io/redirect/marketplace_repository/?owner=olerida&repository=maestro_mcz_plus&category=integration)
[![Add integration to Home Assistant](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=maestro_mcz_plus)

> [!WARNING]
> Normal mode is read-only. Advanced options enable changes to stove combustion settings and are intended only for technicians or users with advanced knowledge. Commands have been tested in simulations; their effect on a physical stove has not yet been verified.

Maestro MCZ Plus is a community integration for Home Assistant that adds operating data and recipe settings for MCZ Maestro stoves. It uses an existing [Maestro MCZ](https://github.com/Robbe-B/maestro_mcz) account and connection. This project is independent and is not affiliated with or endorsed by MCZ Group.

## Installation

### Prerequisites

1. Install and configure **Maestro MCZ** and check that it detects your stove. This package has been tested in an isolated Home Assistant 2026.10.4 environment.
2. Ensure the stove is connected and Maestro MCZ can reach the MCZ cloud.

### Home Assistant Marketplace

The repository is currently private; the Marketplace button and public installation link will be usable once the repository is made public. No catalog listing is implied.

1. In Home Assistant 2026.11 or later, open **Settings → Marketplace**, select **Add from link**, and enter `https://github.com/olerida/maestro_mcz_plus`. Select **Integration** if asked. The Marketplace button above opens the same flow.
2. Open **Maestro MCZ Plus**, select **Install**, and follow any restart prompt.
3. Select the **Add integration** button above, or go to **Settings → Devices & services → Add integration** and search for **Maestro MCZ Plus**. Select the account already configured in Maestro MCZ.

On earlier compatible versions, add the repository as a custom repository in HACS under the **Integration** category and follow the installation and restart prompts.

### Manual installation

1. Copy `custom_components/maestro_mcz_plus` from the repository or installation ZIP into your Home Assistant configuration's `custom_components` directory. Create that directory if necessary.
2. Restart Home Assistant.
3. Go to **Settings → Devices & services → Add integration**, select **Maestro MCZ Plus**, and choose your existing Maestro MCZ account.

If you already use **Maestro MCZ Extra Sensors** or **Maestro MCZ Recipes**, this integration creates new entities. Review automations and dashboards that use the old entities before disabling those integrations.

## Operating data

Depending on the stove model, entities can include exhaust and board temperatures, operating phase, active power, exhaust fan and auger speeds, and brazier cleaning times. Entities appear as the source integration receives the data. Updates follow Maestro MCZ's interval and may differ from the official app.

## Recipes

Active, Pellet and Adaptive mode values appear when provided by the stove. Reading them is enabled by default. A technician can enable recipe controls under **Settings → Devices & services → Maestro MCZ Plus → Configure**. Controls are offered only for recognized model and parameter combinations. Numeric values change in steps of one within the limits provided by the model.

Commands have been tested with simulations only. Verify real changes in the official app or on the stove. The integration reports an error if the source does not return the requested values after a command. When changing one Active setting, the other is preserved from the latest reading; avoid changing Active settings from two clients at the same time.

After reloading or updating Maestro MCZ, reload Maestro MCZ Plus as well to reconnect its entities to the source.

## Troubleshooting

- **No account available:** configure Maestro MCZ first and ensure the account is loaded and detects at least one stove.
- **Missing readings or controls:** availability depends on data and metadata provided by the stove and the source integration. Controls require the advanced option and recognized settings.
- **Data unavailable after reloading Maestro MCZ:** reload Maestro MCZ Plus from its menu under Devices & services.
- **A change is not confirmed:** check the official app or stove before trying again. Commands have only been validated in simulations.

## Removal

Under **Settings → Devices & services**, open the Maestro MCZ Plus menu and select **Delete**. For a manual installation, also remove `custom_components/maestro_mcz_plus` and restart Home Assistant. If installed with Marketplace or HACS, uninstall it there and follow the restart prompt. Maestro MCZ and its devices are retained.

## macOS preview and build

Craft Anything can open `dist/Maestro MCZ Plus Preview.app` to display simulated stove readings and recipes. The real stove connection is made through Home Assistant.

To build the installation ZIP and macOS preview, set up the Python test environment in `requirements-test.txt`, install Xcode command line tools, and run `./build.sh`.

## Code and license

[Maestro+ 5.8.0 mechanics](MECHANICS.md) documents the recipe limits, command format and telemetry found in the app. Compatibility with other stoves depends on the data and metadata available from Maestro MCZ.

The code is distributed under the [MIT license](LICENSE). MCZ and its logos belong to their respective owner and are not covered by the MIT license.
