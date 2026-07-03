# Python Capstone Project Idea Proposal

---

## Project Title
Automated Mall-Parking-System

---

## Project Description
This project helps the user (gate attendants) to track vehicle entry and exit times, calculate the parking fees and bill them accordingly. A grace period of 50 minutes will be applied and if they exceed, they will be charged 200 Kenya Shillings for every extra 20 minutes that they extend with. However, there will be an extended grace period of 30 minutes for frequent customers who will be identified and granted the reward after their 20th visit to the mall in a span of 3 months and they will be identified by their name and vehicle number plate. If a customer wishes to leave their car parked there for longer, they will be charged 3,000 Kenyan Shilling for every 24 hours since they checked in. The program uses databases to maintain a persistent record of frequent customers for grace period extensions and uses a live currency API to process payments in both KES and foreign currencies.

---

## Purpose/ Problem Solved
Manual mall parking systems are slow, prone to errors and create long queues at exit barriers. Also, without a structured fee system, drivers tend to abuse the parking lot by leaving their cars all day for free causing a shortage of available spaces for genuine mall customers. Additionally, most mall parking systems lack flexibility to reward frequent customers or accomodate international visitors hence forcing payments exclusively in local currency(KES). This project will build an automated system that uses precise digital time-tracking to eliminate manual errors and automatically applies a 30 minute free parking followed by dynamic biling. This will ensure fair space availability, recognize frequent customers with grace extensions of roughly 20 minutes and fetches live exchange rates to allow multi-currency payments.

---

## Planned Features
- [ ] Vehicle check-in
- [ ] Vehicle check-out
- [ ] Time stamping
- [ ] Parking sessions
- [ ] Payment table
- [ ] Time duration calculation
- [ ] Automatic parking fee calculation.
- [ ] Multi-currency payment calculation
- [ ] SMS Receipt generation

---

## Technologies / Concepts I plan to use
> - Python core (functions, loops, conditional statements, lists, dictionaries)  
> - requests (for API calls)  
> - json module (to parse data)  
> - streamlit (for user interface)
> - SQLite
> - Requests
> - datetime
> - math
> - External APIs 
> - JSON
> - Object-oriented programming 

---

## Data Source 
Frankfurter API will be used to retrieve current exchange rates, allowing parking fees to be displayed in both Kenyan Shillings (KES) and selected foreign currencies.

---

## Success Criteria
The program is considered fully successful when it can:
  > - Record vehicle entry and exit times.
  > - Calculate parking duration accurately.
  > - Apply the free parking period and loyalty grace period correctly.
  > - Calculate parking charges automatically.
  > - Convert charges into selected currencies using a live exchange rate.
  > - Store all parking records in SQLite.
  > - Handle invalid user input gracefully.
  > - Continue functioning correctly after application restarts.

---

## Stretch Goals
  > -  QR code or barcode ticket generation
  > - Automatic parking slot allocation.
  > - Vehicle entry using license plate recognition.