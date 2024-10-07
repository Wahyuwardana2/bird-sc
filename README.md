# trying to degen

## Worms Listing and Unlisting Script

This script automates the process of scraping, unlisting, and listing items on the Worms platform using the Worms API. The script reads the necessary authentication data from a local `auth.txt` file and processes items based on their current status.

## Features

- Scrape items from Worms API.
- Unlist items that are currently listed.
- Relist items automatically after unlisting with custom prices based on item types.
- Configurable delay to avoid rate limits.

## Requirements

Make sure you have Python 3 installed on your machine. To install the required Python packages, run:

```bash
pip install -r requirements.txt
```
