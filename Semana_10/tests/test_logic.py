import pytest

from logic import (
    And,
    Biconditional,
    EvaluationException,
    Implication,
    Not,
    Or,
    Symbol,
    model_check,
)


# ---------------------------------------------------------------------------
# Symbol
# ---------------------------------------------------------------------------


def test_symbol_evaluate_returns_true_when_model_assigns_true():
    p = Symbol("p")

    assert p.evaluate({"p": True}) is True


def test_symbol_evaluate_returns_false_when_model_assigns_false():
    p = Symbol("p")

    assert p.evaluate({"p": False}) is False


def test_symbol_evaluate_raises_when_symbol_not_in_model():
    p = Symbol("p")

    with pytest.raises(EvaluationException):
        p.evaluate({})


def test_symbol_evaluate_raises_with_message_containing_symbol_name():
    p = Symbol("missing_var")

    with pytest.raises(EvaluationException, match="missing_var"):
        p.evaluate({})


def test_symbol_formula_returns_symbol_name():
    p = Symbol("rain")

    assert p.formula() == "rain"


def test_symbol_symbols_returns_singleton_set_with_own_name():
    p = Symbol("rain")

    assert p.symbols() == {"rain"}


def test_symbol_eq_true_for_same_name():
    assert Symbol("p") == Symbol("p")


def test_symbol_eq_false_for_different_name():
    assert Symbol("p") != Symbol("q")


def test_symbol_eq_false_for_non_symbol():
    assert Symbol("p") != "p"


def test_symbol_hash_equal_for_same_name():
    assert hash(Symbol("p")) == hash(Symbol("p"))


def test_symbol_hash_usable_in_set():
    p = Symbol("p")
    assert p in {Symbol("p")}


def test_symbol_repr_returns_name():
    assert repr(Symbol("x")) == "x"


# ---------------------------------------------------------------------------
# Not
# ---------------------------------------------------------------------------


def test_not_evaluate_negates_true_operand():
    p = Symbol("p")

    assert Not(p).evaluate({"p": True}) is False


def test_not_evaluate_negates_false_operand():
    p = Symbol("p")

    assert Not(p).evaluate({"p": False}) is True


def test_not_formula_uses_negation_symbol():
    p = Symbol("p")

    assert Not(p).formula() == "¬p"


def test_not_formula_parenthesizes_compound_operand():
    p = Symbol("p")
    q = Symbol("q")

    assert Not(And(p, q)).formula() == "¬(p ∧ q)"


def test_not_symbols_delegates_to_operand():
    p = Symbol("p")
    q = Symbol("q")

    assert Not(And(p, q)).symbols() == {"p", "q"}


def test_not_raises_type_error_for_non_sentence_operand():
    with pytest.raises(TypeError):
        Not(42)


# ---------------------------------------------------------------------------
# And
# ---------------------------------------------------------------------------


def test_and_evaluate_true_when_all_conjuncts_true():
    p, q = Symbol("p"), Symbol("q")

    assert And(p, q).evaluate({"p": True, "q": True}) is True


def test_and_evaluate_false_when_any_conjunct_false():
    p, q = Symbol("p"), Symbol("q")

    assert And(p, q).evaluate({"p": True, "q": False}) is False


def test_and_evaluate_empty_conjuncts_returns_true():
    assert And().evaluate({}) is True


def test_and_evaluate_single_conjunct_returns_its_value():
    p = Symbol("p")

    assert And(p).evaluate({"p": False}) is False


def test_and_formula_joins_with_conjunction_symbol():
    p, q = Symbol("p"), Symbol("q")

    assert And(p, q).formula() == "p ∧ q"


def test_and_formula_with_single_conjunct_returns_plain_formula():
    p = Symbol("p")

    assert And(p).formula() == "p"


def test_and_formula_empty_returns_empty_string():
    assert And().formula() == ""


def test_and_formula_parenthesizes_compound_conjuncts():
    p, q, r = Symbol("p"), Symbol("q"), Symbol("r")

    assert And(Or(p, q), r).formula() == "(p ∨ q) ∧ r"


