# Bookiniste

Small CLI cheking for book deals on Amazon.

## Configuration file

```json
{
    "aws": {
        "AWS_ACCESS_KEY_ID": "XXXX",
        "AWS_SECRET_ACCESS_KEY": "YYYY",
        "AWS_ASSOCIATE_TAG": "IIII"
    },
    "whislist": [
        {
            "ISBN": "2020414775",
            "target": 3
        },
        {
            "ISBN": "2330096585",
            "target": 7
        }
    ]
}
```

## Output

```
➜  bookiniste python bookiniste.py deals
100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████| 2/2 [00:00<00:00,  3.48req./s]
- Les Adieux à la reine - P..: 3€    -> 0.8€  / 15.0€ (-2.2€ / -75.0%)
- Le grand Nord-Ouest        : 7€    -> 13.5€ / 21.5€ (6.5€  / 92.7%)
```