def main():
    """Run application. Main entry point from command line."""
    import sys

    from virtual_warehouse import app

    sys.exit(app.run())


if __name__ == "__main__":
    main()
