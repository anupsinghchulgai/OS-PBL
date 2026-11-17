from app.services.scheduler import simulate, compare, ALGORITHMS

def sample():
    return [
        {"pid":"P1","arrival_time":0,"burst_time":5,"priority":2},
        {"pid":"P2","arrival_time":1,"burst_time":3,"priority":1},
        {"pid":"P3","arrival_time":2,"burst_time":1,"priority":3},
    ]

def test_all_algorithms_complete():
    for alg in ALGORITHMS:
        r=simulate(sample(),alg,2)
        assert r["metrics"]["average_turnaround_time"] >= 0
        assert len(r["timeline"]) > 0
        assert len(r["metrics"]["processes"]) == 3

def test_compare():
    r=compare(sample())
    assert len(r["results"]) == 6
    assert {x["algorithm"] for x in r["results"]} == set(ALGORITHMS)
