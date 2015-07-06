#coding=utf-8
#!/usr/bin/python

import os
import shutil
import compileall 

import Net


#print os.path.dirname(__file__)
#if(os.getcwd() != os.path.dirname(__file__)):
#	os.chdir(os.path.dirname(__file__))
#print os.getcwd()

#compileall.compile_dir(os.path.dirname(__file__))

Net.main("..\..\..\Doc\in","..\..\Assets\Scripts\Network\Dispatcher")