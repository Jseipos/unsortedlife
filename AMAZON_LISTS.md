# Amazon lists that feed the link page (intake, read in Chrome while signed in)

Rule: a product goes on the page only once it is on a "bought" list AND has a verdict note from Jess AND (ideally) an _a photo in photos/inbox. Wishlist items go on the gift lists as "wishes, not reviews" with a short note.

| Amazon list            | list id        | feeds page section / list          |
|------------------------|----------------|------------------------------------|
| Nova Reorders          | 2AHTI6YW8EU8Z  | puppy (bought, reorders)           |
| Puppy Must Haves       | 332KDGUE2O4RB  | puppy (bought)                     |
| House Things           | 32I6ZEPMTL4TE  | organization (bought)              |
| Unsorted Life          | 2LGSMI851HUT2  | gifts / my-list (wishes)           |
| Ayla Christmas Wishlist| 3NRAT6JHGF96U  | gifts / her-list (wishes)          |
| #FoundItOnAmazon       | QJAOOB6X3XEF   | not on page (women's clothes)      |

Old lists (Earth Friendly Goods default, Presents, Xmas lists, etc.) are NOT intake. Jess moves things into the lists above by hand when they have a home.

Open a list: https://www.amazon.com/hz/wishlist/ls/<list id>
Dump items (scroll to bottom first), one per line "ASIN | name":
  Array.from(document.querySelectorAll('li[data-itemid]')).map(li=>{const a=li.querySelector('a[id^=itemName_]');const m=(a?a.getAttribute('href'):'').match(/\/dp\/([A-Z0-9]{10})/);return (m?m[1]:'?')+' | '+(a?a.textContent.trim().slice(0,60):'')}).join('\n')
Then: python3 check_lists.py <dump.txt>   -> prints ASINs not yet in products.json

## Photos for wish-list items
If Jess photographs one in a store, name the file with the card's short name plus _a, e.g. "roller skate shoes_a.jpg", "atari_a.HEIC". The build then swaps the placeholder tile for the photo. Short names in use: Pots and pans, Robot mower, Sonic toothbrush, Flat plug extension, Grüns kids gummies, Roller skate shoes, Atari, Unicorn robe, Unicorn blanket, Jumbo squishies, Food squishies, Silicone squishies, Squishy making kit, Pottery wheel, Weaving loom, Rock painting kit, Nat Geo rock kit, Science kit, Sentence Search, Kid-safe knives, Cutting gloves, Bath bombs, Glitter balm, Mom and daughter journal, How to draw animals, Junie B. Jones, Descendants novel, Baggy jeans, Flare jeans, Guess jeans, Cat gaming chair
