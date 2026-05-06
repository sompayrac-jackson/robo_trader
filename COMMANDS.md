# Robo Trader — Command Reference

## Droplet / App

| Task | Command |
|------|---------|
| View app status | `systemctl status robo_trader` |
| Start app | `systemctl start robo_trader` |
| Stop app | `systemctl stop robo_trader` |
| Restart after code changes | `systemctl restart robo_trader` |
| Watch live logs | `journalctl -u robo_trader -f` |

## Deploying Code Changes

```bash
git pull
systemctl restart robo_trader
```

## Virtual Environment

```bash
source venv/bin/activate       # activate (needed if running manually)
pip install <package>          # install a package while venv is active
```

## Run Manually (without systemd)

```bash
source venv/bin/activate
python app.py                  # web dashboard
python scheduler.py            # trading bot scheduler
python trader.py               # single trade run
```

## Security

```bash
chmod 600 .env                 # restrict .env to owner only
ls -la .env                    # verify permissions (-rw-------)
ufw status                     # check firewall
ufw allow 5000                 # open port 5000 if blocked
```

## Dashboard

| Page | URL |
|------|-----|
| Portfolio | http://104.248.62.36:5000 |
| Scan Signals | http://104.248.62.36:5000/scan |
