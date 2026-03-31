# FurnishedFinderSender

Automatically sends booking inquiry messages to all listings in your Furnished Finder favorites.

## Pre-requisites

**1. Install Python**

https://www.python.org/downloads/

**2. Install uv**

https://docs.astral.sh/uv/getting-started/installation/

## Setup

**1. Install dependencies**

```bash
uv sync
uv run playwright install chromium
```

**2. Configure environment**

Copy the template and fill in your values:

```bash
cp .env.template .env
```

| Variable | Description | Default |
|---|---|---|
| `EMAIL` | Your Furnished Finder account email | required |
| `MOVE_IN_DATE` | Move-in date (MM/DD/YYYY) | `05/01/2026` |
| `MOVE_OUT_DATE` | Move-out date (MM/DD/YYYY) | blank |
| `NUM_PEOPLE` | Number of occupants — leave blank to use each listing's bedroom count | blank |
| `CONTACT_METHOD` | `Email`, `Text`, `Any`, or `Phone` | `Email` |
| `TRAVEL_REASON` | `Other`, `Digital Nomad`, `Insurance Housing`, `Traveling Healthcare`, `Long Term Housing`, `Business/Work`, `Military`, `Student`, or `Relocation/Transition` | `Other` |
| `HAS_PETS` | `Yes` or `No` | `No` |
| `MESSAGE` | Message to send to each landlord | required |

## Usage

```bash
uv run main.py
```

The script will:

1. Open a browser and navigate to Furnished Finder
2. Enter your email and click Login — a one-time code is sent to your inbox
3. Prompt you in the terminal to enter that code
4. Scrape all listings from your favorites (paginating automatically)
5. Visit each listing and submit a booking inquiry with your trip details
