## Building

Execute the [build.sh](./build.sh) script:
```
$ bash build.sh
```
The above script (among other things) installs **conda**. You will have to scroll down the TOS, then type `yes` to agree to them and accept the default install directory. When asked if you wish the installer to initialize Miniconda3 by running conda init you can just press `ENTER` (default NO).

## Running

Execute the [solver.sh](./solver.sh). Usage:

```
$ ./solver.sh (-p | --problem) <task> (-f | --file) <file> (-fo | --format) <fileformat> [-a <additional_parameter>]
```

### Examples
```
./solver.sh -p CE-ST -f input/stable_easy_examples/stable_easy_example2.apx -fo apx
```
...returns the number of stable extensions of the framework [stable_easy_example2.apx](input/stable_easy_examples/stable_easy_example2.apx),

```
./solver.sh -p SE-ST -f input/stable_easy_examples/stable_easy_example2.apx -fo apx
```
...returns 1 stable extension,


```
./solver.sh -p DC-ST -f input/stable_easy_examples/stable_easy_example2.apx -fo apx -a 2
```
...checks whether argument `2` is credulously justified w.r.t. stable semantics.


### Other options:
To see the list of supported input formats, execute:
```
$ ./subsolver.py --formats
```

To view the help:
```
$ ./subsolver.py (-h | --help)
```

To view the supported problems list:
```
$ ./subsolver.py --problems
```
