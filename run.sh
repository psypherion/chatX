#!/bin/bash

# Get the directory of the current script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Create the chatX script
CHATX_SCRIPT="$SCRIPT_DIR/chatX"
echo "#!/bin/bash" > "$CHATX_SCRIPT"
echo "SCRIPT_DIR=\"$SCRIPT_DIR\"" >> "$CHATX_SCRIPT"
echo "cd \"\$SCRIPT_DIR\"" >> "$CHATX_SCRIPT"
echo "bash \"\$SCRIPT_DIR/bash_server.sh\"" >> "$CHATX_SCRIPT"

# Make the chatX script executable
chmod +x "$CHATX_SCRIPT"

# Copy the chatX script to /usr/local/bin
sudo cp "$CHATX_SCRIPT" /usr/local/bin/chatX

echo "chatX command installed. You can now run 'chatX' from anywhere to start the server."