def test_and_symbols_returns_union_of_all_conjunct_symbols():
    p, q, r = Symbol("p"), Symbol("q"), Symbol("r")

    assert And(p, q, r).symbols() == {"p", "q", "r"}


def test_and_symbols_returns_empty_set_for_empty_and():
    assert And().symbols() == set()


def test_and_add_appends_conjunct_and_evaluates_correctly():
    p, q = Symbol("p"), Symbol("q")
    a = And(p)
    a.add(q)

    assert a.evaluate({"p": True, "q": True}) is True
    assert a.evaluate({"p": True, "q": False}) is False


def test_and_add_raises_type_error_for_non_sentence():
    with pytest.raises(TypeError):
        And().add("not a sentence")


# ---------------------------------------------------------------------------
# Or
# ---------------------------------------------------------------------------


def test_or_evaluate_true_when_any_disjunct_true():
    p, q = Symbol("p"), Symbol("q")

    assert Or(p, q).evaluate({"p": False, "q": True}) is True


def test_or_evaluate_false_when_all_disjuncts_false():
    p, q = Symbol("p"), Symbol("q")

    assert Or(p, q).evaluate({"p": False, "q": False}) is False


def test_or_evaluate_empty_disjuncts_returns_false():
    assert Or().evaluate({}) is False


def test_or_evaluate_single_disjunct_returns_its_value():
    p = Symbol("p")

    assert Or(p).evaluate({"p": True}) is True


def test_or_formula_joins_with_disjunction_symbol():
    p, q = Symbol("p"), Symbol("q")

    assert Or(p, q).formula() == "p ∨ q"


def test_or_formula_with_single_disjunct_returns_plain_formula():
    p = Symbol("p")

    assert Or(p).formula() == "p"


def test_or_formula_empty_returns_empty_string():
    assert Or().formula() == ""


def test_or_formula_parenthesizes_compound_disjuncts():
    p, q, r = Symbol("p"), Symbol("q"), Symbol("r")

    assert Or(Implication(p, q), r).formula() == "(p => q) ∨ r"


def test_or_symbols_returns_union_of_all_disjunct_symbols():
    p, q = Symbol("p"), Symbol("q")

    assert Or(p, q).symbols() == {"p", "q"}


def test_or_symbols_returns_empty_set_for_empty_or():
    assert Or().symbols() == set()


def test_or_add_appends_disjunct_and_evaluates_correctly():
    p, q = Symbol("p"), Symbol("q")
    o = Or(p)
    o.add(q)

    assert o.evaluate({"p": False, "q": True}) is True


def test_or_add_raises_type_error_for_non_sentence():
    with pytest.raises(TypeError):
        Or().add(99)


# ---------------------------------------------------------------------------
# Implication
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("antecedent_val", "consequent_val", "expected"),
    [
        (True, True, True),
        (True, False, False),
        (False, True, True),
        (False, False, True),
    ],
)
def test_implication_evaluate_truth_table(antecedent_val, consequent_val, expected):
    p, q = Symbol("p"), Symbol("q")
    result = Implication(p, q).evaluate({"p": antecedent_val, "q": consequent_val})

    assert result is expected


def test_implication_formula_uses_arrow():
    p, q = Symbol("p"), Symbol("q")

    assert Implication(p, q).formula() == "p => q"


def test_implication_formula_parenthesizes_compound_operands():
    p, q, r = Symbol("p"), Symbol("q"), Symbol("r")

    assert Implication(And(p, q), r).formula() == "(p ∧ q) => r"


def test_implication_symbols_returns_union_of_both_sides():
    p, q = Symbol("p"), Symbol("q")

    assert Implication(p, q).symbols() == {"p", "q"}


def test_implication_raises_type_error_for_non_sentence_antecedent():
    with pytest.raises(TypeError):
        Implication("p", Symbol("q"))


def test_implication_raises_type_error_for_non_sentence_consequent():
    with pytest.raises(TypeError):
        Implication(Symbol("p"), "q")


# ---------------------------------------------------------------------------
# Biconditional
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("left_val", "right_val", "expected"),
    [
        (True, True, True),
        (True, False, False),
        (False, True, False),
        (False, False, True),
    ],
)
def test_biconditional_evaluate_truth_table(left_val, right_val, expected):
    p, q = Symbol("p"), Symbol("q")
    result = Biconditional(p, q).evaluate({"p": left_val, "q": right_val})

    assert result is expected


