---
name: magister
description: "Fetch schedule, grades, and infractions from Magister portal"
homepage: https://magister.net
---

# Obtain token

```bash
node "$(dirname "$0")/obtain_token.mjs"
```

Prints `{token}` to stdout. All further API steps use `web_fetch` with header `Authorization: Bearer {token}`.

> **Fallback:** If `web_fetch` returns 401, your implementation likely does not support custom headers.
> Use `curl` instead:
> ```bash
> curl -s -H "Authorization: Bearer {token}" {url}
> ```

Times are UTC.

# Get parent ID

```
web_fetch GET https://{MAGISTER_HOST}/api/account
```

Use `Persoon.Id` (numeric integer) as `{parent_id}`.

# List children

```
web_fetch GET https://{MAGISTER_HOST}/api/ouders/{parent_id}/kinderen
```

Lowercase JSON, per `items[]`:
- `roepnaam`
- `achternaam`
- `id` — `{child_id}` (schedule/infractions)
- `actieveAanmeldingen[0].links.self.href` — `{aanmelding_id}` (grades)

# Schedule

```
web_fetch GET https://{MAGISTER_HOST}/api/personen/{child_id}/afspraken?van=YYYY-MM-DD&tot=YYYY-MM-DD
```

PascalCase JSON, per `Items[]` ignore `Status=5` (cancelled):
- `Start`
- `Einde`
- `Omschrijving`
- `Lokatie`
- `Vakken[0].Naam`
- `Docenten[0].Naam`

# Infractions

```
web_fetch GET https://{MAGISTER_HOST}/api/personen/{child_id}/absenties?van=YYYY-MM-DD&tot=YYYY-MM-DD
```

PascalCase JSON, per `Items[]`:
- `Omschrijving` (type)
- `Code` (`"TR"/"HV"/"AT"`)
- `Geoorloofd` (excused)
- `Afspraak.Omschrijving`

# Grades

```
web_fetch GET https://{MAGISTER_HOST}/api/aanmeldingen/{aanmelding_id}/cijfers?top=50
```

Lowercase JSON, per `items[]`:
- `waarde` (grade string)
- `isVoldoende`
- `teltMee`
- `kolom.omschrijving`
- `kolom.weegfactor`
- `kolom.type`: `"cijfer"/"gemiddelde"/"tekortpunten"/"som"`
