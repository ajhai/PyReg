PyReg
=====
Bare minimum regression script

How it works
============
Often we write test cases that tests the code we write. This python script leverages those tests and creates a regression suite on top of them. When run with required options, this script regresses each of the test cases in the test directory using the target binary, compares the output of the test cases with expected output. It fails the testcase when the output from the run differs from the expected output.

For example, assume we have test cases test1.rb and test2.rb in testDir. In order to run the regression script over these two test cases, we do 

>python pyreg.py -m path_to_mapfile -b /usr/bin/ruby -e rb testDir

In the first run, it will report all the test cases as failed. We need to inspect and accept the output of each of the test case in the first run. Like
>python pyreg.py -m path_to_mapfile -b /usr/bin/ruby -e rb -a true test1
>python pyreg.py -m path_to_mapfile -b /usr/bin/ruby -e rb -a true test2

From next run on we can simply do 
>python pyreg.py -m path_to_mapfile -b /usr/bin/ruby -e rb testDir
to run regression on the list cases. We can run individual testcases by providing the testcase name without file extension.


Usage
=====
>python pyreg.py -m &lt;variable_map_file&gt; -b &lt;path_to_binary&gt; -e &lt;file_extension&gt; &lt;testcase_name or path_to_dir&gt;


_variable_map_file:_ Variable map file contains space separated key value pair per line which will be used when running the test cases. Any key between <% and %> will be replaced with the value from map file.

_Example map file:_

-----------------
key1 value1<br/>
key2 value2<br/>
key3 value3<br/>

-----------------

and <%key1%> will be replaced with value1 in the test <br/>


_path_to_binary:_ Absolute path to the binary file using which the tests are to be run<br/>
_file_extension:_ File extension for the test case files<br/>
_testcase_name:_ Test case name without file extension or path to directory containing test cases
_
