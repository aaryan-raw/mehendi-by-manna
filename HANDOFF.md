# Mehndi by Manna: launch-readiness and owner handoff

**Status: private concept demonstration. Not approved by the artist, not deployed, not for public launch.**
Last verified: 16 October 2026 (Stage 5), Node v22.22.2, Chromium (Playwright). Nothing in this project has been published, sent or submitted.
Companion documents: `OWNER_APPROVAL_CHECKLIST.md` (what the artist must confirm) and `DEMO_GUIDE.md` (how to run and present the demo honestly).

## 1. Current status

**What the site is.** A one-page portfolio website (Astro 5 + one React island + custom CSS) for the Instagram profile
https://www.instagram.com/mehndi_by_manna_/ . Sections: navigation, hero, intro strip, About, gallery with lightbox,
two services, pricing/enquiry, **Booking Demo**, FAQ, contact, footer. It uses five supplied photographs and the supplied logo.

**What is real:** the page, gallery, lightbox, FAQ, navigation, and the link to the Instagram profile (the only contact route).

**What is a demonstration only:**
- The **Booking Demo** is a frontend simulation. It does **not** create appointments, send enquiries or messages, check real
  availability, take payment, or keep visitor information. All dates, time slots and "availability" are fixed sample data
  (19 Oct to 31 Dec 2026), labelled as such. The receipt says: "This is a website demonstration. No request was sent to the artist,
  and no appointment has been booked or confirmed." Its reference numbers are prefixed `DEMO-`.
- "Guest Henna" exists only inside the demo, labelled as an illustrative option. It is not presented as a service.
- There is **no** backend, form handler, database, login, analytics, cookie, payment or notification code anywhere in the project.

## 2. Run, build, test

