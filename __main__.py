import sys
from tasker import Tasker

app = Tasker(sys.argv)
sys.exit(app.exec_())