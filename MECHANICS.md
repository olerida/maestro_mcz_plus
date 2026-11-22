# Maestro+ MCZ 5.8.0 mechanics

The `it.mcz.maestro.apk` APK and its 32-bit ARM Dart AOT library, `lib/armeabi-v7a/libapp.so`, included in `config.armeabi_v7a.apk`, were analyzed. Library SHA-256: `d70fdfabd3dfa3a3e458e804d607af3cf38470d71f87e60112ce3821756e5e47`. The following addresses are virtual addresses in the original ELF. If Ghidra imports the ELF with base `0x10000`, add that base to function addresses. Ghidra and ARM disassembly were checked against the Dart 3.11.5 instruction table and object pool references.

## Recipe readings and limits

| Setting | State field | Read function | Field offset |
| --- | --- | --- | --- |
| Active value | `pos_ric_flu` | `RecipePage.get:posRicFluValueSelected` · `0x9cc9e8` | `0x07` |
| Active enabled | `act` | `RecipePage.get:isActiveOn` · `0x9cc734` | `0x10f` |
| Pellet | `pos_ric_pel` | `RecipePage.get:pelletValueSelected` · `0x9cc6e4` | `0xab` |
| Adaptive mode | `mod_ada_on` | `RecipePage.get:modAdaOn` · `0x9cc594` | `0x11b` |

Offsets are relative to the tagged Dart object pointer. Getters match `StateResponseFromJson` (`0x5bde84`) and `StateResponseToJson` (`0x573c78`). The app displays a `+` sign for positive Active values (`0x9cc8e8`); Home Assistant retains the numeric value.

- **Active.** `get:commandSensorPosRicFlu` (`0x94cb2c`) retrieves the sensor from the model configuration. `get:sliderRange` (`0x94ca84`) converts the limits at offsets `0x17` and `0x1b` to numbers. The control step is `1.0` (`0x94c4ec`, within `0x94c284`).
- **Pellet.** `createSlider` (`0x95cb60`) converts the minimum and maximum at those offsets, calculates `maximum − minimum` (`0x95ce10`), and sets a step of `1.0` (`0x95cf3c`). The Active and Pellet send methods convert the selection to an integer before constructing the command.
- **Home Assistant.** Integer settings use `ceil(Min)` and `floor(Max)`. Both limits must be finite and allow at least one integer. Advanced controls require enabled metadata from a recognized model. The −3 to +3 range was observed on an Ego Comfort Air; limits are taken from the connected model.

## Saving

| Setting | Send function | Commands in app order |
| --- | --- | --- |
| Active | `0x94cf34` | `SENSOR_PELLET_ACT_VALUE` (integer), then `SENSOR_PELLET_ACT` (boolean) |
| Pellet | `0x95d4bc` | `SENSOR_PALLET` (integer) |
| Adaptive mode | `0x94de98` | `SENSOR_PELLET_MOD_ADA_ON` (boolean) |

The app obtains UUIDs by sensor family in `listConfigurations` (`0x56e2fc`) and `listSensorsId` (`0x56e514`). Active getters find both sensors in the selected configuration (`0x94cb2c`, `0x94d4c8`). Snapshot maps pair these keys with the following UUIDs.

| Key | AIR / HYBRID | HYDRO |
| --- | --- | --- |
| `CONFIGURATION_PELLET` | `f6538f6b-ef3d-4ed7-9ab6-4b3b97fc0e1f` | `62bfda67-95b2-4372-804d-0f7013d857e0` |
| `SENSOR_PALLET` | `e50abf4a-6e52-487c-8637-1d00d8978359` | `8c59dc5a-4e7d-4706-8ac3-e144ed8a9515` |
| `SENSOR_PELLET_ACT_VALUE` | `307ba615-e58f-4df0-944a-a1df97c73e06` | `8056d063-f5e0-48c7-9960-90b48ca81798` |
| `SENSOR_PELLET_ACT` | `2998639c-8240-4bc5-9331-2b9aa9ffc1a2` | `9156d446-2062-40c7-bea7-4934c5e5d79a` |
| `SENSOR_PELLET_MOD_ADA_ON` | `f5ee03fd-7f71-48fb-8e71-46d5d4cf56d5` | `b22fb6e1-d8d2-4857-b9bf-07bfcf10fe91` |

