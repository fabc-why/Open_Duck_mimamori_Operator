try:
    from .operator_node import main
except ImportError:
    from operator_node import main


if __name__ == "__main__":
    main()