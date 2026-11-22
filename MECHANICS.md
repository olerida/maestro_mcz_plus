# Mecánica de Maestro+ MCZ 5.8.0

Se analizó el APK `it.mcz.maestro.apk` y su biblioteca Dart AOT ARM de 32 bits, `lib/armeabi-v7a/libapp.so`, incluida en `config.armeabi_v7a.apk`. SHA-256 de la biblioteca: `d70fdfabd3dfa3a3e458e804d607af3cf38470d71f87e60112ce3821756e5e47`. Las direcciones siguientes son virtuales en el ELF original. Si Ghidra importa el ELF con base `0x10000`, suma esa base a las direcciones de función. Ghidra y el desensamblado ARM se contrastaron con la tabla de instrucciones y las referencias del pool de objetos de Dart 3.11.5.

## Lectura y límites de receta

| Ajuste | Campo del estado | Función de lectura | Offset del campo |
| --- | --- | --- | --- |
| Activo, valor | `pos_ric_flu` | `RecipePage.get:posRicFluValueSelected` · `0x9cc9e8` | `0x07` |
| Activo, habilitado | `act` | `RecipePage.get:isActiveOn` · `0x9cc734` | `0x10f` |
| Pellet | `pos_ric_pel` | `RecipePage.get:pelletValueSelected` · `0x9cc6e4` | `0xab` |
| Adaptación | `mod_ada_on` | `RecipePage.get:modAdaOn` · `0x9cc594` | `0x11b` |

Los offsets son relativos al puntero etiquetado del objeto Dart. Los getters coinciden con `StateResponseFromJson` (`0x5bde84`) y `StateResponseToJson` (`0x573c78`). La aplicación añade el signo `+` a un valor positivo en la presentación de Activo (`0x9cc8e8`). Home Assistant conserva el valor numérico.

- **Activo.** `get:commandSensorPosRicFlu` (`0x94cb2c`) obtiene el sensor de la configuración del modelo. `get:sliderRange` (`0x94ca84`) convierte a número sus límites de los offsets `0x17` y `0x1b`. El paso del control es `1.0` (`0x94c4ec`, dentro de `0x94c284`).
- **Pellet.** `createSlider` (`0x95cb60`) convierte el mínimo y máximo de esos mismos offsets, calcula `máximo − mínimo` (`0x95ce10`) y configura un paso de `1.0` (`0x95cf3c`). Los métodos de envío de Activo y Pellet convierten la selección en un entero antes de construir el comando.
- **Home Assistant.** Para representar ajustes enteros, el mínimo se calcula como `ceil(Min)` y el máximo como `floor(Max)`. Se requieren ambos límites finitos con al menos un entero posible. La integración ofrece los controles avanzados para metadatos habilitados de un modelo reconocido. El intervalo −3 a +3 era el observado en una Ego Comfort Air y ahora se toma del modelo conectado.

## Guardado

| Ajuste | Función de envío | Comandos en el orden de la app |
| --- | --- | --- |
| Activo | `0x94cf34` | `SENSOR_PELLET_ACT_VALUE` (entero), luego `SENSOR_PELLET_ACT` (booleano) |
| Pellet | `0x95d4bc` | `SENSOR_PALLET` (entero) |
| Adaptación | `0x94de98` | `SENSOR_PELLET_MOD_ADA_ON` (booleano) |

La app obtiene los UUID por familia de sensores en `listConfigurations` (`0x56e2fc`) y `listSensorsId` (`0x56e514`). Los getters de Activo buscan los dos sensores en la configuración seleccionada (`0x94cb2c`, `0x94d4c8`). Los mapas del snapshot emparejan estas claves con los siguientes UUID.

| Clave | AIR / HYBRID | HYDRO |
| --- | --- | --- |
| `CONFIGURATION_PELLET` | `f6538f6b-ef3d-4ed7-9ab6-4b3b97fc0e1f` | `62bfda67-95b2-4372-804d-0f7013d857e0` |
| `SENSOR_PALLET` | `e50abf4a-6e52-487c-8637-1d00d8978359` | `8c59dc5a-4e7d-4706-8ac3-e144ed8a9515` |
| `SENSOR_PELLET_ACT_VALUE` | `307ba615-e58f-4df0-944a-a1df97c73e06` | `8056d063-f5e0-48c7-9960-90b48ca81798` |
| `SENSOR_PELLET_ACT` | `2998639c-8240-4bc5-9331-2b9aa9ffc1a2` | `9156d446-2062-40c7-bea7-4934c5e5d79a` |
| `SENSOR_PELLET_MOD_ADA_ON` | `f5ee03fd-7f71-48fb-8e71-46d5d4cf56d5` | `b22fb6e1-d8d2-4857-b9bf-07bfcf10fe91` |

