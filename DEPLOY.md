# Deploy Commands

## Windows PowerShell (One-Line Install)

Copy and paste this into PowerShell (as Administrator):

```powershell
irm https://raw.githubusercontent.com/YOUR_USERNAME/liberty-funding/main/install.ps1 | iex
```

## Manual Setup

1. Clone repository:
```bash
git clone https://github.com/YOUR_USERNAME/liberty-funding.git
cd liberty-funding
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/Scripts/activate  # Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure:
```bash
cp config/settings.example.py config/settings.py
# Edit settings.py with your credentials
```

5. Run:
```bash
python scripts/run.py
```

## For IRM to Work

1. Upload this project to GitHub
2. Replace `YOUR_USERNAME` in the URL above with your GitHub username
3. Make the install.ps1 script accessible via raw URL