`activateAProgram` (`0x558974`) sends a `POST` to `/mcz/v1.0/Program/ActivateProgram/{id}`. The request serializer (`0x558d38`) uses `ModelId`, `ConfigurationId`, `SensorSetTypeId` and `Commands`. Each command serializer (`0x566338`) writes `SensorId` and `Value` using the supplied value type. The integration delegates sending to Maestro MCZ. When changing an Active setting, it reads the other, sends both in app order, and verifies the result with a subsequent refresh.

## Operating data

`StateInfoResponseFromJson` (`0xa26cac`) y `StateInfoResponseToJson` (`0xa263ac`) map these fields to the app table (`HowItWorksInfoPage.buildBodyTableLayout`, `0x9a86dc`).

| Reading | Field | Offset | App presentation |
| --- | --- | --- | --- |
| Exhaust fan, requested / actual | `vel_imp_ventola_fumi` / `vel_real_ventola_fumi` | `0x03` / `0x07` | RPM |
| Auger, requested / actual | `vel_imp_coclea` / `vel_real_coclea` | `0x0b` / `0x0f` | RPM |
| Active, requested / actual | `pressione_imp` / `pressione` | `0x17` / `0x13` | Direct values, no unit specified |
| Active power / duration | `potenza_att` / `potenza_counter` | `0x2b` / `0x2f` | Direct values, no unit specified |
| Expected / remaining cleaning time | `t_dur_pul` / `t_int_pul` | `0x33` / `0x37` | Seconds (`0x9a96dc`, `0x9a981c`) |
| Exhaust / board | `temp_fumi` / `temp_scheda` | `0x43` / `0x1b` | °C |

The integration retains the update interval and values provided by the coordinator. `adaptive_on` belongs to `StateInfoResponse` telemetry. The recipe uses `mod_ada_on` from `StateResponse`.

## Evidence and scope

- Craft Anything located names and messages in the ELF using `native_strings_find`. Recipes and settings `ev_c432df8bf7c19cecc5b9b8e87b26868a995d0d82122e8b3faa1619135451a88d`, telemetry `ev_07cb7f835dece4acac15aa812ebb55f181dec088c279fc99bd50c535299d1488` and interface `ev_593baa8b632f8657efe1b930e99f35fcdc034416173ab6aa3ab88175564aca3b`.
- `native_function_pseudocode` used Ghidra 12.1.4 on the original `.text` section, extracted byte by byte from `0x4e0000`. Active and Pellet limits `ev_a4aa594e8b0340dc81f073879f7c22567f533c05f401db827b32776f6d1a39a8`, `ev_5812fd05f1b80dbd90c2e310d3f3ead67e90d8c6a50dfc4473f3b7100ab4ca78`. Active, Pellet and Adaptive command sending `ev_d458c1537fd30a5c8ed28505d373415d5834647f728cacfa9feed5fb13de9ca4`, `ev_1c6737e74337ec168711c092f3edb4e74694b8abeb107e952f48a1c68a5e8278`, `ev_5841fae3a1aae02719d34e897c96565e5a68558bf5d3d5b33fd9c4ea616da5be`. Telemetry table and serializer `ev_d11f17b89ebb6760774def9a7dac4e3d2921fd1ad213e0d9313ebfa72ea09bf6`, `ev_d4f0a0b21b7fc23b4a0178b7c2b34ccacd1fc6dfd096105d9dcb56723a2663be`.
- Effective limits depend on each model’s metadata. Writes were verified in Home Assistant tests using a simulated coordinator. Physical application remains unverified.
