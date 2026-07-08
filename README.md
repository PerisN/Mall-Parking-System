# Python Capstone Project Idea Proposal

---

## Project Title
Automated Mall-Parking-System

---

## Project Description
This project helps the user (gate attendants) to track vehicle entry and exit times, calculate the parking fees and bill them accordingly. 
This are the key features:-
> - Customer loyalty detection: Scans historical vehicle entries over a rolling 90-day window and automatically upgrades frequent visitors (>=20 visits) from a Standard Tier (50 mins free grace period) to a Loyal Tier (80 mins free grace period).
> - Progressive tariff calculation: Automatically computes overtime fees at a rate of KES 200 per 20-minute block using ceiling logic, with a hardcoded long-term flat cap of KES 3,000 per day for overnight stays.
> - Digital SMS receipt generation: Simulates mobile network transmission by compiling and rendering text-optimized digital transaction summaries containing ticket IDs, vehicle plates, allocated slots, and settled fees.
> - Automatic parking slot allocation: Dynamically tracks garage occupancy up to a 100-car capacity. The system automatically calculates and assigns the next sequentially available parking bay upon check in and instantly frees it up upon check out.
> - Daily revenue reports: Utilizes aggregate SQL queries to automatically compile a daily ledger, breaking down the exact number of settled invoices and total financial collections grouped by calendar date.
> - Live administrator dashboard: A digital control tower built for mall managers that shows exactly what is happening in the parking lot in real time. It automatically counts how many cars are parked right now (e.g., 15 out of 100 slots filled) and instantly sums up every shilling collected to show total lifetime earnings at a glance.
> - Developer "Time Travel" diagnostics: A built-in testing tool that lets developers skip real world waiting times, by checking a box, you can fake how long a car has been parked to instantly test if the system calculates the correct KES fees and long-term caps without crashing.
---

## Purpose/ Problem Solved
Traditional mall parking setups struggle with messy, manual parking lots where drivers waste time hunting for empty spaces and management has no clear way to track daily earnings. On top of that, people frequently abuse mall parking by dumping their cars there all day, which fills up the lot and limited space for genuine customers who actually want to shop. This project solves these exact problems. It completely automates the parking lot by instantly assigning a specific empty slot to each car at entry, using an automated loyalty system to reward regular shoppers, and enforcing a strict progressive fee system that penalizes people who leave their cars all day. Finally, it gives management a simple, live dashboard that tracks total revenue and available spaces automatically, eliminating paperwork and parking abuse all at once.

---

## Planned Features
- [ ] Vehicle check-in.
- [ ] Vehicle check-out.
- [ ] Time stamping.
- [ ] Parking sessions.
- [ ] Payment table.
- [ ] Time duration calculation.
- [ ] Automatic parking fee calculation.
- [ ] Automatic parking slot allocation.
- [ ] Administration dashboards and reports.
- [ ] Daily revenue reports.
- [ ] Digital SMS Receipt generation.

---

## Technologies / Concepts I plan to use
> - Python core (functions, loops, conditional statements, lists, dictionaries)     
> - streamlit (for user interface)
> - SQLite
> - datetime
> - math

---

## Success Criteria
The program is considered fully successful when it can:
  > - Record vehicle entry and exit times.
  > - Accurate sequential slot allocation.
  > - Accurate parking fee calculation.
  > - Flawless automated loyalty upgrades.
  > - Calculate parking duration accurately.
  > - Apply the free parking period and loyalty grace period correctly.
  > - Reliable time-travel testing.
  > - Store all parking records in SQLite.
  > - Handle invalid user input gracefully.
  > - Continue functioning correctly after application restarts.

---

## Stretch Goals
  > -  QR code or barcode ticket generation
  > - Vehicle entry using license plate recognition.
  > - Uing live APIs for foreign currency conversion.