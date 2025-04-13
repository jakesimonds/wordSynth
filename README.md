# word synth!


## Running the Application

### Step 1: Download the Model
First, download the required model by running the provided script:

```bash
./pull_model.sh
```

This will download the Llama-3.2-1B-Instruct model to the `models` directory if it doesn't already exist.

### Step 2: Start the Backend Server
Activate the virtual environment and start the backend server:

```bash
# Activate the virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Navigate to the backend directory
cd backend

# Start the backend server
python -m uvicorn main:app --reload
```

The backend server will be available at http://localhost:8000.

### Step 3: Start the Frontend Server
In a new terminal window, navigate to the frontend directory and start the development server:

```bash
# Navigate to the frontend directory
cd frontend

# Install dependencies (if you haven't already)
npm install

# Start the frontend development server
npm run dev
```

The frontend will be available at http://localhost:5173.

### Step 4: Use the Application
Open your browser and navigate to http://localhost:5173 to use WordSynth.

### Stopping the Servers
To stop either server, press `Ctrl+C` in the respective terminal window.


debug cheat sheet:
sudo journalctl -u synth.service -n 500 --no-pager
