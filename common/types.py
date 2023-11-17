from typing import Literal

question_category = Literal[
    "Literature",
    "History",
    "Science",
    "Fine Arts",
    "Religion",
    "Mythology",
    "Philosophy",
    "Social Science",
    "Current Events",
    "Geography",
    "Other Academic",
    "Trash",
]

category_field_translations = {
    'Literature': 'literature',
    'History': 'history',
    'Science': 'science',
    'Fine Arts': 'fine_arts',
    'Religion': 'religion',
    'Mythology': 'mythology',
    'Philosophy': 'philosophy',
    'Social Science': 'social_science',
    'Current Events': 'current_events',
    'Geography': 'geography',
    'Other Academic': 'other_academic',
    'Trash': 'trash'
}
