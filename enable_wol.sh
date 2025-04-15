#!/bin/bash

install_wakeonlan() {
    echo "Checking and installing wakeonlan and ethtool..."
    sudo apt update
    sudo apt install -y wakeonlan ethtool
}


install_wakeonlan

# Identify the network interface
INTERFACE=$(ip -o link show | grep "<BROADCAST,MULTICAST,UP,LOWER_UP>" | awk -F': ' '{print $2}' | awk '{print $1}' | xargs)

if [ -n "$INTERFACE" ]; then
    echo "Network interface identified: $INTERFACE"
    sudo ethtool -s "$INTERFACE" wol g

    WOL_STATUS=$(sudo ethtool "$INTERFACE" | grep "Wake-on:" | awk '{print $2}')
    if [ "$WOL_STATUS" == "g" ]; then
        echo "Wake-on-LAN successfully enabled on interface $INTERFACE"
    else
        echo "Failed to enable Wake-on-LAN on interface $INTERFACE. Current status: $WOL_STATUS"
    fi
else
    echo "No active network interface found."
fi

# Create the enable_wol.sh script
ENABLE_WOL_SCRIPT="/usr/local/bin/enable_wol.sh"
sudo tee "$ENABLE_WOL_SCRIPT" > /dev/null << 'EOF'
#!/bin/bash

INTERFACE=$(ip -o link show | grep "<BROADCAST,MULTICAST,UP,LOWER_UP>" | awk -F': ' '{print $2}' | awk '{print $1}' | xargs)

if [ -n "$INTERFACE" ]; then
    echo "Network interface identified: $INTERFACE"
    if ! command -v ethtool &> /dev/null; then
        echo "ethtool not found. Installing..."
        sudo apt-get update && sudo apt-get install -y ethtool
    fi
    sudo ethtool -s "$INTERFACE" wol g
    WOL_STATUS=$(sudo ethtool "$INTERFACE" | awk '/Wake-on:/ {print $2}' | tail -n1)
    if [ "$WOL_STATUS" == "g" ]; then
        echo "Wake-on-LAN successfully enabled on interface $INTERFACE"
    else
        echo "Failed to enable Wake-on-LAN on interface $INTERFACE. Current status: $WOL_STATUS"
    fi
else
    echo "No active network interface found!"
fi
EOF


sudo chmod +x "$ENABLE_WOL_SCRIPT"


SERVICE_FILE="/etc/systemd/system/enable_wol.service"
sudo tee "$SERVICE_FILE" > /dev/null << EOF
[Unit]
Description=Enable Wake-on-LAN on Raspberry Pi
After=network.target

[Service]
Type=oneshot
ExecStart=$ENABLE_WOL_SCRIPT

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable enable_wol.service
sudo systemctl start enable_wol.service