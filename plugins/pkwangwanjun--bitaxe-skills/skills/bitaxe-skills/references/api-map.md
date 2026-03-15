# Bitaxe Skills API Map

## Source Endpoints

- Discovery and reads: `GET /api/system/info`
- Restart: `POST /api/system/restart`
- Common settings updates: `PATCH /api/system`

Bitaxe documents these endpoints in the official ESP-Miner README and OpenAPI spec:
- https://github.com/bitaxeorg/ESP-Miner
- https://raw.githubusercontent.com/bitaxeorg/ESP-Miner/master/main/http_server/openapi.yaml

The NerdAxe fork states that it uses the same Bitaxe API functions and supports system setting updates:
- https://github.com/BitMaker-hub/ESP-Miner-NerdAxe

Inference:
- Treat `PATCH /api/system` as the common write path for both Bitaxe and Nerd firmware families.
- Treat exact writable fields on Nerd firmware as fork-dependent unless they are part of the documented common Bitaxe settings or already visible in the device payload.

## Device Identification

- Identify `bitaxe` when the payload includes keys such as `axeOSVersion`, `ipv4`, or `boardVersion`.
- Identify `nerd` when the payload includes keys such as `deviceModel`, `hostip`, `hashRate_1d`, or nested `stratum.pools`.
- If the payload does not clearly match either family, keep the raw JSON and report it as `unknown` rather than guessing.

## Normalized Fields

| Normalized field | Bitaxe source | Nerd source | Notes |
| --- | --- | --- | --- |
| `ip` | `ipv4` | `hostip` | Fallback to scanned target if missing |
| `device_type` | derived | derived | `bitaxe`, `nerd`, or `unknown` |
| `hostname` | `hostname` | `hostname` | Common |
| `device_model` | derived from `boardVersion` or `deviceModel` | `deviceModel` | Human label |
| `board_version` | `boardVersion` | `boardVersion` if present | Often Bitaxe-only |
| `asic_model` | `ASICModel` | `ASICModel` | Common |
| `firmware_version` | `axeOSVersion` or `version` | `version` | Prefer AxeOS version when present |
| `wifi_ssid` | `ssid` | `ssid` | Common |
| `wifi_rssi` | `wifiRSSI` | `wifiRSSI` | Common |
| `mac_addr` | `macAddr` | `macAddr` | Common |
| `power_w` | `power` | `power` | Common |
| `voltage_mv` | `voltage` | `voltage` | Device reports millivolts |
| `current_ma` | `current` | `current` | Device reports milliamps |
| `temp_c` | `temp` | `temp` | Main chip temperature |
| `vr_temp_c` | `vrTemp` | `vrTemp` | VR temperature |
| `hash_rate_ghs` | `hashRate` | `hashRate` | Current GH/s |
| `hash_rate_1m_ghs` | `hashRate_1m` | `hashRate_1m` | Common |
| `hash_rate_10m_ghs` | `hashRate_10m` | `hashRate_10m` | Common |
| `hash_rate_1h_ghs` | `hashRate_1h` | `hashRate_1h` | Common |
| `hash_rate_1d_ghs` | not present in sample | `hashRate_1d` | Nerd-specific in sample |
| `best_diff` | `bestDiff` | `bestDiff` | Lifetime best difficulty |
| `best_session_diff` | `bestSessionDiff` | `bestSessionDiff` | Best difficulty for current session or round |
| `pool_difficulty` | `poolDifficulty` | `poolDifficulty` | Common |
| `shares_accepted` | `sharesAccepted` | `sharesAccepted` | Common |
| `shares_rejected` | `sharesRejected` | `sharesRejected` | Common |
| `frequency_mhz` | `frequency` | `frequency` | Common |
| `core_voltage_mv` | `coreVoltage` | `coreVoltage` | Common |
| `pool_url` | `stratumURL` | `stratumURL` | Common |
| `pool_port` | `stratumPort` | `stratumPort` | Common |
| `pool_user` | `stratumUser` | `stratumUser` | Common |
| `fallback_pool_url` | `fallbackStratumURL` | `fallbackStratumURL` | Common |
| `fallback_pool_port` | `fallbackStratumPort` | `fallbackStratumPort` | Common |
| `fallback_pool_user` | `fallbackStratumUser` | `fallbackStratumUser` | Common |
| `uptime_seconds` | `uptimeSeconds` | `uptimeSeconds` | Common |
| `response_time_ms` | `responseTime` | `lastpingrtt` | Network or pool RTT |
| `fan_speed_percent` | `fanspeed` | `fanspeed` | Common |
| `fan_rpm` | `fanrpm` | `fanrpm` | Common |
| `found_blocks` | `blockFound` | `foundBlocks` | Family-specific naming |
| `total_found_blocks` | not present in sample | `totalFoundBlocks` | Nerd sample only |

## Query Heuristics

- "本轮最佳难度" -> `best_session_diff`
- "历史最佳难度" -> `best_diff`
- "池难度" -> `pool_difficulty`
- "当前算力" -> `hash_rate_ghs`
- "最近 1 分钟算力" -> `hash_rate_1m_ghs`
- "最近 10 分钟算力" -> `hash_rate_10m_ghs`
- "最近 1 小时算力" -> `hash_rate_1h_ghs`
- "在线多久" -> `uptime_seconds`
- "矿池地址" -> `pool_url`, plus `pool_port` if needed

When the user asks for a metric without naming the miner, discover first and either:
- answer for all miners, or
- ask which device they want only if multiple devices are found and ambiguity matters.

## Common Writable Settings

Documented common keys from Bitaxe OpenAPI:

- `useFallbackStratum`
- `stratumURL`
- `fallbackStratumURL`
- `stratumUser`
- `stratumPassword`
- `fallbackStratumUser`
- `fallbackStratumPassword`
- `stratumPort`
- `fallbackStratumPort`
- `ssid`
- `wifiPass`
- `hostname`
- `coreVoltage`
- `frequency`
- `rotation`
- `overheat_mode`
- `overclockEnabled`
- `invertscreen`
- `autofanspeed`
- `fanspeed`
- `temptarget`
- `displayTimeout`
- `statsFrequency`

Observed Nerd-specific keys from the supplied payload and worth treating as firmware-dependent:

- `flipscreen`
- `autoscreenoff`
- `invertfanpolarity`
- `stratum_keep`
- `pidTargetTemp`
- `pidP`
- `pidI`
- `pidD`
- `stratumDifficulty`
- `overheat_temp`
- `vrFrequency`

## Restart Rule

- After `PATCH /api/system`, restart when the user expects the new configuration to apply immediately.
- If a write is sent without restart, explicitly note that a restart may still be required for the change to take effect.
