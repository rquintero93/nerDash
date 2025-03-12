'''
MongoDB queries for the ETL process.

'''

kengrams = [
    {
        "$match": {"anchorChange": {"$exists": True, "$not": {"$size": 0}}}
    },  # Ensure "anchorChange" field exists
    {"$unwind": "$anchorChange"},  # Flatten the "anchorChange" array
    {
        "$replaceRoot": {
            "newRoot": {
                "$mergeObjects": ["$$ROOT", "$anchorChange"]
            }
        }
    },
    {
        "$unwind": "$metadata"  # Flatten the "metadata" array
    },
    {
        "$replaceRoot": {
            "newRoot": {
                "$mergeObjects": ["$$ROOT", "$metadata"]
            }
        }
    }
]
