## GitHub Copilot Chat

- Extension Version: 0.22.4 (prod)
- VS Code: vscode/1.95.3
- OS: Mac

## Network

User Settings:
```json
  "github.copilot.advanced": {
    "debug.useElectronFetcher": true,
    "debug.useNodeFetcher": false
  }
```

Connecting to https://api.github.com:
- DNS ipv4 Lookup: 4.225.11.201 (25 ms)
- DNS ipv6 Lookup: ::ffff:4.225.11.201 (1 ms)
- Electron Fetcher (configured): HTTP 200 (192 ms)
- Node Fetcher: HTTP 200 (96 ms)
- Helix Fetcher: HTTP 200 (388 ms)

Connecting to https://api.individual.githubcopilot.com/_ping:
- DNS ipv4 Lookup: 140.82.112.21 (2 ms)
- DNS ipv6 Lookup: ::ffff:140.82.112.21 (1 ms)
- Electron Fetcher (configured): HTTP 200 (354 ms)
- Node Fetcher: HTTP 200 (359 ms)
- Helix Fetcher: HTTP 200 (364 ms)

## Documentation

In corporate networks: [Troubleshooting firewall settings for GitHub Copilot](https://docs.github.com/en/copilot/troubleshooting-github-copilot/troubleshooting-firewall-settings-for-github-copilot).