from config import UNLOCK_SKIN_LEVEL, UNLOCK_CHARACTER_LEVEL, UNLOCK_MAPS_LEVEL


def xp_for_level(level):
    return 500 * level * (level + 1) // 2


def add_xp(profile_data, amount):
    profile_data["xp"] += amount
    current_level = profile_data["level"]
    while profile_data["xp"] >= xp_for_level(current_level + 1):
        current_level += 1
        profile_data["level"] = current_level
        if current_level >= UNLOCK_SKIN_LEVEL and "skin_red" not in profile_data["unlocks"]:
            profile_data["unlocks"].append("skin_red")
        if current_level >= UNLOCK_CHARACTER_LEVEL and "char_alt" not in profile_data["unlocks"]:
            profile_data["unlocks"].append("char_alt")
        if current_level >= UNLOCK_MAPS_LEVEL and "map_unlock_all" not in profile_data["unlocks"]:
            profile_data["unlocks"].append("map_unlock_all")


def update_stats(profile_data, kills=0, deaths=0, won=False, damage=0):
    s = profile_data["stats"]
    s["total_kills"] += kills
    s["total_deaths"] += deaths
    s["matches_played"] += 1
    if won:
        s["matches_won"] += 1
    s["total_damage"] = s.get("total_damage", 0) + damage
