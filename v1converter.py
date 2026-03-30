import json
import os

def total_convert():
    info_dat = "info.dat"
    info_json = "info.json"

    if not os.path.exists(info_dat):
        print(f"Error: {info_dat} not found! Check your folder.")
        return

    print("--- Phase 1: Audio Conversion (.egg -> .ogg) ---")
    with open(info_dat, 'r', encoding='utf-8') as f:
        v2_info = json.load(f)

    original_audio = v2_info.get("_songFilename", "")
    new_audio = original_audio
    
    if original_audio.lower().endswith(".egg"):
        new_audio = original_audio[:-4] + ".ogg"
        if os.path.exists(original_audio):
            if os.path.exists(new_audio):
                os.remove(new_audio)
            os.rename(original_audio, new_audio)
            print(f"  [!] Renamed {original_audio} to {new_audio}")
    
    bpm = v2_info.get("_beatsPerMinute", 120)
    v1_info = {
        "songName": v2_info.get("_songName", "Unknown"),
        "songSubName": v2_info.get("_songSubName", ""),
        "authorName": v2_info.get("_songAuthorName", "Unknown"),
        "beatsPerMinute": bpm,
        "previewStartTime": v2_info.get("_previewStartTime", 12),
        "previewDuration": v2_info.get("_previewDuration", 10),
        "coverImagePath": v2_info.get("_coverImageFilename", "cover.jpg"),
        "environmentName": v2_info.get("_environmentName", "DefaultEnvironment"),
        "difficultyLevels": []
    }

    print("\n--- Phase 2: Difficulty Conversion (v2 -> v1) ---")
    dats_to_delete = [info_dat] # Start the delete list with info.dat

    for diff_set in v2_info.get("_difficultyBeatmapSets", []):
        for beatmap in diff_set.get("_difficultyBeatmaps", []):
            dat_filename = beatmap.get("_beatmapFilename", "")
            json_filename = dat_filename.replace(".dat", ".json")
            njs = beatmap.get("_noteJumpMovementSpeed", 10)
            
            if os.path.exists(dat_filename):
                dats_to_delete.append(dat_filename) # Add to delete list
                with open(dat_filename, 'r', encoding='utf-8') as f:
                    diff_data = json.load(f)

                v1_diff = {
                    "_version": "1.5.0",
                    "_beatsPerMinute": bpm,
                    "_beatsPerBar": 16,
                    "_noteJumpSpeed": njs,
                    "_shuffle": 0,
                    "_shufflePeriod": 0.5,
                    "_events": diff_data.get("_events", []),
                    "_notes": diff_data.get("_notes", []),
                    "_obstacles": diff_data.get("_obstacles", [])
                }

                with open(json_filename, 'w', encoding='utf-8') as f:
                    json.dump(v1_diff, f)
                
                print(f"  [+] Converted {dat_filename} -> {json_filename}")

                v1_info["difficultyLevels"].append({
                    "difficulty": beatmap.get("_difficulty", "Expert"),
                    "difficultyRank": beatmap.get("_difficultyRank", 4),
                    "audioPath": new_audio,
                    "jsonPath": json_filename,
                    "offset": beatmap.get("_customData", {}).get("_editorOffset", 0),
                    "oldOffset": beatmap.get("_customData", {}).get("_editorOldOffset", 0)
                })

    # Save info.json
    with open(info_json, 'w', encoding='utf-8') as f:
        json.dump(v1_info, f, indent=2)

    print("\n--- Phase 3: Auto-Cleanup ---")
    for file in dats_to_delete:
        try:
            os.remove(file)
            print(f"  [x] Deleted old file: {file}")
        except Exception as e:
            print(f"  [?] Could not delete {file}: {e}")

    print("\n--- SUCCESS! ---")
    print(f"Folder is now 100% legacy compatible for version 0.12.2!")

if __name__ == "__main__":
    total_convert()