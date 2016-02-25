
import pydre.project
import os.path
import glob

p = pydre.project.Project("docs/example_projectfile.json")

# put some data files in tests/testdata/ to test it out
filelist = glob.glob(os.path.join(os.path.dirname(__file__), 'testdata/*.dat'))

p.run(filelist)