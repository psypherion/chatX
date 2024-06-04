#!/bin/bash

# Define the credentials file
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CREDENTIALS_FILE="$SCRIPT_DIR/credentials.json"

# Check if credentials.json exists
if [ ! -f "$CREDENTIALS_FILE" ]; then
    # Ask the user for the ngrok API key
    read -p "Enter your ngrok API key: " API_KEY
    
    # Create the credentials.json file with the API key
    echo "{\"api_key\": \"$API_KEY\"}" > "$CREDENTIALS_FILE"
fi

# Function to check and fix credentials
check_credentials() {
    python3 "$SCRIPT_DIR/credchecker.py" "$CREDENTIALS_FILE"
}

# Check and fix credentials before proceeding
check_credentials

# Install ngrok using snap if not already installed
if ! command -v ngrok &> /dev/null; then
    echo "Installing ngrok..."
    sudo snap install ngrok &> /dev/null
fi

# Run the Python script to get the ngrok auth token
python3 "$SCRIPT_DIR/auth.py" &> /dev/null

# Read the auth token from credentials.json
AUTH_TOKEN=$(python3 -c "import json; print(json.load(open('$CREDENTIALS_FILE'))['auth_token'])")

# Authenticate ngrok
ngrok authtoken $AUTH_TOKEN &> /dev/null

# Kill any process using port 8080
fuser -k 8080/tcp &> /dev/null

# Run the Python server script
python3 "$SCRIPT_DIR/chat_server.py" &> /dev/null &

# Run ngrok to expose the server and generate connection command
python3 "$SCRIPT_DIR/ngrok_setup.py" &> /dev/null

# Read the generated ngrok connection details and create the telnet command
NGROK_URL=$(cat "$SCRIPT_DIR/ngrok_url.txt")
HOST=$(echo $NGROK_URL | sed -n 1p)
PORT=$(echo $NGROK_URL | sed -n 2p)

# Create the telnet command
echo "telnet $HOST $PORT" > "$SCRIPT_DIR/command.txt"

echo "Server setup complete. Connection command saved to command.txt."

echo "Send this command to your desired user : "

cat "$SCRIPT_DIR/command.txt"


# Function to shut down ngrok and server
shutdown() {
    echo "Shutting down server and ngrok..."
    # Kill the ngrok process
    NGROK_PID=$(pgrep ngrok)
    if [ -n "$NGROK_PID" ]; then
        kill -9 $NGROK_PID &> /dev/null
    fi
    # Kill the chat server process
    SERVER_PID=$(pgrep -f chat_server.py)
    if [ -n "$SERVER_PID" ]; then
        kill -9 $SERVER_PID &> /dev/null
    fi
    # Run ngrok_setup.py to delete auth tokens
    python3 "$SCRIPT_DIR/ngrok_setup.py" &> /dev/null
    exit 0
}

# Trap INT and TERM signals to run the shutdown function
trap shutdown INT TERM

# Wait indefinitely to keep the script running
while :; do
    sleep 1
done
