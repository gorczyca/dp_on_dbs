%%%%%%%%%%%%%%%% guess S %%%%%%%%%%%%%%%%%%%%%%%%%%

in(X) :- arg(X), not out(X).
out(X) :- arg(X), not in(X).


%%%%%%%%%%%%%%%% conflict-free %%%%%%%%%%%%%%%%%%%%%%%%%%

% mutually attacking arguments are forbidden in a cf set
:- att(X,Y), att(Y,X), in(X), in(Y).

% cancelled attacks via d
cancel(X,Y) :- att(X,Y), in(Z), d(Z,X,Y).
:- in(X), in(Y), att(X,Y), not cancel(X,Y).

defeated(Z) :- in(Y), att(Y,Z), not cancel(Y,Z).
:- out(Z), not defeated(Z).

#show in/1.