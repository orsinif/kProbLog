lexer grammar CommonIdentifiers;

PLUS: '+';
MINUS: '-';
TIMES: '*';
DIV: '/';
POW: '^';
//fragment MATH_OP : PLUS|MINUS|TIMES|DIV|POW;
fragment STRING_ID :  '\'' ( ~('\n'|'\r'|'\'') )*? '\'';

CONST_ID : [a-z] [a-zA-Z0-9_]* | STRING_ID;
VAR_ID : [A-Z] [a-zA-Z0-9_]*;
INT_ID
    : '0'
    | [1-9] [0-9]*;

FLOAT_ID : INT_ID '.' [0-9]*;

WS : [ \t\r\n]+ -> skip;


