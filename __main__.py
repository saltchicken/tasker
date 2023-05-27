import sys
from tasker import Tasker

if __name__ == '__main__':
    print('Running Tasker')
    app = Tasker(sys.argv)
    sys.exit(app.exec_())