# A-Folio DPDB v0.1

Johannes Fichte (johannes.fichte@tu-dresden.de),  
Markus Hecher (markus.hecher@tuwien.ac.at),  
Piotr Gorczyca (gorczycapj@gmail.com),  
Ridhwan Dewoprabowo (ridhwan.dewoprabowo@gmail.com).

___  

A-Folio supports Static Abstract Argumentation track, specifically its **stable** and **complete** subtracks, i.e. the tasks:
- CE-ST, SE-ST, DC-ST, DS-ST,
- CE-CO, SE-CO, DC-CO, DS-CO.
  
# Building

Execute the [build.sh](./build.sh) script:
```
user$ bash build.sh
```

The above script installs **Miniconda** and creates a necessary environment.  
You will have to scroll down the TOS, then type `yes` to agree to them and accept the default install directory. When asked if you wish the installer to initialize Miniconda3 by running conda init you can just press `ENTER` (default is `[NO]`).

# Running

Running works precisely as required in the [solver requirements](http://argumentationcompetition.org/2021/SolverRequirements.pdf) 

Execute the [solver.sh](./solver.sh). Usage:

```
user$ ./solver.sh -p <task> -f <file> -fo  <fileformat> [-a <additional_parameter>]
```

## Examples
- Return the number of stable extensions of the framework [easy2.apx](input/easy2.apx):
    ```
    user$ ./solver.sh -p CE-ST -f input/easy2.apx -fo apx
    ```

- Return 1 stable extension:
    ```
    user$ ./solver.sh -p SE-ST -f input/easy2.apx -fo apx
    ```

- Check whether argument `2` is credulously justified w.r.t. stable semantics. 
    ```
    user$ ./solver.sh -p DC-ST -f input/easy2.apx -fo apx -a 2
    ```


## Other options:
  

- Show help:
    ```
    user$ ./solver.sh (-h | --help)
    ```

- Show the list of supported input formats:
    ```
    user$ ./solver.sh --formats
    ```

- Show the supported problems list:
    ```
    user$ ./solver.sh --problems
    ```
