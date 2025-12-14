import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gui.main_window import MainWindow

def main():
    """Main function"""
    print("\n" + "=" * 70)
    print(" INTELLIGENT CUBIC PLAYER ".center(70))
    print(" 4x4x4 Tic-Tac-Toe with Minimax & Alpha-Beta Pruning ".center(70))
    print("=" * 70)
    print("\nInitializing game...")

    app = MainWindow()

    print("Game window loaded successfully!")
    print("=" * 70 + "\n")

    app.run()

    print("\nThank you for playing!")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()