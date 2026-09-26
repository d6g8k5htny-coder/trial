"""Focused experiment-harness controls. No solver or external files required."""
from fractions import Fraction as F
import unittest
import probe as p

class HarnessControls(unittest.TestCase):
    def test_duplicate_json(self):
        with self.assertRaises(p.Refusal): p.strict_json('{"a":1,"a":2}')
    def test_nonfinite_json(self):
        with self.assertRaises(p.Refusal): p.strict_json('{"a":NaN}')
    def test_command_injection(self):
        with self.assertRaises(p.Refusal): p.parse('(> a 0) (assert false)')
    def test_unclosed(self):
        with self.assertRaises(p.Refusal): p.parse('(> a 0')
    def test_unknown_symbol(self):
        with self.assertRaises(p.Refusal): p.validate_formula('(> hidden 0)',{'a'})
    def test_sort_error(self):
        with self.assertRaises(p.Refusal): p.validate_formula('(+ (> a 0) 1)',{'a'})
    def test_nonboolean_formula(self):
        with self.assertRaises(p.Refusal): p.validate_formula('(+ a 1)',{'a'})
    def test_wrong_arity(self):
        with self.assertRaises(p.Refusal): p.validate_formula('(< a)',{'a'})
    def test_zero_division(self):
        with self.assertRaises(p.Refusal): p.validate_formula('(> (/ 1 0) 1)',set())
    def test_variable_denominator(self):
        with self.assertRaises(p.Refusal): p.validate_formula('(> (/ 1 a) 1)',{'a'})
    def test_rational_denominator(self):
        self.assertTrue(p.exact(p.validate_formula('(= (/ 1 2) 0.5)',set()),{}))
    def test_exact_negative_rational(self):
        self.assertEqual(p.exact(p.parse('(- (/ 1 4))'),{}),F(-1,4))
    def test_unsat_premises_not_valid(self):
        self.assertEqual(p.classify('unsat','unsat'),'VACUOUS')
    def test_unknown_premises(self):
        self.assertEqual(p.classify('unknown','unsat'),'INCONCLUSIVE')
    def test_unknown_negation(self):
        self.assertEqual(p.classify('sat','unknown'),'INCONCLUSIVE')
    def test_satisfiable_counterexample(self):
        self.assertEqual(p.classify('sat','sat'),'COUNTEREXAMPLE')
    def test_nonvacuous_validity(self):
        self.assertEqual(p.classify('sat','unsat'),'VALID_ALGEBRA')
    def test_baseline_not_applicable_distinct_from_caught(self):
        c={'witness':{'x':'1'},'hypotheses':['(< x 0)'],'conclusion':'(< x 1)'}
        self.assertEqual(p.original_witness_baseline(c),'NOT_APPLICABLE')
    def test_rational_recurrence_counterexample(self):
        # Double-ratio mutation at p=5/8, m=3/10, n=1.
        v={'p':F(5,8),'m':F(3,10),'n':F(1)}
        self.assertTrue(p.exact(p.parse('(= (* (- 1 p) n) (* 2 p m))'),v))
        self.assertEqual((1-v['p'])**2*v['n']-v['p']**2*v['m'],F(3,128))
    def test_independent_recurrence_identity_grid(self):
        # A finite implementation control, not proof of the continuum result.
        for prob in (F(-1),F(0),F(1,2),F(3,4),F(2)):
            for mass in (F(-2),F(0),F(1,3)):
                n=prob*mass/(1-prob)
                self.assertEqual((1-prob)**2*n-prob**2*mass,prob*(1-2*prob)*mass)

if __name__=='__main__': unittest.main(verbosity=2)
