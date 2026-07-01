# Python Capstone Project Idea Proposal

---

## Project Title
Automated Mall-Parking-System

---

## Project Description
This project helps the user to track vehicle entry and exit times, calculate the parking fees and bill them if they stay for more than 30 minutes and give a grace period of 20 more minutes to loyal/frequent customers. It uses file handling to maintain a persistent database of loyal/frequent customers for grace period extensions and uses a live currency API to process payments in both KES and foreign currencies.

---

## Purpose/ Problem Solved
Manual mall parking systems are slow, prone to errors and create long queues at exit barriers. Also, without a structured fee system, drivers tend to abuse the parking lot by leaving their cars all day for free causing a shortage of available spaces for genuine mall customers. Additionally, most mall parking systems lack flexibility to reward frequent customers or accomodate international visitors hence forcing payments exclusively in local currency(KES). This project will build an automated system that uses precise digital time-tracking to eliminate manual errors and automatically applies a 30 minute free parking followed by dynamic biling. This will ensure fair space availability, recognize frequent customers with grace extensions of roughly 20 minutes and fetches live exchange rates to allow multi-currency payments.

---

## Planned Features
- [ ] User input (number plate)
- [ ] datetime (for time tracking)
- [ ] math (to round up parking fractions)
- [ ] External APIs (currency converter)
- [ ] json
- [ ] Databses (SQlite)
- [ ] Loops (for and while)
- [ ] Conditional statements
- [ ] Dictionaries (to store API data)
- [ ] Lists (temporarily hold data before formatting them)
- [ ] Functions (def functions)
- [ ] Object-oriented programming (classes)

---

## Technologies / Concepts I plan to use
> - Python core (functions, loops, dictionaries)  
> - requests (for API calls)  
> - json module (to parse data)  
> - streamlit (for user interface)

---

## Data Source 
- [ ] API (Foreign Exchange Rate API)

---

## Success Criteria
The program is considered fully successful when it can dynamically process vehicle entry and exit inputs in a continuous terminal loop, accurately enforce parking limits and VIP grace periods by pulling and saving records from an active SQLite database and complete a checkout transaction using a live-fetched currency conversion rate without dropping data when the application restarts.

---

## Stretch Goals
