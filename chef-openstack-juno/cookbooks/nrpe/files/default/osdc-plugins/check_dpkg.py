#!/usr/bin/env python3
import re
import subprocess
import sys

problems=[]

retcode,results=subprocess.getstatusoutput("sudo dpkg -V 2>/dev/null")
results=results.split("\n")

if not (retcode==0 or retcode==2):
    print("Error - command failed to even run")
    sys.exit(2)

for line in results:
  if line=="":
    continue
  m=re.match('([^ ]+) (.) ([^$]+)',line)
  path=m.group(3)

  if(m.group(1)[2]=='5'):
    md5error=True
  else:
    md5error=False

  if(m.group(2)=='c'):
    config=True
  else:
    config=False
  if(not(config and md5error)):
    problems.append(line)

if problems:
  print("WARNING - dpkg -V problems with: "+(", ".join(problems)))
  sys.exit(1)

print("OK - No issues with dpkg -V")
sys.exit(0)
