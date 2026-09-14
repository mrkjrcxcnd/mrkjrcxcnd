# Repository-owned profile

The design follows the supplied terminal screenshot. The original ASCII portrait
and block lettering were recovered from the old profile configuration. There are
no remote fonts, widget images, package dependencies, or GitASCII calls.

- Edit `profile/config.json` for biography, technologies, portrait, and lettering.
- Run `python3 scripts/generate_profile.py` to rebuild both SVGs offline.
- Run `GH_TOKEN=… python3 scripts/generate_profile.py --refresh` to fetch current
  public metrics and the contribution calendar from GitHub's GraphQL API. Never
  commit your token. GitHub Actions supplies its built-in token automatically.
- `profile/github-data.json` is the last successful API snapshot. A failed API
  request exits without replacing it or publishing partial artwork.
- Updates run daily, or manually through **Actions → Update profile artwork →
  Run workflow**, and use the GitHub Actions bot identity.

`assets/profile.svg` matches the desktop composition. `profile-mobile.svg` stacks
its panels and splits the same calendar into two rows. The README's `<picture>`
selects the mobile version on narrow screens. Its text alternative and expandable
biography keep essential information accessible. The technology strip moves
within its frame and respects reduced-motion settings.

The calendar uses GitHub's actual daily counts with the screenshot's dark green palette, never invented activity.
Current streak allows the last calendar day to be unfinished; longest streak is
limited to the displayed period. Stars and forks total the public owned repos.
Stats reflect the last refresh; GitHub may need time to recalculate contributions
following the branch history rewrite.
