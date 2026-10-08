# Pinecrest Prime LLC – dashboard

A private, view-only dashboard of Luca's investment income and house expenses.

- **Website:** https://carolinam19.github.io/pinecrest-prime/
- **Access:** the data in `data.enc.json` is encrypted. It can only be opened in the browser with the site password. Nothing readable is stored in this repository.
- **Updates:** Carolina keeps the records in her Claude dashboard. Claude publishes a fresh encrypted copy here every morning (and on request) with `tools/publish.py`, which only needs the public key in `keys.json`, not the password.

To change the password, ask Claude to create a new key pair and republish.
