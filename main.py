import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from langchain_customer_service_robot.cli.main import main

if __name__ == '__main__':
    main()
