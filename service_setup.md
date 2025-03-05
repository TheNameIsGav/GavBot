Service for the Script
Now we're going to define the service to run this script:

---

cd /lib/systemd/system/

sudo nano bot.service

---

[Unit]
Description=bot World
After=multi-user.target

[Service]
Type=simple
ExecStart=/usr/bin/python /home/pi/bot_world.py
Restart=on-abort

[Install]
WantedBy=multi-user.target

---

Now that we have our service we need to activate it:

sudo chmod 644 /lib/systemd/system/bot.service

chmod +x /home/pi/bot_world.py

sudo systemctl daemon-reload

sudo systemctl enable bot.service

sudo systemctl start bot.service

# Service Tasks

For every change that we do on the /lib/systemd/system folder we need to execute a daemon-reload (third line of previous code). If we want to check the status of our service, you can execute:

sudo systemctl status bot.service

In general:

Check status
sudo systemctl status bot.service

Start service
sudo systemctl start bot.service

Stop service
sudo systemctl stop bot.service

Check service's log
sudo journalctl -f -u bot.service