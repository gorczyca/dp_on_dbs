%%%%%%%%%%%%%%%% auxiliary %%%%%%%%%%%%%%%%%%%%%%%%%%

% ordering
lt(X,Y) :- arg(X), arg(Y), X<Y.
nsucc(X,Z) :- lt(X,Y), lt(Y,Z).
succ(X,Y) :- lt(X,Y), not nsucc(X,Y).
ninf(Y) :- lt(X,Y).
inf(X) :- arg(X), not ninf(X).
nsup(X) :- lt(X,Y).
sup(X) :- arg(X), not nsup(X).

%%%%%%%%%%%%%%%% guess S %%%%%%%%%%%%%%%%%%%%%%%%%%

in(X) :- arg(X), not out(X).
out(X) :- arg(X), not in(X).

%%%%%%%%%%%%%%%% conflict-free %%%%%%%%%%%%%%%%%%%%%%%%%%

% mutually attacking arguments are forbidden in a cf set
:- att(X,Y), att(Y,X), in(X), in(Y).

% cancelled attacks via d
cancel(X,Y) :- att(X,Y), in(Z), d(Z,X,Y).
:- in(X), in(Y), att(X,Y), not cancel(X,Y).

succeed(X,Y) :- att(X,Y), not cancel(X,Y).

%%%%%%%%%%%%%%%% admissibility %%%%%%%%%%%%%%%%%%%%%%%%%%

% fixed point computation of RS[S] (= rs)

% initially add all attacks which are successfully attacked from S
rsinit(Y,Z) :- in(Y), succeed(Y,Z).

% removal candidates
todef(X,Y,Z) :- rsinit(Y,Z),d(X,Y,Z).

% remove attacks which are attacked by arguments not attacked by S
unattacked_upto(X,Y,Z,N) :- inf(N), todef(X,Y,Z), not rsinit(N,X).
unattacked_upto(X,Y,Z,N) :- inf(N), todef(X,Y,Z), remove(N,X).
unattacked_upto(X,Y,Z,N) :- succ(M,N), unattacked_upto(X,Y,Z,M), not rsinit(N,X).
unattacked_upto(X,Y,Z,N) :- succ(M,N), unattacked_upto(X,Y,Z,M), remove(N,X).
unattacked(X,Y,Z) :- sup(N), unattacked_upto(X,Y,Z,N).
remove(Y,Z) :- unattacked(X,Y,Z).

% arguments which are safely defeated by S
defeated(Y) :- rsinit(X,Y), not remove(X,Y).

%% The argument A is not defended by S
not_defended(A) :- arg(A), succeed(Z,A), not defeated(Z).

%% admissible
:- in(X), not_defended(X).

%% Every argument which is defended by S belongs to S
:- out(X), not not_defended(X).

#show in/1.