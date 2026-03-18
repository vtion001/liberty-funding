# Google Sheet Structure

## Required Sheet: "suppression register"

Create a Google Sheet tab named exactly `suppression register`.

## Column Headers (Row 1)

Add these exact headers in row 1, column A through K:

| Col | Header |
|-----|--------|
| A | DATE ADDED |
| B | PLATFORM SOURCE |
| C | CONTACT ID |
| D | EMAIL |
| E | SUPPRESSION SOURCE |
| F | REASON |
| G | RULE ID |
| H | SUPPRESSION TAG |
| I | PERMANENT REQUIRED |
| J | DND REQUIRED |
| K | WORKFLOW REMOVAL REQUIRED |

## Share the Sheet

1. Click **Share** on the Google Sheet
2. Add this email as **Editor**:
   ```
   libertad-capital-funding@email-marketing-490517.iam.gserviceaccount.com
   ```
3. Copy the **Spreadsheet ID** from the URL:
   ```
   https://docs.google.com/spreadsheets/d/[SPREADSHEET_ID_HERE]/edit
   ```
4. Paste it into `.env` as:
   ```
   SPREADSHEET_ID=your_spreadsheet_id_here
   ```

## Sheet ID

The current spreadsheet ID configured:
```
1qktMN2WAXSXtDNn_UVWe8quJ9ysBjGUDIpWxl45efIA
```