`activateAProgram` (`0x558974`) hace un `POST` a `/mcz/v1.0/Program/ActivateProgram/{id}`. El serializador de la petición (`0x558d38`) usa `ModelId`, `ConfigurationId`, `SensorSetTypeId` y `Commands`. El serializador de cada comando (`0x566338`) escribe `SensorId` y `Value` con el tipo del valor entregado. La integración delega el envío en Maestro MCZ. Cuando se modifica un ajuste de Activo, consulta el otro, envía los dos en el orden de la app y confirma el resultado con una consulta posterior.

## Datos de funcionamiento

`StateInfoResponseFromJson` (`0xa26cac`) y `StateInfoResponseToJson` (`0xa263ac`) enlazan estos campos con la tabla de la app (`HowItWorksInfoPage.buildBodyTableLayout`, `0x9a86dc`).

| Lectura | Campo | Offset | Presentación de la app |
| --- | --- | --- | --- |
| Extractor, solicitado / real | `vel_imp_ventola_fumi` / `vel_real_ventola_fumi` | `0x03` / `0x07` | RPM |
| Sinfín, solicitado / real | `vel_imp_coclea` / `vel_real_coclea` | `0x0b` / `0x0f` | RPM |
| Activo, solicitado / real | `pressione_imp` / `pressione` | `0x17` / `0x13` | Valores directos, sin unidad indicada |
| Potencia activa / duración | `potenza_att` / `potenza_counter` | `0x2b` / `0x2f` | Valores directos, sin unidad indicada |
| Limpieza prevista / restante | `t_dur_pul` / `t_int_pul` | `0x33` / `0x37` | Segundos (`0x9a96dc`, `0x9a981c`) |
| Humos / placa | `temp_fumi` / `temp_scheda` | `0x43` / `0x1b` | °C |

La integración conserva la frecuencia de actualización y los valores proporcionados por el coordinador. `adaptive_on` pertenece a la telemetría de `StateInfoResponse`. La receta usa `mod_ada_on` de `StateResponse`.

## Evidencia y alcance

- Craft Anything localizó los nombres y mensajes en el ELF con `native_strings_find`. Recetas y ajustes `ev_c432df8bf7c19cecc5b9b8e87b26868a995d0d82122e8b3faa1619135451a88d`, telemetría `ev_07cb7f835dece4acac15aa812ebb55f181dec088c279fc99bd50c535299d1488` e interfaz `ev_593baa8b632f8657efe1b930e99f35fcdc034416173ab6aa3ab88175564aca3b`.
- `native_function_pseudocode` usó Ghidra 12.1.4 sobre la sección `.text` original, extraída byte a byte desde `0x4e0000`. Límites de Activo y Pellet `ev_a4aa594e8b0340dc81f073879f7c22567f533c05f401db827b32776f6d1a39a8`, `ev_5812fd05f1b80dbd90c2e310d3f3ead67e90d8c6a50dfc4473f3b7100ab4ca78`. Envío de Activo, Pellet y Adaptación `ev_d458c1537fd30a5c8ed28505d373415d5834647f728cacfa9feed5fb13de9ca4`, `ev_1c6737e74337ec168711c092f3edb4e74694b8abeb107e952f48a1c68a5e8278`, `ev_5841fae3a1aae02719d34e897c96565e5a68558bf5d3d5b33fd9c4ea616da5be`. Tabla y serializador de telemetría `ev_d11f17b89ebb6760774def9a7dac4e3d2921fd1ad213e0d9313ebfa72ea09bf6`, `ev_d4f0a0b21b7fc23b4a0178b7c2b34ccacd1fc6dfd096105d9dcb56723a2663be`.
- Los límites efectivos dependen de los metadatos que devuelve cada modelo. Las escrituras se verificaron en pruebas de Home Assistant con un coordinador simulado. Su aplicación física queda pendiente de una prueba con la estufa.
