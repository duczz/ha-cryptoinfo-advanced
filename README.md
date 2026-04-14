[![HA Version](https://img.shields.io/badge/HA%20Minimum-2024.1.0-blue)](https://www.home-assistant.io)
[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/hacs/integration)

## Cryptoinfo Advanced — Cryptocurrency Home Assistant Integration
This is a Fork from https://github.com/TheHolyRoger/hass-cryptoinfo & https://github.com/heyajohnny/cryptoinfo

### An all-in-one data center for Crypto and Blockchain enthusiasts.
Powered by trustworthy APIs from **CoinGecko**, **CryptoID**, and **Mempool.space**.

Add comprehensive cryptocurrency prices, blockchain statistics, mining pool hashrates, and real-time Mempool data directly into your Home Assistant dashboards. Create powerful automations based on market movements or network congestion!

---

## Support me ☕

If you like this integration and would like to support my work, I would appreciate a small donation. <br>
Thank you very much for your support! ❤️

<a href="https://www.paypal.com/donate/?hosted_button_id=GBCCKFTK5FVX4">
  <img src="https://github.com/duczz/ha-cryptoinfo-advanced/blob/master/.github/paypal_donation_logo.png?raw=true" width="230" alt="Donate with PayPal">
</a>

---

## 🛠️ Installation & Setup

### Step 1: Install the Integration

**Option A — HACS (Recommended):**
1. Go to **HACS** in your Home Assistant.
2. Click on **Integrations** → **Explore & Download Repositories**.
3. Search for *Cryptoinfo Advanced* and download it.
4. Restart Home Assistant.

**Option B — Manual Installation:**
Copy the `custom_components/cryptoinfo_advanced/` folder from this repository into your Home Assistant `config/custom_components/` directory and restart.

### Step 2: Add your first Sensor

The integration works by adding individual sensors one by one. This gives you complete control over what data you fetch and how often.

1. Go to **Settings → Devices & Services → Add Integration**.
2. Search for **Cryptoinfo Advanced**.
3. Choose the **API Mode** (e.g. `price_main` for full price data, or `mempool_fees` for Bitcoin transaction fees).
4. Fill out the relevant details (Coin name, Currency, etc.) and click **Submit**.
5. *Optional:* The next screen lets you dive into **Advanced Settings**. Here you can extract attributes into their own separate entities using the **Extra Sensors** dropdown.

To add more sensors (e.g., Ethereum price, Bitcoin Mempool size), simply click **Add Integration** again and repeat the process!

---

## 🔑 CoinGecko API Key (Recommended for Price Sensors)

If you want to track **Prices or Dominance** using CoinGecko (Modes: `price_main`, `price_simple`, `dominance`), it is **strongly recommended** to use a free API key.

**Without a key:** CoinGecko's public API allows only 5–15 requests per minute. The integration handles this gracefully (see Rate Limit Handling below), but with many sensors you may occasionally see delayed updates.

**With a free API key:** The rate limit increases to ~30 requests per minute, which is sufficient for most setups.

1. Go to [CoinGecko API](https://www.coingecko.com/en/api) and create a free account.
2. Generate a **API Key**.
3. Enter this key in the **API Key** field when setting up your sensor in Home Assistant.

*Note: You only need the API key for CoinGecko. Other sources (CryptoID, Mempool, NOMP) do not require keys.*

---

## 📊 Available API Modes (Data Sources)

When creating a new sensor, you must choose an **API Mode**. This determines what kind of data the sensor will fetch.

### 💰 1. Cryptocurrency Prices (CoinGecko)
*Requires a free CoinGecko API key.*

- **`price_main` - Full Price Data & Market Overview**
  Provides the current price and a massive list of attributes: 24h volume, 1h/24h/7d/30d changes, Market Cap, Circulating Supply, All-Time Highs/Lows, and more.
- **`price_simple` - Lightweight Price Data**
  A simplified version containing only the most basic price and 24h data. Useful if you want to track hundreds of coins without overloading Home Assistant.
- **`dominance` - Market Dominance**
  Tracks the percentage of total crypto market cap that belongs to a specific coin (usually Bitcoin).

### 🔗 2. Blockchain & Mining Data (CryptoID & NOMP)

- **`chain_summary` - Network Overview**
  Tracks the current Block Height, Network Hashrate, and Mining Difficulty.
- **`chain_control` - Pool Dominance Tracker**
  Tracks how many blocks a specific mining pool (e.g., Foundry, AntPool) mined in the last 100 or 1000 blocks.
- **`chain_orphans` - Network Health**
  Tracks how many orphaned blocks occurred in the last 24 hours.
- **`chain_block_time` - Block Timestamp**
  Returns the exact date/time a specific block was mined.
- **`nomp_pool_stats` - Custom NOMP Mining Pools**
  Track the hashrate, pending blocks, and connected workers of any standard NOMP-based mining pool.

### ⚡ 3. Bitcoin Mempool & Fees (Mempool.space)
*These modes are strictly for Bitcoin (`btc`).*

- **`mempool_fees` - Recommended Transaction Fees**
  Provides the current recommended `sat/vB` fees. Exposes attributes for Fastest, 30-min, 60-min, Economy, and Minimum fees. Great for automations that alert you when network fees are low!
- **`mempool_stats` - Mempool Status**
  Tracks the total size of the unconfirmed Mempool (in vBytes) and the total number of unconfirmed transactions.
- **`mempool_next_block` - Next Block Projections**
  Estimates the size and total fees of the very next block to be mined.

---

## ⚙️ Advanced Features

### 🧩 "Extra Sensors" (Extracting Attributes)
Many sensors download a lot of data grouped into "Attributes" (e.g., a `price_main` sensor has the price as its main state, but hides 24h volume, ATH, and 7d changes inside its attributes).

During setup (or by clicking **Configure** on an existing sensor), you can use the **Extra Sensors** dropdown. This allows you to select any of those hidden attributes and instantly turn them into their own standalone Home Assistant entities! 

*Example: You can extract `all_time_high_distance` to easily display how far Bitcoin is from its ATH on your dashboard.*

### 🔄 Multipliers & Units
- **Multiplier:** You can use this to tweak values. For example, if you hold `0.5` Bitcoin, set the multiplier to `0.5` — the sensor will now directly show the value of *your* holdings instead of the price of 1 full Bitcoin.
- **Unit of Measurement:** You define what unit to show in the UI (`$`, `€`, `sat/vB`, `EH/s`).

### ⏱️ Rate Limit Handling (CoinGecko)

The integration includes built-in protection against CoinGecko's API rate limits (Public API: 5–15 calls/min depending on worldwide usage; API key: ~30 calls/min):

**Shared API calls:** Multiple sensors tracking the same coin and currency (e.g. two sensors for `bitcoin` / `eur` with different multipliers) share a single API call. The result is cached and reused — no duplicate requests.

**Automatic backoff on HTTP 429:** If CoinGecko returns a rate limit error, all sensors automatically pause their requests to that domain for 60 seconds (or the duration specified in the `Retry-After` response header). Sensors that were blocked during this cooldown automatically schedule up to 3 retries once the cooldown expires — so no manual intervention is needed.

#### Example: 6 sensors at startup (no API key)

| Time | Sensor | Action | Result |
|------|--------|--------|--------|
| t=0s | Bitcoin/EUR | First fetch | ✅ Data received |
| t=0s | BTC Dominance | First fetch | ✅ Data received |
| t=0s | Ethereum/EUR | First fetch | ✅ Data received |
| t=0s | Fetch-AI/EUR | First fetch | ❌ HTTP 429 → domain blocked 60s, Retry #1 scheduled in 61s |
| t=0s | Solana/EUR | Domain blocked | ⏳ Skipped → Retry #1 scheduled in 61s |
| t=0s | Sui/EUR | Domain blocked | ⏳ Skipped → Retry #1 scheduled in 61s |
| t=61s | Fetch-AI/EUR | Retry #1 | ✅ Data received |
| t=61s | Solana/EUR | Retry #1 | ✅ Data received |
| t=61s | Sui/EUR | Retry #1 | ✅ Data received |

→ **All sensors have data within ~61 seconds**, even without an API key.

If retries also hit a 429, the process repeats up to 3 times total. After that, the normal update interval takes over.

### 🛠️ Reload Service
If you ever need to forcefully restart the integration without rebooting Home Assistant:
Go to **Developer Tools → Services** and call `cryptoinfo_advanced.reload`. This cleanly restarts all your sensors.

---

## 📝 Common Sensor Parameters

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

## 📖 Detailed Sensor Reference

### Price (Main) — `price_main`

**State:** `base_price × multiplier`

#### Attributes

| Attribute | Description |
| --- | --- |
| `base_price` | Price of 1 coin in `currency_name`. |
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

**State:** `base_price × multiplier`

#### Attributes

| Attribute | Description |
| --- | --- |
| `base_price` | Price of 1 coin in `currency_name`. |
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

## ❓ Troubleshooting & Finding Coin Names

**"My CoinGecko sensor is Unavailable/Unknown!"**
Make sure you are using the correct `cryptocurrency_name` and `currency_name`.
- List of valid Coins: [CoinGecko Coin List](https://api.coingecko.com/api/v3/coins/list) (use the `id` field, e.g., `bitcoin`, `ethereum`, `shiba-inu`).
- List of valid Currencies: [Supported vs_currencies](https://api.coingecko.com/api/v3/simple/supported_vs_currencies) (e.g., `usd`, `eur`, `btc`).
- Ensure you have entered a valid API Key.

**"My Mempool sensors aren't working!"**
Make sure you typed `bitcoin` or `btc` in the Cryptocurrency field. Mempool sensors only work for the Bitcoin network.

---
