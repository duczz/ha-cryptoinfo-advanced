## Cryptoinfo Advanced — Cryptocurrency Home Assistant Sensor Component
[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/hacs/integration)

### Powered by CoinGecko, CryptoID and Mempool.space APIs

Provides Home Assistant sensors for cryptocurrencies and blockchain data across multiple APIs.

If you like this project, please consider supporting it:

<a href="https://www.buymeacoffee.com/TheHoliestRoger" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me an Aubergine" style="height: 60px !important;width: 217px !important;"></a>

<details>
  <summary>BTC donation address</summary>
  bc1qpq4djuxgxsk0zrkg9y2rye8fyz7e0mjx64gzq0
</details>

Originally started from [Cryptoinfo](https://github.com/heyajohnny/cryptoinfo), significantly extended with additional features.

**Minimum Home Assistant version: 2024.1.0**

---

## Installation

### Step 1 — Add the integration

**Option A — HACS (recommended):**
Download *Cryptoinfo Advanced* from the HACS store.

**Option B — Manual:**
Copy the `custom_components/cryptoinfo_advanced/` folder into your HA config directory.

### Step 2 — Add a sensor via UI

Go to **Settings → Devices & Services → Add Integration** and search for *Cryptoinfo Advanced*.

Each sensor is its own integration entry. The setup wizard has two steps:

**Step 1 — Core parameters:**
- **API Mode** — choose the data source (e.g. `price_main`, `mempool_fees`)
- **Cryptocurrency** — coin name or symbol (e.g. `bitcoin`, `btc`)
- **Currency** — conversion currency (e.g. `eur`, `usd`)
- **Unit of Measurement** — displayed unit (e.g. `€`, `$`, `sat/vB`)
- **Update Frequency** — polling interval in minutes (default: 60)
- **CoinGecko API Key** — optional, required for price sensors

**Step 2 — Advanced settings** (optional, mode-specific):
- **Multiplier** — multiply the state value (default: `1`)
- **Max Fetch Failures** — failures before unavailable (default: `3`)
- **Extra Sensors** — select which attributes to expose as separate entities
- Additional parameters depending on the chosen API mode (pool name, difficulty window, etc.)

To add more sensors, click **Add Integration** again — each sensor is a separate entry.

To edit an existing sensor, click **Configure** on the entry in the integration list.

> **Note:** A free CoinGecko API key is required since 2024 for price sensors. Register at [coingecko.com](https://www.coingecko.com/en/api) and use the Demo key.

---

## CoinGecko API Key

CoinGecko requires a free API key for all requests since 2024. Without a key, price sensors will return HTTP 429 errors.

Enter the key in the **API Key** field when adding or editing a price sensor via the UI.

**Supported sensor types:** `price_main`, `price_simple`, `dominance`

For available `cryptocurrency_name` values: https://api.coingecko.com/api/v3/coins/list
For available `currency_name` values: https://api.coingecko.com/api/v3/simple/supported_vs_currencies

---

## Services (Functions)

The integration provides the following Home Assistant services:

### `cryptoinfo_advanced.reload`
Reloads all `cryptoinfo_advanced` sensor entities and their configurations without requiring a full Home Assistant restart. This is useful when you have modified configurations or want to forcefully re-initialize the integration.

---

## Common Sensor Parameters

All sensors share the following parameters (configured via the UI setup wizard):

| Parameter | Default | Description |
| --- | --- | --- |
| **API Mode** | `price_main` | Data source and type — see API modes below. |
| **Cryptocurrency** | `bitcoin` | Coin/token name or symbol depending on the API. |
| **Currency** | `usd` | Conversion currency (for price sensors). |
| **Unit of Measurement** | `$` | Unit displayed in the UI. |
| **Multiplier** | `1` | Multiplied with the state value. |
| **Update Frequency** | `60` | Update interval in minutes. |
| **API Key** | `""` | CoinGecko API key (required for price sensors). |
| **Max Fetch Failures** | `3` | Consecutive failures before the sensor becomes unavailable. |
| **Extra Sensors** | `[]` | Additional child entities derived from attributes — see each mode below. |

---

## API Modes

| Mode | Source | Description |
| --- | --- | --- |
| `price_main` | CoinGecko | Full price data with extended attributes. |
| `price_simple` | CoinGecko | Lightweight price data. |
| `dominance` | CoinGecko | Market dominance percentage. |
| `chain_summary` | CryptoID | Blockchain summary: block height, hashrate, difficulty. |
| `chain_control` | CryptoID | Mining pool hashrate control. |
| `chain_orphans` | CryptoID | Orphaned blocks in the past 24 hours. |
| `chain_block_time` | CryptoID | Unix timestamp of a specific block height. |
| `nomp_pool_stats` | NOMP | Pool stats from any NOMP-based mining pool. |
| `mempool_stats` | Mempool.space | Mempool size and fee data (Bitcoin only). |
| `mempool_fees` | Mempool.space | Recommended fee rates (Bitcoin only). |
| `mempool_next_block` | Mempool.space | Projected next block data (Bitcoin only). |

---

## Sensor Reference

### Price (Main) — `price_main`

**State:** `baseprice × multiplier`

#### Attributes

| Attribute | Description |
| --- | --- |
| `baseprice` | Price of 1 coin in `currency_name`. |
| `24h_volume` | 24-hour trading volume. |
| `1h_change` | 1-hour price change in %. |
| `24h_change` | 24-hour price change in %. |
| `7d_change` | 7-day price change in %. |
| `30d_change` | 30-day price change in %. |
| `24h_low` | 24-hour low price. |
| `24h_high` | 24-hour high price. |
| `market_cap` | Total market cap in `currency_name`. |
| `circulating_supply` | Circulating supply. |
| `total_supply` | Total supply. |
| `all_time_high` | All-time high price. |
| `all_time_high_date` | Date of the all-time high. |
| `all_time_low` | All-time low price. |
| `all_time_low_date` | Date of the all-time low. |
| `image_url` | URL to the coin icon. |
| `last_update` | Timestamp of the last successful update. |

#### Extra Sensor Properties

| Property | Description |
| --- | --- |
| `all_time_high_distance` | Distance from current price to ATH in `currency_name`. |
| `all_time_high_days` | Days since ATH. |
| `all_time_low_days` | Days since ATL. |

---

### Price (Simple) — `price_simple`

**State:** `baseprice × multiplier`

#### Attributes

| Attribute | Description |
| --- | --- |
| `baseprice` | Price of 1 coin in `currency_name`. |
| `24h_volume` | 24-hour trading volume. |
| `24h_change` | 24-hour price change in %. |
| `market_cap` | Total market cap in `currency_name`. |
| `last_update` | Timestamp of the last successful update. |

---

### Market Dominance — `dominance`

**State:** Dominance percentage (rounded to 2 decimal places).

#### Attributes

| Attribute | Description |
| --- | --- |
| `market_cap` | Total market cap of `cryptocurrency_name` in USD. |
| `last_update` | Timestamp of the last successful update. |

---

### Blockchain Summary — `chain_summary`

**State:** Current block height.

#### Attributes

| Attribute | Description |
| --- | --- |
| `circulating_supply` | Circulating supply. |
| `hashrate` | Network hashrate. |
| `difficulty` | Current mining difficulty. |
| `last_update` | Timestamp of the last successful update. |

#### Parameters

| Parameter | Default | Description |
| --- | --- | --- |
| `difficulty_window` | `2016` | Number of blocks per difficulty retarget window. |
| `diff_multiplier` | `4294967296` | Maximum nonces (2³²) used for difficulty calculations. |
| `block_time_minutes` | `10.0` | Target minutes between blocks. |
| `halving_window` | `210000` | Number of blocks per halving window. |

#### Extra Sensor Properties

| Property | Description |
| --- | --- |
| `difficulty_calc` | Difficulty scaled by `unit_of_measurement`. |
| `hashrate_calc` | Hashrate scaled by `unit_of_measurement`. |
| `block_time_in_seconds` | Estimated seconds between blocks (requires a `chain_summary` or `nomp_pool_stats` sensor for the same coin). |
| `difficulty_block_progress` | Current block count within the difficulty window. |
| `difficulty_retarget_height` | Block height of the next difficulty retarget. |
| `difficulty_retarget_seconds` | Estimated seconds until the next retarget. |
| `difficulty_retarget_percent_change` | Estimated difficulty change at the next retarget (%). |
| `difficulty_retarget_estimated_diff` | Estimated difficulty value at the next retarget. |
| `halving_block_progress` | Current block count within the halving window. |
| `halving_blocks_remaining` | Blocks remaining until the next halving. |
| `next_halving_height` | Block height of the next halving. |
| `total_halvings_to_date` | Total halvings that have occurred. |

---

### Blockchain Hashrate Control — `chain_control`

**State:** Blocks mined by `pool_prefix` in the last 100 blocks.

#### Attributes

| Attribute | Description |
| --- | --- |
| `pool_control_1000b` | Blocks mined by `pool_prefix` in the last 1000 blocks. |

#### Parameters

| Parameter | Default | Description |
| --- | --- | --- |
| `pool_prefix` | `""` | Pool prefix(es) to track. Set to `remaining_percentage` to calculate unknown pool control. Accepts lists. |

#### Extra Sensor Properties

| Property | Description |
| --- | --- |
| `pool_control_1000b_perc` | Percentage of the last 1000 blocks mined by `pool_prefix`. |

---

### Blockchain Orphans — `chain_orphans`

**State:** Total orphaned blocks in the past 24 hours.

---

### Block Timestamp — `chain_block_time`

**State:** Unix epoch timestamp of the specified block height.

#### Attributes

| Attribute | Description |
| --- | --- |
| `block_height` | Block height of the fetched timestamp. |

#### Parameters

| Parameter | Default | Description |
| --- | --- | --- |
| `fetch_args_template` | `""` | Block height to fetch the timestamp for. Accepts HA templates. If empty, fetches the last difficulty retarget block. |

---

### NOMP Pool Stats — `nomp_pool_stats`

**State:** Current hashrate of the NOMP pool.

#### Attributes

| Attribute | Description |
| --- | --- |
| `hashrate` | Pool hashrate. |
| `block_height` | Current block height reported by the pool. |
| `worker_count` | Total active workers. |
| `last_block` | Last block mined by the pool. |
| `blocks_pending` | Total pending blocks. |
| `blocks_confirmed` | Total confirmed blocks. |
| `blocks_orphaned` | Total orphaned blocks. |

#### Parameters

| Parameter | Default | Description |
| --- | --- | --- |
| `api_domain_name` | `""` | **Required.** Domain of the NOMP pool (include subdomain if applicable). |
| `pool_name` | `""` | **Required.** Pool name as reported by the NOMP API. |

#### Extra Sensor Properties

| Property | Description |
| --- | --- |
| `hashrate_calc` | Pool hashrate scaled by `unit_of_measurement`. |

---

### Mempool Stats — `mempool_stats` *(Bitcoin only)*

**State:** Total mempool size in vBytes.

#### Attributes

| Attribute | Description |
| --- | --- |
| `mempool_tx_count` | Total transactions in the mempool. |
| `mempool_total_fee` | Total fees of all mempool transactions in satoshis. |

#### Extra Sensor Properties

| Property | Description |
| --- | --- |
| `mempool_size_calc` | Mempool size scaled by `unit_of_measurement`. |
| `mempool_total_fee_calc` | Total mempool fees scaled by `unit_of_measurement`. |
| `mempool_average_fee_per_tx` | Average fee per transaction in satoshis. |

---

### Mempool Fee Rates — `mempool_fees` *(Bitcoin only)*

**State:** Fastest recommended fee rate in sat/vB.

#### Attributes

| Attribute | Description |
| --- | --- |
| `mempool_fees_fastest` | Fastest confirmation fee rate (sat/vB). |
| `mempool_fees_30min` | Fee rate for ~30-minute confirmation (sat/vB). |
| `mempool_fees_60min` | Fee rate for ~60-minute confirmation (sat/vB). |
| `mempool_fees_eco` | Economy fee rate (sat/vB). |
| `mempool_fees_minimum` | Minimum relay fee rate (sat/vB). |

---

### Mempool Next Block — `mempool_next_block` *(Bitcoin only)*

**State:** Projected size of the next block in vBytes.

#### Attributes

| Attribute | Description |
| --- | --- |
| `mempool_next_block_tx_count` | Projected transaction count in the next block. |
| `mempool_next_block_total_fee` | Projected total fees in the next block (satoshis). |
| `mempool_next_block_median_fee` | Projected median fee rate (sat/vB). |
| `mempool_next_block_fee_range_combined` | Fee range as a formatted string, e.g. `12 - 45`. |
| `mempool_next_block_fee_range_min` | Minimum fee rate in the projected next block (sat/vB). |
| `mempool_next_block_fee_range_max` | Maximum fee rate in the projected next block (sat/vB). |

#### Extra Sensor Properties

| Property | Description |
| --- | --- |
| `mempool_next_block_size_calc` | Next block size scaled by `unit_of_measurement`. |
| `mempool_next_block_total_fee_calc` | Next block total fees scaled by `unit_of_measurement`. |

---

## Issues and Feature Requests

Please report bugs or request features at:
https://github.com/TheHolyRoger/hass-cryptoinfo/issues
