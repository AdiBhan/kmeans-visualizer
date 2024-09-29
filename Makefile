# Define paths
CLIENT_DIR=client
SERVER_DIR=server

# Define commands
PIP=pip
PYTHON=python
NPM=npm

# Install all dependencies for frontend and backend
install: install-client install-server

# Install frontend dependencies
install-client:
	@echo "Installing frontend dependencies..."
	cd $(CLIENT_DIR) && $(NPM) install

# Install backend dependencies
install-server:
	@echo "Installing backend dependencies..."
	cd $(SERVER_DIR) && $(PIP) install -r requirements.txt

# Run both frontend and backend
run: run-client run-server

# Start the frontend (React app) on port 3000
run-client:
	@echo "Starting frontend on http://localhost:3000..."
	cd $(CLIENT_DIR) && $(NPM) run dev &

# Start the backend (Flask app)
run-server:
	@echo "Starting backend..."
	cd $(SERVER_DIR) && $(PYTHON) server.py

# Clean up generated files (optional)
clean:
	@echo "Cleaning up..."
	rm -rf $(CLIENT_DIR)/node_modules
