# Deploy Commands

## Windows PowerShell (One-Line Install)

```powershell
irm https://raw.githubusercontent.com/vtion001/libertad-capital/main/install.ps1 | iex
```

## Update (Windows)

```powershell
irm https://raw.githubusercontent.com/vtion001/libertad-capital/main/update.ps1 | iex
```

## Manual Setup (macOS / Linux / Windows Git Bash)

```bash
git clone https://github.com/vtion001/liberty-funding.git
cd libertad-capital

python3 -m venv venv
source venv/bin/activate          # macOS/Linux
# venv\Scripts\activate           # Windows CMD

pip install -r requirements.txt

cp .env.example .env
# Edit .env with your API keys

./run.sh                          # macOS/Linux
# run.bat                          # Windows
```

## For Windows (without Git)

1. Download ZIP from: https://github.com/vtion001/liberty-funding
2. Extract to `C:\libertad-capital`
3. Double-click `install.bat` to set up Python environment
4. Edit `.env` with your API keys
5. Run `run.bat`
