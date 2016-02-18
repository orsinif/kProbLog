grammar GKProlog;
import CommonIdentifiers;

Comment:  '%' ~( '\r' | '\n' )*;

constant
    : CONST_ID #Const
    | INT_ID #Int
    | FLOAT_ID #Float
    ;

term
    : constant #ConstTerm
        | CONST_ID '(' term_list ')' #FuncTerm
    ;

term_list
    : term #TermInList
    | term ',' term_list #TermList
    ;

algebraic_weight
    : multiplyingExpression (PLUS multiplyingExpression)*
    ;

multiplyingExpression
    : powExpression (TIMES powExpression)*
    ;

powExpression
    : term (POW term)? #powExpression_term
    | '@' constant '['algebraic_weight (',' algebraic_weight)* ']' #powExpression_metafunction
    ;

atom
    : constant #AtomZero
    | constant '(' term_list ')' #AtomNonZero
    ;

atom_list
    : atom #AtomInList
    | atom ',' atom_list #AtomList
    ;

body_atom
    : atom #SimpleBodyAtom
    | '@' constant '[' body_atom_list ']' #DecoratedBodyAtom
    ;

body_atom_list
    : body_atom #BodyAtomInList
    | body_atom ',' body_atom_list #BodyAtomList
    ;

semiring_type: term;

clause
    : atom ':-' body_atom_list '.' #Rule
    | atom '.' #Fact
    | algebraic_weight '::' atom ':-' body_atom_list '.' #WeightedRule
    | algebraic_weight '::' atom '.' #WeightedFact
    | ':-' 'declare' '(' predicate_name '/' INT_ID ',' semiring_type ')' '.' #Declaration
    | ':-' 'declare' '(' predicate_name '/' INT_ID ',' semiring_type ',' UPDATE_TYPE ')' '.' #DeclarationCycle
    | ':-' 'query' '(' atom_list ')' '.' #QueryAtoms
    ;

predicate_name : constant;
UPDATE_TYPE
    : 'additive'
    | 'destructive'
    ;

program0: (clause|Comment)*;

program : program0 EOF;
