from experiments.metrics import catalog_coverage, intra_list_diversity, ndcg_at_k, recall_at_k


def test_ndcg_perfect_order_is_one():
    rel = {"a": 1.0, "b": 0.5, "c": 0.0}
    assert ndcg_at_k(["a", "b", "c"], rel, 3) == 1.0


def test_ndcg_worse_order_is_lower():
    rel = {"a": 1.0, "b": 0.5, "c": 0.0}
    assert ndcg_at_k(["c", "b", "a"], rel, 3) < ndcg_at_k(["a", "b", "c"], rel, 3)


def test_ndcg_zero_when_no_relevance():
    assert ndcg_at_k(["a"], {"a": 0.0}, 1) == 0.0


def test_recall_basic_and_empty():
    assert recall_at_k(["a", "b", "c"], ["a", "z"], 3) == 0.5
    assert recall_at_k(["a"], [], 1) is None


def test_coverage():
    assert catalog_coverage(["a", "a", "b"], 4) == 0.5


def test_intra_list_diversity():
    assert intra_list_diversity([["pop", "rock"], ["pop", "pop"]]) == 0.75
