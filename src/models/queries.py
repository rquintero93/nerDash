"""
MongoDB queries for the ETL process.

"""

default = [
    {"$match": {}},
]

kengrams = [
    {"$match": {}},
]


# kengrams = [
#     {
#         "$match": {"anchorChange": {"$exists": True, "$not": {"$size": 0}}}
#     },
#     {
#         "$unwind": {
#             "path": "$anchorChange",
#             "preserveNullAndEmptyArrays": True
#         }
#     },
#     {
#         "$replaceRoot": {
#             "newRoot": {
#                 "$mergeObjects": ["$$ROOT", "$anchorChange"]
#             }
#         }
#     },
#     {
#         "$unwind": {
#             "path": "$metadata",
#             "preserveNullAndEmptyArrays": True
#         }
#     },
#     {
#         "$replaceRoot": {
#             "newRoot": {
#                 "$mergeObjects": ["$$ROOT", "$metadata"]
#             }
#         }
#     }
# ]
