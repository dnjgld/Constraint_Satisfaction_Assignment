**The Problem:**
An air cargo terminal receives aircraft loaded with freight, unloads the aircraft, sorts the cargo, and transfers the cargo to trucks for distribution.

**Arrivals**
Aircraft arrive on a schedule. Each arriving aircraft has:

* A unique name
* An arrival time
* A cargo manifest:
  * The manifest indicates how many cargo pallets are carried on the aircraft

**Scheduling:**

Aircraft must be scheduled to unload at hangars at specific times.

* Once an aircraft arrives at a hangar, it remains until unloaded
  * No aircraft can unload before arriving at a hangar
* Aircraft can wait for a hangar after landing at the terminal (be at “no hangar” between landing at the terminal and arriving at a hangar)

**Hangars**

Aircraft are unloaded at hangars. Each terminal hangar can handle one aircraft at a time.

After pallets are unloaded, they are stored at the hangar until they are subsequently loaded onto a cargo truck

**Forklifts**
Aircraft are unloaded by forklifts. Each forklift can unload one pallet in 20 minutes.

* Any number of forklifts can work to unload a plane at any time
* One pallet can only be unloaded by one forklift
* Multiple pallets can be unloaded from a plane simultaneously
    * Each must be unloaded by a separate forklift
* The aircraft must remain at the hangar until unloading is complete

**Scheduling:**

* Forklifts must be scheduled to work at hangars at specific times.
* Forklifts must be scheduled to unload (from an aircraft) or load (to a truck) (see below)

**Trucks**
Each cargo truck can receive one pallet. Cargo trucks are loaded by forklifts, similar to how aircraft are unloaded by forklifts. Each forklift can load one pallet in 5 minutes:

* A cargo truck can be loaded by one forklift in 5 minutes
* A cargo truck can be loaded by two forklifts in 5 minutes
    * The pallet is already being loaded, so the second forklift has nothing to do
* Each hangar can accommodate one truck at any given time
* Assume the truck leaves as soon as it is loaded

**Scheduling:**

* Cargo trucks must be scheduled to be loaded at hangars at specific times.
* The truck can arrive at the hangar before loading
    * The truck can’t load until it has arrived at a hangar
* Trucks can wait at the terminal (at no hangar) before arriving at a hangar to load

**Scheduling**
* Each aircraft must be scheduled to arrive a specific hangar at a specific time
    * The time must be after the plane arrives at the terminal
    * The aircraft must be scheduled to depart from the hangar after it is finished unloading
* Forklifts must be assigned to a specific hangar
    * Each forklift must be assigned to load or unload at a specific hangar at a specific time
    * A forklift can only unload if there is a plane with cargo waiting to be unloaded
    * A forklift can only load if there is a truck waiting to be loaded and a pallet to load
    
Time is always expressed as minutes on a 24h clock, i.e. 900 is five minutes after 855 and 1300 is five minutes after 1255. Events should be scheduled to the closest five minutes (e.g. 1000, 1005, 1010) and not more granularly.

The scheduling problem is solved if an assignment of aircraft, forklifts, and trucks results in all cargo being unloaded from aircraft and loaded onto trucks by the end of the day.
