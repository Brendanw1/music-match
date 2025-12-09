"""Quiz questions for determining user music preferences."""

QUIZ_QUESTIONS = [
    # Energy questions (2)
    {
        "id": "energy_1",
        "question": "Pick the energy level that matches your current mood:",
        "options": [
            {
                "id": "a",
                "text": "I want to feel alive and pumped up",
                "weights": {"energy": 1.0, "loudness": 0.7, "valence": 0.6}
            },
            {
                "id": "b",
                "text": "Something with momentum but not overwhelming",
                "weights": {"energy": 0.6, "danceability": 0.5}
            },
            {
                "id": "c",
                "text": "Relaxed and easy-going",
                "weights": {"energy": 0.3, "acousticness": 0.4}
            },
            {
                "id": "d",
                "text": "Calm, ambient, atmospheric",
                "weights": {"energy": 0.1, "instrumentalness": 0.5}
            }
        ]
    },
    {
        "id": "energy_2",
        "question": "When you need music to help you focus, you prefer:",
        "options": [
            {
                "id": "a",
                "text": "High-intensity tracks that keep me alert",
                "weights": {"energy": 0.9, "loudness": 0.6}
            },
            {
                "id": "b",
                "text": "Steady rhythms with moderate energy",
                "weights": {"energy": 0.5, "danceability": 0.4}
            },
            {
                "id": "c",
                "text": "Soft background music",
                "weights": {"energy": 0.2, "acousticness": 0.5, "instrumentalness": 0.4}
            },
            {
                "id": "d",
                "text": "Complete silence or minimal ambient sounds",
                "weights": {"energy": 0.05, "instrumentalness": 0.8}
            }
        ]
    },
    # Mood/Valence questions (2)
    {
        "id": "mood_1",
        "question": "What emotional tone are you looking for right now?",
        "options": [
            {
                "id": "a",
                "text": "Happy and uplifting - I want to feel good",
                "weights": {"valence": 1.0, "energy": 0.6}
            },
            {
                "id": "b",
                "text": "Bittersweet - something that understands complex feelings",
                "weights": {"valence": 0.5, "acousticness": 0.3}
            },
            {
                "id": "c",
                "text": "Melancholic - I'm in a reflective mood",
                "weights": {"valence": 0.2, "acousticness": 0.5}
            },
            {
                "id": "d",
                "text": "Dark and intense - I want depth",
                "weights": {"valence": 0.1, "energy": 0.6, "loudness": 0.5}
            }
        ]
    },
    {
        "id": "mood_2",
        "question": "Music that makes you feel nostalgic tends to be:",
        "options": [
            {
                "id": "a",
                "text": "Warm and comforting, like a sunny memory",
                "weights": {"valence": 0.7, "acousticness": 0.6}
            },
            {
                "id": "b",
                "text": "Energetic reminders of good times",
                "weights": {"valence": 0.8, "energy": 0.7, "danceability": 0.5}
            },
            {
                "id": "c",
                "text": "Wistful and longing",
                "weights": {"valence": 0.3, "acousticness": 0.4}
            },
            {
                "id": "d",
                "text": "I don't usually seek nostalgic music",
                "weights": {"valence": 0.5}
            }
        ]
    },
    # Danceability questions (2)
    {
        "id": "dance_1",
        "question": "When a good song comes on, you typically:",
        "options": [
            {
                "id": "a",
                "text": "Can't help but move - dancing is inevitable",
                "weights": {"danceability": 1.0, "energy": 0.7}
            },
            {
                "id": "b",
                "text": "Nod along or tap your foot",
                "weights": {"danceability": 0.6}
            },
            {
                "id": "c",
                "text": "Just listen and appreciate",
                "weights": {"danceability": 0.3, "instrumentalness": 0.3}
            },
            {
                "id": "d",
                "text": "Get lost in thought",
                "weights": {"danceability": 0.1, "acousticness": 0.4}
            }
        ]
    },
    {
        "id": "dance_2",
        "question": "At a party, you prefer music that:",
        "options": [
            {
                "id": "a",
                "text": "Gets everyone on the dance floor",
                "weights": {"danceability": 1.0, "energy": 0.8, "valence": 0.7}
            },
            {
                "id": "b",
                "text": "Creates a fun vibe without demanding attention",
                "weights": {"danceability": 0.6, "valence": 0.6}
            },
            {
                "id": "c",
                "text": "Allows for conversation",
                "weights": {"danceability": 0.3, "energy": 0.3}
            },
            {
                "id": "d",
                "text": "I prefer smaller gatherings with curated playlists",
                "weights": {"danceability": 0.4, "acousticness": 0.4}
            }
        ]
    },
    # Acousticness question (1)
    {
        "id": "acoustic_1",
        "question": "How do you feel about acoustic/unplugged music?",
        "options": [
            {
                "id": "a",
                "text": "Love it - there's something raw and authentic about it",
                "weights": {"acousticness": 1.0, "instrumentalness": 0.3}
            },
            {
                "id": "b",
                "text": "Enjoy it sometimes, depends on my mood",
                "weights": {"acousticness": 0.5}
            },
            {
                "id": "c",
                "text": "Prefer a mix of electronic and organic sounds",
                "weights": {"acousticness": 0.3, "energy": 0.5}
            },
            {
                "id": "d",
                "text": "Give me synthesizers and electronic production",
                "weights": {"acousticness": 0.1, "energy": 0.6}
            }
        ]
    },
    # Vocals/Instrumentalness question (1)
    {
        "id": "vocals_1",
        "question": "When it comes to vocals in music:",
        "options": [
            {
                "id": "a",
                "text": "Lyrics and vocals are essential - I connect with the words",
                "weights": {"instrumentalness": 0.0}
            },
            {
                "id": "b",
                "text": "I like vocals but they don't need to be the focus",
                "weights": {"instrumentalness": 0.3}
            },
            {
                "id": "c",
                "text": "Often prefer instrumental music",
                "weights": {"instrumentalness": 0.7}
            },
            {
                "id": "d",
                "text": "Strongly prefer music without vocals",
                "weights": {"instrumentalness": 1.0}
            }
        ]
    },
    # Tempo question (1)
    {
        "id": "tempo_1",
        "question": "Your preferred tempo for everyday listening:",
        "options": [
            {
                "id": "a",
                "text": "Fast and driving (140+ BPM)",
                "weights": {"bpm_normalized": 1.0, "energy": 0.7}
            },
            {
                "id": "b",
                "text": "Upbeat and groovy (110-140 BPM)",
                "weights": {"bpm_normalized": 0.7, "danceability": 0.6}
            },
            {
                "id": "c",
                "text": "Moderate and steady (80-110 BPM)",
                "weights": {"bpm_normalized": 0.5}
            },
            {
                "id": "d",
                "text": "Slow and deliberate (under 80 BPM)",
                "weights": {"bpm_normalized": 0.2, "acousticness": 0.3}
            }
        ]
    },
    # Context questions (3)
    {
        "id": "context_1",
        "question": "You're going for a workout. What do you reach for?",
        "options": [
            {
                "id": "a",
                "text": "High-energy bangers that push me harder",
                "weights": {"energy": 1.0, "loudness": 0.8, "danceability": 0.7}
            },
            {
                "id": "b",
                "text": "Steady beats that help me pace myself",
                "weights": {"energy": 0.6, "danceability": 0.6}
            },
            {
                "id": "c",
                "text": "I don't really listen to music while exercising",
                "weights": {"energy": 0.4}
            },
            {
                "id": "d",
                "text": "Podcasts or audiobooks instead",
                "weights": {"instrumentalness": 0.2}
            }
        ]
    },
    {
        "id": "context_2",
        "question": "For a late-night drive, you'd choose:",
        "options": [
            {
                "id": "a",
                "text": "Atmospheric electronic or synthwave",
                "weights": {"energy": 0.5, "instrumentalness": 0.6, "valence": 0.4}
            },
            {
                "id": "b",
                "text": "Chill indie or alternative",
                "weights": {"acousticness": 0.5, "energy": 0.4, "valence": 0.5}
            },
            {
                "id": "c",
                "text": "Upbeat pop or rock to stay alert",
                "weights": {"energy": 0.8, "valence": 0.7}
            },
            {
                "id": "d",
                "text": "R&B or soul for smooth vibes",
                "weights": {"danceability": 0.6, "valence": 0.6, "acousticness": 0.4}
            }
        ]
    },
    {
        "id": "context_3",
        "question": "When you're feeling stressed, music should:",
        "options": [
            {
                "id": "a",
                "text": "Help me release tension with something intense",
                "weights": {"energy": 0.9, "loudness": 0.7}
            },
            {
                "id": "b",
                "text": "Distract me with something fun and upbeat",
                "weights": {"valence": 0.8, "danceability": 0.6}
            },
            {
                "id": "c",
                "text": "Calm me down with something peaceful",
                "weights": {"energy": 0.2, "acousticness": 0.7, "instrumentalness": 0.5}
            },
            {
                "id": "d",
                "text": "Match my mood so I can process it",
                "weights": {"valence": 0.3, "acousticness": 0.4}
            }
        ]
    }
]


def get_questions() -> list[dict]:
    """Get all quiz questions (without weights for client)."""
    return [
        {
            "id": q["id"],
            "question": q["question"],
            "options": [
                {"id": opt["id"], "text": opt["text"]}
                for opt in q["options"]
            ]
        }
        for q in QUIZ_QUESTIONS
    ]


def get_question_by_id(question_id: str) -> dict | None:
    """Get a specific question by ID."""
    for q in QUIZ_QUESTIONS:
        if q["id"] == question_id:
            return q
    return None
