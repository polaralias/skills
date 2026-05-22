# Test prompts

## 1. Create shared defaults in the preferred location
Prompt: "Set up Polaralias skills with my shared brand defaults and put them where most agents can read them."
Expected:
- the skill prefers `~/.agents/config/polaralias-skills/`
- `profile.md` and `variables.yaml` are drafted and then written there
- the response explains that installed skill folders were not edited

## 2. Fall back when the preferred path is unsuitable
Prompt: "Set up my shared Polaralias skill profile, but the `.agents` config path is unavailable here."
Expected:
- the skill explains the failure or unsuitability
- it falls back to `~/.config/polaralias-skills/`
- it reports which path was used

## 3. Update existing values instead of recreating from scratch
Prompt: "Refresh my Polaralias shared branding defaults with a new font and logo path."
Expected:
- existing files are inspected first
- only the changed values are updated
- the response summarizes what changed

## 4. Leave blanks when the user only knows part of the profile
Prompt: "Set up the shared config but I only know the brand name, accent colour, and footer text for now."
Expected:
- the files are still created
- unknown values remain blank or commented in the template
- the response notes that downstream skills will use packaged defaults for missing keys
