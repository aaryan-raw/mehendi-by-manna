# Mehndi by Manna: private demo guide (for the developer)

*For your preparation only. It is not a message to the artist and nothing in it has been sent to anyone.*

**The one sentence to use whenever booking comes up**

> "The booking interface is currently a demonstration. It does not check actual availability, send an enquiry, or reserve an appointment."

---

## 1. What the website contains
A single scrolling page, top to bottom:
1. **Navigation**: logo, section links, and a "Booking demo" button (a menu button on phones).
2. **Hero**: headline "A little art. A lasting impression." (creative copy written for this concept, **not** her tagline), a short intro, and an arched photo.
3. **Intro strip**: Bridal Henna · Non-Bridal Henna · Trivandrum · Kochi · Customisable Designs, marked "As listed on the Instagram profile".
4. **About**: what the profile says she offers. There is deliberately **no personal story, name or biography**.
5. **Gallery**: five of her photographs plus a "More work on Instagram" tile. Tap a photo to open the larger view.
6. **Services**: Bridal Henna and Non-Bridal Henna cards.
7. **Pricing & enquiries**: no prices; "Ask about pricing" with a link to her Instagram.
8. **Booking Demo**: a simulated five-step booking experience.
9. **FAQ**: eight questions; unconfirmed answers carry a "To be confirmed" tag.
10. **Contact** and **footer**: Instagram link and the line "Independent concept demonstration · Not an official website".

## 2. Run it locally
```
unzip mehndi-by-manna.zip && cd mehndi-by-manna
npm ci                 # installs exactly what package-lock.json says
npm run dev            # http://localhost:4321  (live editing)
# or the production-style version:
npm run build && npm run preview     # http://localhost:4321
```
Requires Node 18.20.8, 20.3 or newer, or 22+ (Astro's declared range; tested here with Node 22.22.2) and npm 9.6.5+. The page is marked `noindex`; nothing is online.

## 3. A suggested walk-through (about 5 minutes)
1. **Landing.** Read the headline and intro. Note the "Booking demo" button in the nav.
2. **Explore the collection** button, then scroll the gallery.
3. **Gallery and lightbox.** Click any photo: it opens full-screen. Use the **‹ ›** buttons or the **← →** keys to move between the five photos; **Esc** or **✕** closes it and returns you to where you were. On a phone, tap the buttons (swiping is built in but has **not** been tested on a real device).
4. **Services.** Click "Try the booking demo" on a card: it jumps to the demo with that service already selected.
5. **Pricing & enquiries.** Point out that no prices are shown, and that the Instagram link is the only contact route.
6. **Booking demo** (section 4 below).
7. **FAQ.** Open "Where is the artist available?" and "How much does it cost?" to show the "To be confirmed" tags.
8. **Contact and footer.** Confirm the Instagram link and the concept-demo line.

## 4. Demonstrating the booking flow honestly
Say first: *"This is a demonstration. It does not check actual availability, send an enquiry, or reserve an appointment."*
The page itself says the same in a dark banner on **every** step.
1. **Service.** "Guest Henna" is preselected as an example, labelled "Illustrative option, for this demonstration only". Try Bridal or Non-Bridal.
2. **Date.** Scroll the date strip or use the calendar (arrow keys work). Dates are **fixed sample data** (19 Oct to 31 Dec 2026): some show "few" or "full" to illustrate how it could look. Struck-through dates cannot be picked.
3. **Time.** Pick a sample slot. If you later change the date, the time is cleared (on purpose).
4. **Details.** Use **made-up** details. Try leaving fields empty to show the error messages.
5. **Review.** Use "Edit details" or "Edit service/date/time" to show you can go back.
6. **Receipt.** It reads "Demo request completed … No request was sent to the artist, and no appointment has been booked or confirmed." The reference starts with `DEMO-` and is not a booking number.
7. **Start again and clear details** resets everything to the example state.

**Do not:** type real personal or client details; call the `DEMO-` reference a booking; say availability is real; show the receipt as proof that something was sent.
Nothing is sent or stored: the demo makes no network request, sets no cookie and uses no browser storage (checked by the automated tests).

## 5. What is verified and what is not
**Taken from the Instagram profile text and the supplied images** (these are the profile's own claims, not independently verified): the brand name and handle; "Bridal Henna | Non-Bridal henna services"; "Trivandrum | Kochi"; "Affordable and Customizable Designs"; "DM for bookings"; the five photographs and the logo.

**Not confirmed by anyone** (see `OWNER_APPROVAL_CHECKLIST.md`): the correct name and its spelling; permission and rights for the photos and logo; what the two city names mean; prices; travel, deposit, cancellation and duration policies; real availability; any phone, email or WhatsApp number; whether she wants a booking feature at all; her approval of the design and wording.

## 6. What to inspect yourself
**Laptop:** open in **Safari and Firefox** as well as Chrome (only Chromium has been tested); resize the window narrow and wide; zoom to 200%; press **Tab** through the whole page and check you can always see where focus is; open every FAQ item; run the whole demo with the keyboard only.
**Phone:** to look on your phone, put it on the **same Wi-Fi** and run `npm run dev -- --host` (or `npm run preview -- --host`); the terminal prints a "Network" address to open on the phone. This shares the site only on your local network, only while the command runs; stop it with Ctrl+C. (The commands were tested to start; a phone connection could not be tested here and may depend on your firewall.) Check: the menu button, the gallery and lightbox with your thumb (including swiping), typing in the demo form (is the keyboard covering anything?), portrait and landscape.
**If you can:** try a screen reader (VoiceOver, TalkBack or NVDA) on the gallery and the demo. This has **not** been done.

## 7. Before presenting it as a *proposed business website*
- Be clear that it is **unsolicited**, built from her public Instagram material, and **not approved or live**. Don't present it as launched or official.
- Have the open questions in `OWNER_APPROVAL_CHECKLIST.md` ready, especially permission for the photos and logo, her name, and how she wants people to enquire.
- Keep the site private (no hosting, no public link) until she agrees. Nothing here is legal advice; whether using her Instagram photos in a private mock-up needs her consent first is your call to make.
- Decide beforehand what you will do if she says no, wants changes, or wants the photos removed.

## 8. If she asks whether bookings currently work
Suggested talking points (your preparation, not a script to send):
- "Not yet. The booking interface is currently a demonstration. It does not check actual availability, send an enquiry, or reserve an appointment."
- "Today, the way to enquire is the Instagram DM link; that is the only real contact route on the site."
- "A real booking or enquiry feature would be separate work, and would depend on what you want: how people should contact you, your working days and hours, whether you approve each request, and whether you want deposits. Nothing like that is built."
