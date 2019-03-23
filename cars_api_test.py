import pypcars2api
import time

game = pypcars2api.live()

crash = {
  "0" : "CRASH_DAMAGE_NONE",
  "1" : "CRASH_DAMAGE_OFFTRACK",
  "2" : "CRASH_DAMAGE_LARGE_PROP",
  "3" : "CRASH_DAMAGE_SPINNING",
  "4" : "CRASH_DAMAGE_ROLLING",
}

terrain =	{
  "0" : "TERRAIN_ROAD",
  "1" : "TERRAIN_LOW_GRIP_ROAD",
  "2" : "TERRAIN_BUMPY_ROAD1",
  "3" : "TERRAIN_BUMPY_ROAD2",
  "4" : "TERRAIN_BUMPY_ROAD3",
  "5" : "TERRAIN_MARBLES",
  "6" : "TERRAIN_GRASSY_BERMS",
  "7" : "TERRAIN_GRASS",
  "8" : "TERRAIN_GRAVEL",
  "9" : "TERRAIN_BUMPY_GRAVEL",
  "10" : "TERRAIN_RUMBLE_STRIPS",
  "11" : "TERRAIN_DRAINS",
  "12" : "TERRAIN_TYREWALLS",
  "13" : "TERRAIN_CEMENTWALLS",
  "14" : "TERRAIN_GUARDRAILS",
  "15" : "TERRAIN_SAND",
  "16" : "TERRAIN_BUMPY_SAND",
  "17" : "TERRAIN_DIRT",
  "18" : "TERRAIN_BUMPY_DIRT",
  "19" : "TERRAIN_DIRT_ROAD",
  "20" : "TERRAIN_BUMPY_DIRT_ROAD",
  "21" : "TERRAIN_PAVEMENT",
  "22" : "TERRAIN_DIRT_BANK",
  "23" : "TERRAIN_WOOD",
  "24" : "TERRAIN_DRY_VERGE",
  "25" : "TERRAIN_EXIT_RUMBLE_STRIPS",
  "26" : "TERRAIN_GRASSCRETE",
  "27" : "TERRAIN_LONG_GRASS",
  "28" : "TERRAIN_SLOPE_GRASS",
  "29" : "TERRAIN_COBBLES",
  "30" : "TERRAIN_SAND_ROAD",
  "31" : "TERRAIN_BAKED_CLAY",
  "32" : "TERRAIN_ASTROTURF",
  "33" : "TERRAIN_SNOWHALF",
  "34" : "TERRAIN_SNOWFULL"
}
while True:
    print("Speed: " + str(round(game.mSpeed, 1)) + " m/s")
    print("CrashState: " + crash.get(str(game.mCrashState)))
    print("Tyre FL: " + terrain.get(str(game.mTerrain[0])))
    print("Tyre FR: " + terrain.get(str(game.mTerrain[1])))
    print("Tyre RL: " + terrain.get(str(game.mTerrain[2])))
    print("Tyre RR: " + terrain.get(str(game.mTerrain[3])))
    print("Current Lap Dist: " + str(game.mParticipantInfo[0].mCurrentLapDistance) + " m")
    print("X: " + str(game.mParticipantInfo[0].mWorldPosition[0]))
    print("Y: " + str(game.mParticipantInfo[0].mWorldPosition[1]))
    print("Z: " + str(game.mParticipantInfo[0].mWorldPosition[2]))
    time.sleep(0.5)