Requires Node 18.20.8, 20.3+ or 22+ and npm 9.6.5+ (Astro's declared range).
```
npm ci                 # install exactly what package-lock.json specifies
npm run dev            # http://localhost:4321  (live editing)
npm run build          # static site in dist/
npm run preview        # serve dist/ at http://localhost:4321
```
Optional social-preview build (only once a real domain exists): `SITE_URL=https://<real-domain> npm run build`

QA scripts (not part of the website, not shipped to visitors). Prerequisites: Python 3, `pip install playwright`, `playwright install chromium` (standard Playwright setup; Chromium only):
```
npm run build && python3 -m http.server 4399 -d dist &      # serve the build
python3 qa/qa_suite.py          # layout, navigation, lightbox, booking flow, privacy, accessibility structure
python3 qa/content_audit.py     # claims/wording scan, links, metadata, build scans, SITE_URL build
python3 qa/journey_check.py     # first-time-visitor journey at 5 viewports + booking-demo safety screens
npm install --no-save axe-core && python3 qa/axe_check.py   # axe-core scan of 17 page states (axe is not a project dependency)
```

## 3. Before launch: owner decisions (nothing below has been decided; suggestions need approval)

| # | Decision / confirmation | State on the site today | Suggestion (needs approval) |
|---|---|---|---|
| 1 | **Public name.** The site never states the artist's personal name. The profile display name and the linked handle are spelled differently (see Stage 1 notes), so the correct spelling is unresolved. | Brand name "Mehndi by Manna" only | Ask the artist how she wants to be named, if at all |
| 2 | **Permission for photographs and logo.** The photos were saved from Instagram with a third-party downloader and carry the handle as a watermark. The logo was a JPG; the site uses a background-removed PNG derived from it. | Used for this private demo only | Get written permission; ask for original photo files and a vector/transparent logo |
| 3 | **Location wording.** The profile says "Trivandrum \| Kochi". It is unknown whether this means based in, serves, or travels to. | Shown only as "as listed on the Instagram profile" (intro strip, FAQ, footer); never as a service area or studio address | Artist chooses wording, e.g. "Based in …" / "Available in …" |
| 4 | **Services.** The profile lists bridal and non-bridal henna. | Two service cards with neutral descriptions | Artist confirms, adds or removes services and may supply short descriptions |
| 5 | **Pricing.** No prices are known. | No prices; heading "Ask about pricing."; FAQ marks pricing as unconfirmed | Artist chooses: keep DM-for-prices, show "from" prices, or full price list |
| 6 | **Genuine enquiry method.** The profile says "DM for bookings". | Instagram DM link only; no phone, email or WhatsApp | Choose one or more: Instagram DM / WhatsApp / enquiry form. Any real enquiry feature needs verified details and is a **separate, explicitly approved stage** |
| 7 | **Contact details to publish.** None verified. | None published | Artist supplies exactly what she wants public |
| 8 | **Approval of design and copy.** Headlines and About copy were written for this concept, not by the artist. "Affordable" and "customisable" are the profile's own claims. | Marked as "as described on the Instagram profile" where used as claims | Artist reviews all text; replace creative copy with her own voice if preferred |
| 9 | **Booking Demo.** Keep as a visual idea, replace with a real enquiry route, or remove. | Fully labelled demo; sample dates end 31 Dec 2026 | If kept for any public use, update the sample window in `src/components/Booking.jsx` (`START`/`END`) |
| 10 | **Policies.** Travel, deposit, cancellation, duration, availability are all unknown. | FAQ says "To be confirmed" | Artist supplies answers, or remove those questions |

**Profile claims vs verified facts.** Everything about the business on the site comes from the Instagram profile text or the
supplied images. None of it has been independently verified: bridal and non-bridal services, "Trivandrum | Kochi",
"Affordable and Customizable Designs", "DM for bookings".

**Concept-demo labelling to revisit at launch** (only after approval): `<title>`, meta description and Open Graph text and the
footer line in `src/pages/index.astro`; the Booking Demo banner and receipt in `src/components/Booking.jsx`.

**Keeping the preview private.** The page has `<meta name="robots" content="noindex, nofollow, noarchive, nosnippet">` and `public/robots.txt`
disallows everything. Note that a `Disallow` rule stops crawlers reading the page's noindex tag; for a link shared with one person,
the safest protection is host-level password protection or an `X-Robots-Tag: noindex` response header. **Do not remove `noindex`
until the artist approves a public launch.**

**Domain and social preview.** No domain exists, so no `og:image`/`og:url` and no canonical link are emitted (a relative URL would not
work for link previews). After a real domain exists, build with `SITE_URL=https://<domain>`; the build then emits absolute
`og:image` and `og:url` (tested with a placeholder domain). `public/img/og.jpg` (1200x630, logo plus one photo) needs the artist's approval.

**Launch steps (not yet done):** confirm items 1 to 10, get written permission, replace/approve copy, set `SITE_URL`, decide on
`noindex`, build, deploy to the chosen host, re-run the QA scripts against the deployed URL.

## 4. Technical details

- **Stack:** Astro 5.18, React 18.3 (only for the booking island, loaded when the section nears the viewport), custom CSS with design tokens,
  self-hosted Fontsource fonts (Cormorant Garamond, Jost). Dependencies: `astro`, `@astrojs/react`, `react`, `react-dom`, two Fontsource packages.
- **Directories:** `src/pages/index.astro` (page, lightbox script), `src/components/Booking.jsx` (demo), `src/components/Pic.astro` (responsive image),
  `src/styles/global.css` (tokens + styles), `src/data/images.json` (image sizes), `public/img/` (WebP derivatives, logo, og.jpg), `qa/` (tests).
  Original photographs are **not** in this project; they remain only in the supplied ZIP, which was never modified.
- **Performance facts measured:** layout shift 0 at all five viewports (3 runs each) after preloading the three above-the-fold font files; first paint
  loads 3 font files, none external; React and booking code are not downloaded until the booking section nears the viewport.

### Actual results (final build, 16 Oct 2026)
| Check | Result |
|---|---|
| `qa/qa_suite.py` (Chromium; 375, 430, 768, 1280, 1440 px) | **156 passed, 0 failed** |
| `qa/content_audit.py` | **36 passed, 0 failed** |
| `qa/journey_check.py` (landing, CTA anchors, gallery proportions, FAQ, footer, and all six booking screens: demo banner, no sent/booked claims, no payment fields, reset) | **65 passed, 0 failed** |
| `qa/axe_check.py` (axe-core, WCAG 2.0/2.1/2.2 A and AA + best practice, 17 states: page, mobile menu, lightbox, FAQ, every booking step incl. errors and receipt, at 375 and 1280 px) | **0 violations**; items axe cannot decide: icon-only buttons (visible glyph vs `aria-label`) and contrast over image/overlay backgrounds |
| Console errors, failed requests | none; about 240 requests per full run (239 to 242 observed), none non-GET, none to external hosts (6 to 9 browser-cancelled image loads from rapid lightbox flipping are expected) |
| Horizontal overflow | none at the five viewports, including with every FAQ item open |
| Booking demo | all 41 checks at 1280 px and 42 at 375 px pass: service change, date strip and calendar (mouse and keyboard), unavailable dates/slots, time cleared on date change, validation, review/edit, receipt wording, start again clears everything, no storage or network |

### Known limitations and unverified checks
- **Browsers:** only Chromium was available. Firefox, Safari/iOS and older browsers are **unverified**. The CSS uses modern features (`:has()`, `<dialog>`, `dvh`, `aspect-ratio`) that should work in current browsers, but this was not tested.
- **Assistive technology:** no screen reader (NVDA, JAWS, VoiceOver, TalkBack) and no voice-control test was possible: **unverified**. Automated tools find only part of WCAG issues; full compliance is **not** claimed.
- **Real devices:** no physical phone or tablet; touch behaviour including lightbox swipe is **unverified** (emulated viewports only).
- **Instagram link:** its URL and attributes (`target="_blank"`, `rel="noopener noreferrer"`) were checked locally. The profile was not visited, so that it loads is **unverified**.
- `npm run dev` and `npm run preview` were started from a clean `npm ci` install of the final archive and served the page (HTTP 200; no errors or warnings in the dev log). The QA suites run against the static build. Builds from the archive are byte-identical to the working build except for Astro's random per-build island id in `index.html`.
- **Manual tests still outstanding** (none of these were possible here): screen reader and voice-control testing; real phone and tablet testing (touch, on-screen keyboard, lightbox swipe); Firefox, Safari and iOS Safari; browser zoom to 200 to 400% (reflow), text-spacing overrides, and forced-colours/high-contrast mode; slow-network behaviour. Chromium-only results are **not** proof of cross-browser compatibility, and automated checks passing is **not** proof of WCAG compliance.
- Booking demo needs JavaScript; without it the demo is inert (the rest of the site works).
- The gallery has only five authentic images, so each appears in more than one place.
- Sample dates in the demo are fixed and will look dated after 31 Dec 2026.

## 5. Privacy and bookings
The Booking Demo keeps everything in the visitor's browser memory only and discards it on "Start again" or page reload. It makes no network request when used,
sets no cookie, and writes nothing to localStorage, sessionStorage or IndexedDB. It does not create appointments, send enquiries or messages,
check live availability, or collect payment details. The form asks only for a made-up name or nickname, an occasion, a guest count and optional notes, with an on-screen
warning not to enter sensitive information. The site loads no analytics, trackers, third-party scripts or web fonts from other servers.

## 6. Files changed or added in this stage
| File | Change and reason |
|---|---|
| `src/pages/index.astro` | Copy accuracy: location attributed to the profile; removed unsupported claims ("quotes available", "duration depends on the design", "best way", "she/her", "show the artist's work"); pricing heading to "Ask about pricing."; consistent capitalisation and Instagram CTA labels; accessible names for external links and the Instagram tile; developer note moved out of shipped HTML; font preloads (layout shift 0) |
| `src/components/Booking.jsx` | Accessible names for date chips (Label in Name); valid review `<dl>`; removed `aria-label` from non-semantic `div`s; consistent receipt CTA |
| `src/styles/global.css` | Intro-strip attribution style; review-list styling to match the corrected markup |
| `package.json` | Removed the `check` script (it needed `@astrojs/check`/TypeScript, which are not dependencies, and would have failed) |
| `qa/qa_suite.py` | Creates its own `qa/shots/` folder; selectors updated to stable `data-k` attributes and scoped calendar cells |
| `qa/content_audit.py` (new) | Claims/wording scan, link and metadata checks, build-output scans, `SITE_URL` build test |
| `qa/axe_check.py` (new) | axe-core scan across 17 page states |
| `README.md`, `HANDOFF.md` (new) | Documentation |
| Unchanged | `astro.config.mjs`, `package-lock.json`, `public/robots.txt`, images, `Pic.astro`, `qa/contrast.js` |

## 7. Stage 5 changes (final demo and delivery)
| File | Change and reason |
|---|---|
| `src/styles/global.css` | **Bug fix:** the FAQ column had no side gutters. On phones and tablets the text ran flush to the screen edge and opening an item (its "+" rotates) made the page scroll sideways by 10 px. It now uses the same gutters as every other section. Earlier overflow checks only ran with the FAQ closed. |
| `qa/journey_check.py` (new) | Visitor-journey and booking-demo safety checks that caught the FAQ bug; they run every FAQ open, every booking screen, and check for payment fields and "sent/booked" claims |
| `OWNER_APPROVAL_CHECKLIST.md` (new) | Checklist of owner decisions and permissions before launch |
| `DEMO_GUIDE.md` (new) | Developer's guide to running and presenting the demo honestly |
| `README.md`, `HANDOFF.md` | Updated for the Stage 5 documents, QA prerequisites, Node range and results |
| Unchanged | `package.json`, `package-lock.json`, `astro.config.mjs`, `public/` (including `robots.txt` and all images), `src/pages/index.astro`, `src/components/*` |