def test_biconditional_formula_uses_double_arrow():
    p, q = Symbol("p"), Symbol("q")

    assert Biconditional(p, q).formula() == "p <=> q"


def test_biconditional_formula_parenthesizes_compound_operands():
    p, q, r = Symbol("p"), Symbol("q"), Symbol("r")

    assert Biconditional(And(p, q), r).formula() == "(p ∧ q) <=> r"


def test_biconditional_symbols_returns_union_of_both_sides():
    p, q = Symbol("p"), Symbol("q")

    assert Biconditional(p, q).symbols() == {"p", "q"}


def test_biconditional_raises_type_error_for_non_sentence_left():
    with pytest.raises(TypeError):
        Biconditional(True, Symbol("q"))


def test_biconditional_raises_type_error_for_non_sentence_right():
    with pytest.raises(TypeError):
        Biconditional(Symbol("p"), False)


# ---------------------------------------------------------------------------
# model_check — simple cases
# ---------------------------------------------------------------------------


def test_model_check_returns_true_for_known_symbol():
    p = Symbol("p")

    assert model_check(p, p) is True


def test_model_check_modus_ponens_entails_consequent():
    p, q = Symbol("p"), Symbol("q")
    kb = And(p, Implication(p, q))

    assert model_check(kb, q) is True


def test_model_check_does_not_entail_unsupported_conclusion():
    p, q = Symbol("p"), Symbol("q")
    kb = p

    assert model_check(kb, q) is False


def test_model_check_tautology_is_always_entailed():
    p = Symbol("p")
    tautology = Or(p, Not(p))

    assert model_check(And(p), tautology) is True


def test_model_check_contradiction_as_knowledge_entails_anything():
    p, q = Symbol("p"), Symbol("q")
    contradiction = And(p, Not(p))

    assert model_check(contradiction, q) is True


def test_model_check_biconditional_entails_right_when_left_known():
    a, b = Symbol("a"), Symbol("b")
    kb = And(Biconditional(a, b), a)

    assert model_check(kb, b) is True


def test_model_check_biconditional_does_not_entail_right_without_left():
    a, b = Symbol("a"), Symbol("b")
    kb = Biconditional(a, b)

    assert model_check(kb, b) is False


# ---------------------------------------------------------------------------
# model_check — Harry Potter puzzle
# ---------------------------------------------------------------------------


def test_model_check_harry_puzzle_rain_is_false():
    rain = Symbol("rain")
    hagrid = Symbol("hagrid")
    dumbledore = Symbol("dumbledore")

    knowledge = And()
    knowledge.add(Implication(Not(rain), hagrid))
    knowledge.add(Or(hagrid, dumbledore))
    knowledge.add(
        And(
            Implication(hagrid, Not(dumbledore)),
            Implication(dumbledore, Not(hagrid)),
        )
    )
    knowledge.add(dumbledore)

    assert model_check(knowledge, rain) is True


def test_model_check_harry_puzzle_hagrid_is_false():
    rain = Symbol("rain")
    hagrid = Symbol("hagrid")
    dumbledore = Symbol("dumbledore")

    knowledge = And()
    knowledge.add(Implication(Not(rain), hagrid))
    knowledge.add(Or(hagrid, dumbledore))
    knowledge.add(
        And(
            Implication(hagrid, Not(dumbledore)),
            Implication(dumbledore, Not(hagrid)),
        )
    )
    knowledge.add(dumbledore)

    assert model_check(knowledge, hagrid) is False


def test_model_check_harry_puzzle_dumbledore_is_true():
    rain = Symbol("rain")
    hagrid = Symbol("hagrid")
    dumbledore = Symbol("dumbledore")

    knowledge = And()
    knowledge.add(Implication(Not(rain), hagrid))
    knowledge.add(Or(hagrid, dumbledore))
    knowledge.add(
        And(
            Implication(hagrid, Not(dumbledore)),
            Implication(dumbledore, Not(hagrid)),
        )
    )
    knowledge.add(dumbledore)

    assert model_check(knowledge, dumbledore) is True
