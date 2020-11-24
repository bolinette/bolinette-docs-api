import sys

if __name__ == '__main__':
    from bolinette_docs import bolinette
    bolinette.run_command(*sys.argv[1:])
