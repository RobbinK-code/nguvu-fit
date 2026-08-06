"""Static reference data mapping muscle groups to gym machine/equipment
alternatives - so a home-workout plan still translates when someone's at
a commercial gym. Kept as plain data (not a DB table) since it's shared
reference content, not per-user data; easy to move into a table later if
it needs to become admin-editable.
"""

EQUIPMENT = {
    "legs": [
        {
            "id": "leg-press",
            "name": "Leg Press Machine",
            "icon": "plate-stack",
            "description": "A seated machine that lets you push weight away with your legs - "
            "one of the safest ways to load your legs heavily without needing a spotter.",
            "how_to": [
                "Sit in the machine with your back flat against the pad and feet shoulder-width on the platform.",
                "Release the safety catches and lower the platform until your knees reach about 90 degrees.",
                "Press through your heels to extend your legs, without locking your knees at the top.",
                "Control the weight back down - don't let it drop.",
            ],
        },
        {
            "id": "leg-extension",
            "name": "Leg Extension Machine",
            "icon": "cable",
            "description": "An isolation machine that targets your quads directly by extending your knee against resistance.",
            "how_to": [
                "Sit with your back against the pad and the ankle pad resting just above your feet.",
                "Extend your legs until they're straight, squeezing your quads at the top.",
                "Lower back down slowly - don't let the weight stack slam.",
            ],
        },
        {
            "id": "smith-squat",
            "name": "Smith Machine Squat",
            "icon": "barbell",
            "description": "A guided barbell fixed on vertical rails - a good stepping stone into barbell squats "
            "since the bar path is fixed for you.",
            "how_to": [
                "Set the bar at shoulder height and step under it, resting it across your upper back.",
                "Unrack it, step back, and set your feet shoulder-width apart.",
                "Squat down until your thighs are roughly parallel to the floor, then drive back up.",
            ],
        },
    ],
    "chest": [
        {
            "id": "chest-press-machine",
            "name": "Chest Press Machine",
            "icon": "plate-stack",
            "description": "A seated pressing machine that mimics a bench press without needing a spotter.",
            "how_to": [
                "Adjust the seat so the handles sit at chest height.",
                "Press the handles forward until your arms are extended, without locking your elbows hard.",
                "Return slowly to the starting position.",
            ],
        },
        {
            "id": "cable-crossover",
            "name": "Cable Crossover",
            "icon": "cable",
            "description": "Two adjustable cable towers that let you bring your hands together in front of you, "
            "targeting the chest through a long range of motion.",
            "how_to": [
                "Set both pulleys to chest height and grab a handle in each hand.",
                "Step forward with a slight forward lean and a soft bend in your elbows.",
                "Bring your hands together in front of your chest, then return with control.",
            ],
        },
        {
            "id": "smith-bench-press",
            "name": "Smith Machine Bench Press",
            "icon": "barbell",
            "description": "A fixed-rail bar over a bench - a guided way to work up to a free-weight bench press.",
            "how_to": [
                "Lie on the bench under the bar with it aligned over your chest.",
                "Unrack it, lower it to your chest with control, then press back up.",
            ],
        },
    ],
    "back": [
        {
            "id": "lat-pulldown",
            "name": "Lat Pulldown",
            "icon": "cable",
            "description": "A cable machine that mimics a pull-up, letting you build pulling strength "
            "with adjustable weight.",
            "how_to": [
                "Sit with your thighs secured under the pad, grip the bar wider than shoulder-width.",
                "Pull the bar down to your upper chest, squeezing your shoulder blades together.",
                "Let it rise back up with control, without shrugging your shoulders up.",
            ],
        },
        {
            "id": "seated-row",
            "name": "Seated Cable Row",
            "icon": "cable",
            "description": "A seated pulling machine that targets your mid-back by rowing a handle toward your torso.",
            "how_to": [
                "Sit with knees slightly bent, feet on the platform, and grab the handle.",
                "Pull it toward your lower ribs, keeping your back straight and elbows close.",
                "Extend back out with control, letting your shoulders stretch forward slightly.",
            ],
        },
    ],
    "shoulders": [
        {
            "id": "shoulder-press-machine",
            "name": "Shoulder Press Machine",
            "icon": "plate-stack",
            "description": "A seated pressing machine for your shoulders, safer than free weights when working near failure.",
            "how_to": [
                "Sit with the handles at shoulder height and your back flat against the pad.",
                "Press upward until your arms are extended without locking out hard.",
                "Lower back to the start with control.",
            ],
        },
        {
            "id": "lateral-raise-machine",
            "name": "Lateral Raise Machine",
            "icon": "cable",
            "description": "An isolation machine for the side of your shoulders, mimicking a dumbbell lateral raise.",
            "how_to": [
                "Sit with your arms against the pads at your sides.",
                "Raise your arms out to the sides until roughly shoulder height.",
                "Lower with control - don't let momentum take over.",
            ],
        },
    ],
    "arms": [
        {
            "id": "cable-tricep-pushdown",
            "name": "Cable Tricep Pushdown",
            "icon": "cable",
            "description": "A cable exercise isolating your triceps by pushing a bar or rope downward.",
            "how_to": [
                "Grab the attachment with an overhand grip, elbows tucked to your sides.",
                "Push down until your arms are extended, squeezing your triceps.",
                "Let it rise back up without letting your elbows flare out.",
            ],
        },
        {
            "id": "cable-bicep-curl",
            "name": "Cable Bicep Curl",
            "icon": "cable",
            "description": "A cable version of a bicep curl - constant tension through the whole movement.",
            "how_to": [
                "Stand facing the low pulley, grab the bar with an underhand grip.",
                "Curl the bar up toward your chest, keeping your elbows still.",
                "Lower with control back to the start.",
            ],
        },
    ],
    "core": [
        {
            "id": "cable-woodchopper",
            "name": "Cable Woodchopper",
            "icon": "cable",
            "description": "A rotational cable exercise that builds core strength through a twisting motion.",
            "how_to": [
                "Set the pulley high, grab the handle with both hands, and stand side-on to the machine.",
                "Pull the handle diagonally down across your body, rotating through your torso.",
                "Return with control and repeat, then switch sides.",
            ],
        },
        {
            "id": "ab-crunch-machine",
            "name": "Ab Crunch Machine",
            "icon": "plate-stack",
            "description": "A seated machine that loads a crunching motion, letting you add resistance to core work.",
            "how_to": [
                "Sit with your chest against the pad and hands on the grips.",
                "Crunch forward, contracting your abs, then return with control.",
            ],
        },
    ],
    "full_body": [
        {
            "id": "functional-trainer",
            "name": "Functional Trainer (Dual Cable Station)",
            "icon": "cable",
            "description": "A dual-pulley station that can mimic almost any bodyweight movement with added resistance - "
            "squats, presses, rows, and rotations, all in one machine.",
            "how_to": [
                "Adjust both pulleys to match the movement you're doing (low for squats/rows, high for presses/pulldowns).",
                "Keep your core braced and move with control through the full range of motion.",
            ],
        },
        {
            "id": "kettlebells",
            "name": "Kettlebells",
            "icon": "barbell",
            "description": "Versatile free weights good for swings, goblet squats, and full-body conditioning circuits.",
            "how_to": [
                "Start with a weight you can control through a full range of motion.",
                "For a goblet squat: hold it at chest height and squat down, keeping your chest up.",
            ],
        },
    ],
    "cardio": [
        {
            "id": "treadmill",
            "name": "Treadmill",
            "icon": "cardio",
            "description": "A motorized running belt - the most direct gym equivalent to outdoor running or brisk walking.",
            "how_to": [
                "Start slow to get a feel for the belt speed before increasing pace.",
                "Keep an upright posture rather than leaning on the front console.",
            ],
        },
        {
            "id": "rowing-machine",
            "name": "Rowing Machine",
            "icon": "cardio",
            "description": "A full-body cardio machine that also works your back and legs - a strong alternative to "
            "bodyweight cardio circuits.",
            "how_to": [
                "Push off with your legs first, then lean back slightly and pull the handle to your chest.",
                "Reverse the order on the way back: arms, then torso, then legs.",
            ],
        },
        {
            "id": "stationary-bike",
            "name": "Stationary Bike",
            "icon": "cardio",
            "description": "A low-impact cardio option, good for intervals without the joint stress of running.",
            "how_to": [
                "Set the seat height so your knee has a slight bend at the bottom of the pedal stroke.",
                "Alternate between a steady pace and short bursts of higher intensity for interval training.",
            ],
        },
    ],
}


def get_equipment(muscle_group=None):
    if muscle_group:
        return EQUIPMENT.get(muscle_group, [])
    return EQUIPMENT
