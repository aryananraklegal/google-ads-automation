# visuals/

Ad creative assets for this account. Organised by type.

```
visuals/
  brand/        ← logos, brand colours, product screenshots — source assets Addy uses in briefs
  generated/    ← AI-generated images (Higgsfield / Canva) ready for upload to Google Ads
  screenshots/  ← Transparency Centre research screenshots captured during creative sessions
```

## How Addy uses this folder

**Before creating a brief:**
Addy checks `brand/` for existing logos and screenshots to reference in the art direction notes.

**After generating images:**
Generated assets go into `generated/` with a naming convention:
`YYYY-MM-DD_[campaign-label]_[format]_[version].png`
Example: `2026-08-01_PMax-Students_landscape_v1.png`

**During Transparency Centre research:**
Browser screenshots of competitor ads go into `screenshots/` for session reference.
Named: `YYYY-MM-DD_[search-term].png`

## What goes to GitHub

This folder (structure + README) is committed.
The actual image files are gitignored — they stay local only.
Brand assets should be backed up separately (Google Drive / OneDrive).
