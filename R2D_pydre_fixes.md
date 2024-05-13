# R2D Data Fixes

## OSU Data Files:
For Week 1, Load, Event files, the "CriticalEventStatus" column was not updated for
the cut-in event. Added a filter titled "modifyCriticalEventsCol" that changed the 
CriticalEventStatus column to indicate 1 between the x-positions 2165 and 2240. 

## UAB Data Files:
Several fixes were made.
1. The SimTime column only had 0.0 throughout. Copied over the values in DatTime into SimTime
to fix this issue. 
2. The CriticalEventStatus column was never updated and had 0s throughout.
Added 1s in the CriticalEventStatus column based on where the critical events 
occurred in the videos. Also, locations where critical events began varied for each
scenario type (Load, Event vs No Load, Event), so I processed them separately.
3. The cut-off event would occur at different x-position as it is velocity-dependent. So,
determined when the cut-off began by checking when "HeadwayDistance" would go below a certain
parametrized value and adding 130 meters to that value. This ensured that the CriticalEventStatus
column would change to 1 similarly to the OSU datafiles.
4. For some datafiles, the drive began at the spot where a previous drive ended, and
the XPosition reset once the new drive was loaded up. For example, the XPosition column would
have values starting at 6400 for a few seconds, and would reset back to 20. This was corrected
by filtering out the rows where the x-positions would start at an extremely high value.

## Extra Notes:
In the UAB Week 1, No Load, Event scenario, the trashtip event does not occur. A trashcan shows up
on screen, but it does not tip and thus there is no reaction time detected.