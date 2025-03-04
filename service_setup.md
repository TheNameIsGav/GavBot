Service for the Script
Now we're going to define the service to run this script:

---

cd /lib/systemd/system/

sudo nano hello.service

---

[Unit]
Description=Hello World
After=multi-user.target

[Service]
Type=simple
ExecStart=/usr/bin/python /home/pi/hello_world.py
Restart=on-abort

[Install]
WantedBy=multi-user.target

---

Now that we have our service we need to activate it:

sudo chmod 644 /lib/systemd/system/hello.service

chmod +x /home/pi/hello_world.py

sudo systemctl daemon-reload

sudo systemctl enable hello.service

sudo systemctl start hello.service

# Service Tasks

For every change that we do on the /lib/systemd/system folder we need to execute a daemon-reload (third line of previous code). If we want to check the status of our service, you can execute:

sudo systemctl status hello.service

In general:

Check status
sudo systemctl status hello.service

Start service
sudo systemctl start hello.service

Stop service
sudo systemctl stop hello.service

Check service's log
sudo journalctl -f -u hello.service