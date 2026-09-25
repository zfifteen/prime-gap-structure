from .fermat import fermat_steps
from .contamination import check_contamination

FIXTURES = {
    "40-bit": {"N": 1099507433251, "p": 1048559, "q": 1048589},
    "50-bit": {"N": 1027435935526951, "p": 30729371, "q": 33434981},
    "64-bit": {"N": 10376454699372036973, "p": 3221225473, "q": 3221275501}
}

def run_official_replay():
    results = {}
    for name, data in FIXTURES.items():
        contam = check_contamination(data["N"], data["p"], data["q"])
        steps, _, _ = fermat_steps(data["N"])
        
        results[name] = {
            "N": data["N"],
            "isqrt": contam["isqrt"],
            "fermat_steps": steps,
            "near_square": contam["near_square"],
            "min_dist": contam["min_dist"]
        }
    return results
