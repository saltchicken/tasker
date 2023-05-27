import sys
from tasker import Tasker


print('Running Tasker')
app = Tasker(sys.argv)
sys.exit(app.exec_())