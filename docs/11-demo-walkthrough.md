# Demo walkthrough

*Last updated 5 November 2026. A direct walkthrough of the app from start to finish, for a demo video. It takes about 3 minutes at a natural pace.*

## The story in one line

A small business's website stops AI agents from helping its customers, and Legible fixes that without the owner rebuilding anything.

Each step causes the next, so you never need to jump around. The **Next** card at the bottom of the sidebar points at every step except the last, so you can follow it on camera.

| | What happens | What it proves |
|---|---|---|
| 1 | Agents try the website and mostly fail | The problem is real |
| 2 | Each failure becomes a plain question for the owner | The owner only supplies what's missing |
| 3 | The owner confirms, and a page goes live | Nothing goes public without them |
| 4 | The same customers try again, and all succeed | It worked |
| 5 | The owner adds one line to their site, and agents arrive | That's all it takes to be found |
| 6 | The owner handles a booking and a question | Business comes in through it |
| 7 | The owner changes a price in plain words | It stays accurate without effort |

## Before you record

```bash
uv run python scripts/start.py --demo
```

Open `http://127.0.0.1:8300`, and press **Start over** in the sidebar if you've used it before. Use a browser window around 1280 by 800, and close other tabs.

To get back to the first screen at any point, press the Legible logo or **Add a website** in the sidebar. In the demo copy, adding a website starts a new take and replaces the current one.

Pause after each action. The numbers and traces animate, and they're the most persuasive part of the video.

## The walkthrough

### 1. The problem (20 seconds)

**On screen:** the empty Websites screen, with Sunrise Auto Detailers' address filled in.

**Say:** "This is Sunrise Auto Detailers, a mobile car detailing business. Their prices are in an image and most of their rules aren't written down. A person can pick up the phone. An AI agent shopping for a customer just gets stuck. Legible starts with their website address."

**Do:** press the arrow.

### 2. Legible reads the site (30 seconds)

**On screen:** pages being read, prices lifted from images, facts appearing, then 4 customer agents working.

**Say:** "It reads the site, including the prices in the images, and builds a fact sheet. Then it tests the site the way customers will: four agents each ask a real customer's question, using only this website."

**Wait for:** "1 of 4 got a real answer from your website."

**Do:** press **Answer 4 questions** in the Next card.

### 3. What stopped them (30 seconds)

**On screen:** Simulations, with each customer's question, its answer and the circled point where it gave up.

**Say:** "Only one of four got an answer. This customer wants a total under $400, and the site never states tax, travel or Saturday fees. Every failure becomes one plain question for the owner. They don't fill in a form, they just answer what's actually stopping customers."

**Do:** click the suggested answer for each of the 4 questions and send it. Do the first one slowly, so viewers see the answer turn into structured facts.

**Then:** press **Confirm 54 facts** in the Next card.

### 4. The owner stays in control (20 seconds)

**On screen:** Resource, with everything marked "Not public yet" until confirmed.

**Say:** "Here's everything Legible knows. None of it is public yet. Only the owner can publish it, and any line can be fixed first."

**Do:** press **Confirm and publish**.

**On screen:** "Your page is live."

**Say:** "That's a page built for agents: prices they can read, quotes they can work out, and requests they can send."

**Do:** press **Test it again**, then **Run the check again**.

### 5. It worked (20 seconds)

**On screen:** the same customers run again, then the two scores side by side.

**Say:** "Same customers, now using the Legible page. Four of four. The customer with the $400 budget now learns that Saturday comes to $422.38 and a weekday to $395.22, so a weekday fits."

**Do:** press **Put your link on your website** in the Next card.

### 6. Agents find it (25 seconds)

**On screen:** Websites, with the one line to paste.

**Say:** "The owner doesn't rebuild their website. They add this one line, and any agent reading the site can find the page."

**Do:** press **Check it's on your site**, then go to **Inbox**.

**On screen:** the counts climbing as agents arrive.

**Say:** "This is a sample week of agents using the page. The owner can see what they read and what they quoted, and where they hit a dead end. Three asked for ceramic coating, which Sunrise doesn't offer, and that's demand this owner could never see before."

### 7. Business comes in (25 seconds)

**Do:** press **Reply to 2 booking requests** in the Next card.

**On screen:** the request with its bill, $297.63.

**Say:** "An agent has sent a booking for its customer, with the price the page worked out, tax and Saturday fee included. One click to accept, and the agent sees the reply."

**Do:** press **Accept booking**. The list also shows the muddy F-250 from the test customers, already accepted at $628.76, and a request where the owner suggested another time. Then press **Answer 2 agent questions** in the Next card.

**Say:** "Another agent asked something the page didn't cover. The owner answers once, and it goes on the page for every agent after that."

**Do:** click "We don't detail golf carts." and send it.

### 8. It stays accurate (20 seconds)

**Do:** go to **Resource**, click the hint **Class A of the Skiff is now $70**, and send it.

**On screen:** "The Skiff, Class A, goes from $69 to $70".

**Say:** "When something changes, the owner just says so. Legible works out the exact change and waits for a yes."

**Do:** press **Confirm and publish**, then **What agents see**.

**Say:** "Every agent gets the new price straight away. That's Legible: any small business, readable to any AI agent, in the owner's own words."

## Say this plainly

- **It's sample data.** The demo copy is scripted and sped up, and the sidebar says so. Say so in the video or its description. You can truthfully add that the same flow runs for real with `scripts/start.py`.
- **Real numbers:** if you quote the benchmark, 3 of 7 versus 7 of 7, use the wording and limits in [the README](../README.md#the-result). It used a stand-in agent, not Muse or any other real one.

## What's real and what's scripted in the demo

| Part | In the demo |
|---|---|
| Reading the site, fact sheet, questions, test customers | Scripted, with no AI calls |
| Placing the link | Scripted: the demo site never really carries it |
| Agents arriving | Invented customers, sent as real requests to the real public page, and dated across the last 4 days. Opening Inbox or Bookings starts them if you skip the link step |
| Booking replies already there | 2 of the 4 sample bookings arrive already answered, using the same real reply |
| Publishing, the public page, quotes, bills, booking replies | Real, and the numbers are worked out live |
| Plain-words changes | A simple scripted reader. The real app uses the model |
